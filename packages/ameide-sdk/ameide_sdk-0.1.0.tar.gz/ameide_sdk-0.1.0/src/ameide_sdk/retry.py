from __future__ import annotations

import random
import time
from typing import Any, Iterable, Optional, Tuple

import grpc

from .config import RetryConfig


def wrap_stub_with_retry(stub: Any, cfg: RetryConfig):
    """Wraps UnaryUnary RPC callables with retry semantics."""
    if cfg.max_attempts <= 1:
        return stub
    return _RetryingStub(stub, cfg)


class _RetryingStub:
    def __init__(self, target: Any, cfg: RetryConfig) -> None:
        self._target = target
        self._cfg = cfg
        self._retryable = {getattr(grpc.StatusCode, code) for code in cfg.retryable_codes}

    def __getattr__(self, name: str):
        attr = getattr(self._target, name)
        if isinstance(attr, grpc.UnaryUnaryMultiCallable):
            return _RetryingUnaryUnary(attr, self._cfg, self._retryable)
        return attr


class _RetryingUnaryUnary(grpc.UnaryUnaryMultiCallable):
    def __init__(self, inner: grpc.UnaryUnaryMultiCallable, cfg: RetryConfig, retryable: set[grpc.StatusCode]) -> None:
        self._inner = inner
        self._cfg = cfg
        self._retryable = retryable

    def _invoke(self, method_name: str, request, *args, **kwargs):
        delay = self._cfg.initial_backoff
        attempts = 0
        while attempts < self._cfg.max_attempts:
            attempts += 1
            call = getattr(self._inner, method_name)
            try:
                return call(request, *args, **kwargs)
            except grpc.RpcError as exc:
                if exc.code() not in self._retryable or attempts >= self._cfg.max_attempts:
                    raise
                sleep = min(delay * random.uniform(0.5, 1.5), self._cfg.max_backoff)
                time.sleep(sleep)
                delay = min(delay * self._cfg.backoff_multiplier, self._cfg.max_backoff)

    def __call__(
        self,
        request,
        timeout: Optional[float] = None,
        metadata: Optional[Iterable[Tuple[str, str]]] = None,
        credentials: Optional[grpc.CallCredentials] = None,
        wait_for_ready: Optional[bool] = None,
        compression: Optional[grpc.Compression] = None,
    ):
        return self._invoke(
            "__call__",
            request,
            timeout=timeout,
            metadata=metadata,
            credentials=credentials,
            wait_for_ready=wait_for_ready,
            compression=compression,
        )

    def with_call(
        self,
        request,
        timeout: Optional[float] = None,
        metadata: Optional[Iterable[Tuple[str, str]]] = None,
        credentials: Optional[grpc.CallCredentials] = None,
        wait_for_ready: Optional[bool] = None,
        compression: Optional[grpc.Compression] = None,
    ):
        return self._invoke(
            "with_call",
            request,
            timeout=timeout,
            metadata=metadata,
            credentials=credentials,
            wait_for_ready=wait_for_ready,
            compression=compression,
        )

    def future(
        self,
        request,
        timeout: Optional[float] = None,
        metadata: Optional[Iterable[Tuple[str, str]]] = None,
        credentials: Optional[grpc.CallCredentials] = None,
        wait_for_ready: Optional[bool] = None,
        compression: Optional[grpc.Compression] = None,
    ):
        return self._invoke(
            "future",
            request,
            timeout=timeout,
            metadata=metadata,
            credentials=credentials,
            wait_for_ready=wait_for_ready,
            compression=compression,
        )
