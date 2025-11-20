from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, AsyncIterator, AsyncGenerator

import grpc
from grpc import StatusCode
from grpc.aio import Channel, insecure_channel, secure_channel, AioRpcError

from etcd.api.etcdserverpb import rpc_pb2, rpc_pb2_grpc


@dataclass
class EtcdConfig:
    endpoint: str  # "etcd-stest.cag.wargaming.net:443" or "etcd-server:2379"
    username: str
    password: str
    ca_cert_path: Optional[Path] = None
    insecure: bool = False  # True -> plaintext (no TLS)


class EtcdAsyncClient:
    """
    Async etcd v3 client using grpc.aio:

      - async authentication (username/password -> token)
      - async put/get
      - async prefix watcher
      - auto re-auth & retry on auth failures (once per call)
    """

    def __init__(self, config: EtcdConfig, auth_timeout: float = 5.0):
        self._config = config
        self._auth_timeout = auth_timeout

        self._channel: Optional[Channel] = None
        self._token: Optional[str] = None

        self._kv: Optional[rpc_pb2_grpc.KVStub] = None
        self._watch: Optional[rpc_pb2_grpc.WatchStub] = None
        self._auth: Optional[rpc_pb2_grpc.AuthStub] = None

    # ---------- async context manager ----------

    async def __aenter__(self) -> "EtcdAsyncClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    # ---------- connection / auth ----------

    async def connect(self) -> None:
        if self._config.insecure:
            self._channel = insecure_channel(self._config.endpoint)
        else:
            if self._config.ca_cert_path is not None:
                root_certs = self._config.ca_cert_path.read_bytes()
                creds = grpc.ssl_channel_credentials(root_certificates=root_certs)
            else:
                creds = grpc.ssl_channel_credentials()
            self._channel = secure_channel(self._config.endpoint, creds)

        # async stubs share the aio channel
        self._kv = rpc_pb2_grpc.KVStub(self._channel)
        self._watch = rpc_pb2_grpc.WatchStub(self._channel)
        self._auth = rpc_pb2_grpc.AuthStub(self._channel)

        await self._authenticate()

    async def _authenticate(self) -> None:
        assert self._auth is not None
        req = rpc_pb2.AuthenticateRequest(
            name=self._config.username,
            password=self._config.password,
        )
        resp = await self._auth.Authenticate(req, timeout=self._auth_timeout)
        self._token = resp.token

    def _metadata(self):
        assert self._token is not None
        return (("token", self._token),)

    async def close(self) -> None:
        if self._channel is not None:
            await self._channel.close()
            self._channel = None

    # ---------- auth-aware call wrapper ----------

    async def _call_with_auth_retry(self, coro_factory):
        """
        Run an RPC coroutine; on UNAUTHENTICATED / PERMISSION_DENIED
        re-authenticate once and retry.
        """
        try:
            return await coro_factory()
        except AioRpcError as e:
            if e.code() in (StatusCode.UNAUTHENTICATED, StatusCode.PERMISSION_DENIED):
                # token likely expired / revoked -> refresh once
                await self._authenticate()
                return await coro_factory()
            raise

    # ---------- KV API ----------

    async def put(
        self, key: str, value: str, timeout: float = 5.0
    ) -> rpc_pb2.PutResponse:
        assert self._kv is not None

        req = rpc_pb2.PutRequest(
            key=key.encode("utf-8"),
            value=value.encode("utf-8"),
        )

        async def do_call():
            return await self._kv.Put(req, timeout=timeout, metadata=self._metadata())

        return await self._call_with_auth_retry(do_call)

    async def get(self, key: str, timeout: float = 5.0) -> Optional[str]:
        assert self._kv is not None

        req = rpc_pb2.RangeRequest(
            key=key.encode("utf-8"),
            limit=1,
        )

        async def do_call():
            return await self._kv.Range(req, timeout=timeout, metadata=self._metadata())

        resp: rpc_pb2.RangeResponse = await self._call_with_auth_retry(do_call)
        if not resp.kvs:
            return None
        return resp.kvs[0].value.decode("utf-8")

    async def get_prefix(
        self, prefix: str, timeout: float = 5.0
    ) -> rpc_pb2.RangeResponse:
        """
        Fetch all keys under a given prefix using a Range request.
        Returns the raw RangeResponse from etcd (with .kvs list).
        """
        assert self._kv is not None

        key = prefix.encode("utf-8")
        range_end = _prefix_range_end(key)

        req = rpc_pb2.RangeRequest(
            key=key,
            range_end=range_end,
        )

        async def do_call():
            return await self._kv.Range(req, timeout=timeout, metadata=self._metadata())

        return await self._call_with_auth_retry(do_call)

    # ---------- watch API (async) ----------

    async def watch_prefix(
        self,
        prefix: str,
        start_revision: int = 0,
    ) -> AsyncIterator[rpc_pb2.Event]:
        """
        Async generator yielding events for all keys under `prefix`.

        Usage:

            async for ev in client.watch_prefix("/demo/"):
                print(ev.type, ev.kv.key, ev.kv.value)
        """
        assert self._watch is not None

        key = prefix.encode("utf-8")
        range_end = _prefix_range_end(key)

        create_req = rpc_pb2.WatchCreateRequest(
            key=key,
            range_end=range_end,
            start_revision=start_revision or 0,
        )

        async def request_iter() -> AsyncGenerator[rpc_pb2.WatchRequest, None]:
            # single create_request then keep stream open
            yield rpc_pb2.WatchRequest(create_request=create_req)

        async def do_stream():
            return self._watch.Watch(request_iter(), metadata=self._metadata())

        # We want auth retry on opening the stream (create_watch).
        # Once the stream is established, we'll treat auth failures as fatal.
        responses = await self._call_with_auth_retry(do_stream)

        async for resp in responses:
            for ev in resp.events:
                yield ev


def _prefix_range_end(prefix: bytes) -> bytes:
    if not prefix:
        return b"\0"
    ba = bytearray(prefix)
    ba[-1] = (ba[-1] + 1) % 256
    return bytes(ba)
