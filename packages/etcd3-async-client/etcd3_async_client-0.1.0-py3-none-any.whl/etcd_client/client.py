from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

import grpc

from etcd.api.etcdserverpb import rpc_pb2, rpc_pb2_grpc


@dataclass
class EtcdConfig:
    endpoint: str  # e.g. "etcd-stest.cag.wargaming.net:443" or "etcd-server:2379"
    username: str  # etcd user
    password: str  # etcd password
    ca_cert_path: Optional[Path] = None  # for TLS; None = use system CAs
    insecure: bool = False  # True -> grpc.insecure_channel (no TLS)


class EtcdClient:
    """
    Small reusable etcd v3 client (gRPC-based) with:
      - TLS / non-TLS support
      - username/password auth (via Auth.Authenticate)
      - get / put helpers
      - a prefix watcher
    """

    def __init__(self, config: EtcdConfig, auth_timeout: float = 5.0):
        self._config = config
        self._channel = self._create_channel()
        self._token = self._authenticate(timeout=auth_timeout)

        # Stubs reuse the same channel
        self._kv = rpc_pb2_grpc.KVStub(self._channel)
        self._watch = rpc_pb2_grpc.WatchStub(self._channel)

    # ---------- internal helpers ----------

    def _create_channel(self) -> grpc.Channel:
        if self._config.insecure:
            # Plaintext (for http://etcd-server:2379 style)
            return grpc.insecure_channel(self._config.endpoint)

        # TLS
        if self._config.ca_cert_path is not None:
            root_certs = self._config.ca_cert_path.read_bytes()
            creds = grpc.ssl_channel_credentials(root_certificates=root_certs)
        else:
            # System trust store
            creds = grpc.ssl_channel_credentials()

        return grpc.secure_channel(self._config.endpoint, creds)

    def _authenticate(self, timeout: float) -> str:
        """
        Use etcd's Auth.Authenticate RPC to obtain a token for username/password.
        """
        auth_stub = rpc_pb2_grpc.AuthStub(self._channel)
        req = rpc_pb2.AuthenticateRequest(
            name=self._config.username,
            password=self._config.password,
        )
        resp = auth_stub.Authenticate(req, timeout=timeout)
        return resp.token

    def _metadata(self):
        return (("token", self._token),)

    # ---------- public KV API ----------

    def put(self, key: str, value: str, timeout: float = 5.0) -> rpc_pb2.PutResponse:
        """
        Put a UTF-8 string value under a UTF-8 key.
        """
        req = rpc_pb2.PutRequest(
            key=key.encode("utf-8"),
            value=value.encode("utf-8"),
        )
        return self._kv.Put(req, timeout=timeout, metadata=self._metadata())

    def get(self, key: str, timeout: float = 5.0) -> Optional[str]:
        """
        Get a single key, returning its value as a UTF-8 string or None if missing.
        """
        req = rpc_pb2.RangeRequest(
            key=key.encode("utf-8"),
            limit=1,
        )
        resp = self._kv.Range(req, timeout=timeout, metadata=self._metadata())
        if not resp.kvs:
            return None
        return resp.kvs[0].value.decode("utf-8")

    # ---------- watch API ----------

    def watch_prefix(
        self,
        prefix: str,
        start_revision: int = 0,
    ) -> Iterator[rpc_pb2.Event]:
        """
        Watch all changes under a key prefix.

        This is a generator: it yields rpc_pb2.Event objects:
          - event.type
          - event.kv.key
          - event.kv.value

        Usage:
            for event in client.watch_prefix("/demo/"):
                ...
        """
        key = prefix.encode("utf-8")
        range_end = _prefix_range_end(key)

        create_req = rpc_pb2.WatchCreateRequest(
            key=key,
            range_end=range_end,
            start_revision=start_revision or 0,
        )

        def req_iter():
            # First request: create the watch
            yield rpc_pb2.WatchRequest(create_request=create_req)
            # No further requests; server will now stream responses

        # Streaming RPC
        responses = self._watch.Watch(req_iter(), metadata=self._metadata())
        for resp in responses:
            for ev in resp.events:
                yield ev

    # ---------- lifecycle ----------

    def close(self) -> None:
        self._channel.close()

    def __enter__(self) -> "EtcdClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def _prefix_range_end(prefix: bytes) -> bytes:
    """
    Compute the range_end for an etcd prefix scan/watch.

    etcd convention:
      - For a prefix 'foo', range_end is 'fop' (last byte + 1).
      - That gives you all keys k where prefix <= k < range_end.
    """
    if not prefix:
        # empty prefix -> watch whole keyspace
        return b"\0"
    ba = bytearray(prefix)
    ba[-1] = (ba[-1] + 1) % 256
    return bytes(ba)
