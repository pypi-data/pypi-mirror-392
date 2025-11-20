from __future__ import annotations

import uuid
from typing import Callable, Iterable, Optional, Sequence, Tuple

import grpc

from .config import SDKOptions

MetadataSequence = Optional[Sequence[Tuple[str, str]]]


class _ClientCallDetails(grpc.ClientCallDetails):
    def __init__(
        self,
        method: str,
        timeout: Optional[float],
        metadata: MetadataSequence,
        credentials,
        wait_for_ready: Optional[bool],
        compression,
    ):
        self.method = method
        self.timeout = timeout
        self.metadata = metadata
        self.credentials = credentials
        self.wait_for_ready = wait_for_ready
        self.compression = compression


def _append_metadata(existing: MetadataSequence, additions: Iterable[Tuple[str, str]]) -> Sequence[Tuple[str, str]]:
    merged = []
    if existing:
        merged.extend(existing)
    merged.extend(additions)
    return merged


def _has_header(metadata: MetadataSequence, key: str) -> bool:
    if not metadata:
        return False
    key_lower = key.lower()
    return any(existing_key.lower() == key_lower for existing_key, _ in metadata)


class MetadataInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, options: SDKOptions):
        self._options = options
        self._request_id_provider = options.request_id_provider or (lambda: str(uuid.uuid4()))

    def intercept_unary_unary(self, continuation, client_call_details, request):
        additions = []
        if self._options.tenant_id:
            additions.append(("tenant-id", self._options.tenant_id))
        if self._options.user_id:
            additions.append(("user-id", self._options.user_id))
        for key, value in self._options.metadata.items():
            additions.append((key.lower(), value))
        if not _has_header(client_call_details.metadata, "x-request-id"):
            additions.append(("x-request-id", self._request_id_provider()))

        details = _ClientCallDetails(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            metadata=_append_metadata(client_call_details.metadata, additions),
            credentials=client_call_details.credentials,
            wait_for_ready=getattr(client_call_details, "wait_for_ready", None),
            compression=getattr(client_call_details, "compression", None),
        )
        return continuation(details, request)


class AuthInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, token_provider: Callable[[], Optional[str]]):
        self._token_provider = token_provider

    def intercept_unary_unary(self, continuation, client_call_details, request):
        token = self._token_provider()
        additions = [("authorization", f"Bearer {token}")] if token else []
        details = _ClientCallDetails(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            metadata=_append_metadata(client_call_details.metadata, additions),
            credentials=client_call_details.credentials,
            wait_for_ready=getattr(client_call_details, "wait_for_ready", None),
            compression=getattr(client_call_details, "compression", None),
        )
        return continuation(details, request)


class TimeoutInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, timeout: Optional[float]):
        self._timeout = timeout

    def intercept_unary_unary(self, continuation, client_call_details, request):
        if self._timeout is None or self._timeout <= 0:
            return continuation(client_call_details, request)

        current_timeout = client_call_details.timeout
        effective_timeout = self._timeout if not current_timeout else min(current_timeout, self._timeout)

        details = _ClientCallDetails(
            method=client_call_details.method,
            timeout=effective_timeout,
            metadata=client_call_details.metadata,
            credentials=client_call_details.credentials,
            wait_for_ready=getattr(client_call_details, "wait_for_ready", None),
            compression=getattr(client_call_details, "compression", None),
        )
        return continuation(details, request)


def metadata_interceptor(options: SDKOptions) -> grpc.UnaryUnaryClientInterceptor:
    return MetadataInterceptor(options)


def auth_interceptor(provider: Optional[Callable[[], Optional[str]]]) -> Optional[grpc.UnaryUnaryClientInterceptor]:
    if provider is None:
        return None
    return AuthInterceptor(provider)


def timeout_interceptor(timeout: Optional[float]) -> Optional[grpc.UnaryUnaryClientInterceptor]:
    if timeout is None or timeout <= 0:
        return None
    return TimeoutInterceptor(timeout)
