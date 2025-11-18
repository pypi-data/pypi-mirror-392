import asyncio
import json
import logging
import time
import os
import ssl
import signal
from contextlib import asynccontextmanager

import certifi
from typing import Optional, AsyncGenerator, Sequence
from dataclasses import dataclass
from hashlib import sha256

import electrum_aionostr as aionostr
from electrum_aionostr.event import Event as NostrEvent
from electrum_aionostr.key import PrivateKey


@dataclass(kw_only=True, frozen=True)
class NIP89Info:
    """
    This is how content could look like (copied from nostr-dvm):
        content = {
        "name": name,
        "picture": image,
        "about": description,
        "lud16": dvm_config.LN_ADDRESS,
        "supportsEncryption": True,
        "acceptsNutZaps": False,
        "personalized": False,
        "amount": create_amount_tag(cost),
        "nip90Params": {
            "max_results": {
                "required": False,
                "values": [],
                "description": "The number of maximum results to return (default currently 100)"
            }
        }
    }
    """
    content: dict
    extra_tags: Optional[list[list]] = None
    announcement_event_kind: int = 31990

    def __post_init__(self):
        json.dumps(self.content)  # test if valid json

    def to_event(
            self,
            service_event_kind: int,
            pubkey_hex: str,
            expiry_ts: Optional[int] = None
    ) -> NostrEvent:
        d_tag = [
            'd',
            sha256(f"{service_event_kind}{pubkey_hex}".encode('utf-8')).hexdigest()[:16],
        ]
        k_tag = ['k', str(service_event_kind)]
        tags = [d_tag, k_tag]
        if self.extra_tags:
            tags.extend(self.extra_tags)
        event = NostrEvent(
            pubkey=pubkey_hex,
            content=json.dumps(self.content),
            tags=tags,
            kind=self.announcement_event_kind,
            expiration_ts=expiry_ts,
        )
        return event


class AIONostrDVM:
    """
    Basic framework to implement NIP-89/90 Data Vending Machines with electrum-aionostr.
    The "specification" is a mess, at this time there are 3 different NIP-90 specifications?
    https://github.com/nostr-protocol/nips/blob/master/90.md
    https://github.com/nostr-protocol/nips/blob/master/89.md
    https://github.com/nostr-protocol/nips/pull/1942
    https://github.com/nostr-protocol/nips/pull/1903
    https://github.com/nostr-protocol/nips/pull/1728
    This is tested against the Amethyst and Primal.
    """
    CONNECTION_TIMEOUT_SEC = 30  # this is a server application so we're not in a hurry
    ANNOUNCEMENT_INTERVAL_SEC = 1800

    def __init__(
            self, *,
            dvm_name: str,
            # here is a list of taken kinds: https://github.com/believethehype/nostrdvm/tree/main/nostr_dvm/tasks
            service_event_kind: int,
            relays: Sequence[str],
            private_key_hex: Optional[str] = None,  # not passing private key will use random one
            announcement_interval_sec: int = 3600,
    ):
        self.logger = logging.getLogger(dvm_name)
        self.dvm_name = dvm_name
        self.service_event_kind = service_event_kind
        self._private_key = PrivateKey(bytes.fromhex(private_key_hex) if private_key_hex else os.urandom(32))
        self.pubkey = self._private_key.public_key.hex()
        self.relays = set(normalize_websocket_urls(relays))
        self.announcement_interval_sec = announcement_interval_sec
        self.taskgroup = None  # type: Optional[asyncio.TaskGroup]
        self._main_task = None  # type: Optional[asyncio.Task]
        self._relay_manager = None  # type: Optional[aionostr.Manager]
        self._initialized = asyncio.Event()

    async def __aenter__(self) -> 'AIONostrDVM':
        self._main_task = asyncio.create_task(self.main_loop())
        self._main_task.add_done_callback(self._on_main_task_done)
        await asyncio.wait_for(self._initialized.wait(), timeout=self.CONNECTION_TIMEOUT_SEC + 5)
        assert isinstance(self._relay_manager, aionostr.Manager)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            await asyncio.wait_for(self.stop(), timeout=10)
        except asyncio.TimeoutError:
            return

    def _on_main_task_done(self, task: asyncio.Task) -> None:
        if task.cancelled():
            return
        exc = task.exception()
        if exc is not None:
            # rip down the whole thing if the main loop crashed
            self.logger.exception("main task crashed", exc_info=exc)
            try:
                os.kill(os.getpid(), signal.SIGTERM)
            except Exception:
                self.logger.exception("failed to send SIGTERM after crash")

    async def main_loop(self) -> None:
        async with self._start_relay_manager() as _manager:
            self.logger.debug(f"starting AIONostrDVM taskgroup")
            try:
                async with asyncio.TaskGroup() as tg:
                    self.taskgroup = tg
                    tg.create_task(self._subscribe_to_requests())
                    tg.create_task(self._broadcast_nip89_announcement_event())
                    self._initialized.set()
                    await asyncio.sleep(10)
                    tg.create_task(self._broadcast_nip65_relay_announcement_event())
            except* ValueError as eg:
                # re-raise the first exception happening in the taskgroup
                self.logger.exception("Task group failed")
                raise eg.exceptions[0]
            finally:
                self.taskgroup = None
                self.logger.debug(f"taskgroup stopped")

    @asynccontextmanager
    async def _start_relay_manager(self) -> AsyncGenerator[aionostr.Manager, None]:
        ca_path = certifi.where()
        ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=ca_path)
        self.logger.info(f"connecting to nostr relays")
        manager_logger = logging.getLogger('dvm-relay-manager')
        manager_logger.setLevel('INFO')
        try:
            async with aionostr.Manager(
                relays=self.relays,
                private_key=self._private_key.hex(),
                ssl_context=ssl_context,
                connect_timeout=self.CONNECTION_TIMEOUT_SEC,
                log=manager_logger,
            ) as relay_manager:
                self._relay_manager = relay_manager
                yield relay_manager
        except Exception:
            self.logger.exception(f"relay manager crashed")
            raise
        finally:
            self._relay_manager = None
            self.logger.debug(f"relay manager closed")

    async def stop(self) -> None:
        if self._main_task:
            self._main_task.cancel()
        while self._relay_manager is not None:
            self.logger.debug(f"waiting for relay manager disconnect")
            await asyncio.sleep(2)

    async def subscribe_to_filter(self, query: dict) -> AsyncGenerator[NostrEvent, None]:
        assert self._relay_manager is not None and self._relay_manager.connected
        async for event in self._relay_manager.get_events(query, single_event=False, only_stored=False):
            try:
                if event.content:
                    # validate json
                    content = json.loads(event.content)
                    if not isinstance(content, dict):
                        raise Exception("malformed content, not dict")
            except Exception as e:
                self.logger.debug(f"failed to parse event: {e}")
                continue
            yield event
            await asyncio.sleep(0)

    async def _subscribe_to_requests(self):
        """Subscribes to user requests and calls handle_request() with incoming requests"""
        query = {
            "kinds": [self.service_event_kind],
            "limit": 0,
            "#p": [self.pubkey],
        }
        async for event in self.subscribe_to_filter(query):
            if (event.created_at > int(time.time()) + 60 * 60
                     or event.created_at < int(time.time()) - 60 * 60):
                 continue
            asyncio.create_task(self._handle_request_and_send_response(event))

    async def _broadcast_nip89_announcement_event(self):
        """Regularly broadcasts nip89 announcement event for discoverability of the dvm"""
        await asyncio.sleep(5)  # wait some time after startup
        while True:
            nip89_info = await self.get_announcement_info()
            if not nip89_info:
                await asyncio.sleep(10)
                continue
            event = nip89_info.to_event(
                service_event_kind=self.service_event_kind,
                pubkey_hex=self._private_key.public_key.hex(),
                expiry_ts=int(time.time()) + self.ANNOUNCEMENT_INTERVAL_SEC,
            )
            assert isinstance(event, NostrEvent), event
            event.sign(self._private_key.hex())
            try:
                result = await self._relay_manager.add_event(event)
                self.logger.debug(f"nip89 announcement event broadcasted: {result}")
            except asyncio.TimeoutError:
                self.logger.warning(f"failed to broadcast nip89 announcement event")
            await asyncio.sleep(self.ANNOUNCEMENT_INTERVAL_SEC)

    async def _handle_request_and_send_response(self, request: NostrEvent):
        response = await self.handle_request(request)
        if not isinstance(response, NostrEvent):
            return
        if not response.sig:
            response.sign(self._private_key.hex())
        # get the relays the client included in their request that we are not connected to
        their_relays = get_relays_in_event_tag(request)
        new_relays = list(their_relays - self.relays)[:5] if their_relays else None
        try:
            # send to our relays
            await self._relay_manager.add_event(response)
            # connect to clients relays and send response to them as well
            if new_relays:
                self.logger.debug(f"connecting to their relays: {new_relays=}")
                await aionostr.add_event(
                    relays=new_relays,
                    event=response.to_json_object(),
                    private_key=self._private_key.hex(),
                )
            self.logger.debug(f"sent response {response.id} to request {request.id}")
        except asyncio.TimeoutError:
            self.logger.warning(f"sending response event timed out")
        except Exception:
            self.logger.exception(f"failed to send response event: {response.id}")

    async def _broadcast_nip65_relay_announcement_event(self):
        """This allows other clients to know which relays we are using (NIP-65)"""
        tags = [['r', relay_url] for relay_url in self.relays]
        nip65_event = NostrEvent(
            kind=10002,
            content='',
            tags=tags,
            expiration_ts=int(time.time()) + 1209600,  # 2 weeks
            pubkey=self.pubkey,
        )
        nip65_event.sign(self._private_key.hex())
        try:
            await self._relay_manager.add_event(nip65_event)
            self.logger.debug(f"broadcasted nip65 relay announcement")
        except Exception:
            self.logger.error(f"failed to broadcast nip65 relay list")

    async def handle_request(self, request: NostrEvent) -> Optional[NostrEvent]:
        # to be implemented by child, if response is returned it will be broadcast
        raise NotImplementedError()

    async def get_announcement_info(self) -> Optional[NIP89Info]:
        # to be implemented by child, NIP89
        raise NotImplementedError()


def normalize_websocket_urls(urls: Sequence[str]) -> list[str]:
    normalized = []
    for url in urls:
        url = url.strip().lower()
        if not url.startswith(('ws://', 'wss://')):
            url = 'wss://' + url
        if url.endswith('/'):
            url = url[:-1]
        normalized.append(url)
    return normalized


def get_relays_in_event_tag(event: NostrEvent) -> Optional[set[str]]:
    """Returns the relays contained in the given events tags"""
    try:
        relays_tag: list[str] = next(iter(tag for tag in event.tags if tag[0] == 'relays'))
    except StopIteration:
        return None
    if len(relays_tag) > 1:
        return set(normalize_websocket_urls(relays_tag[1:]))
    return None
