from __future__ import annotations

from dataclasses import dataclass

import grpc


class RpcErrorCategory:
    AUTH = "auth"
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    RATE_LIMIT = "rate_limit"
    SERVICE = "service"
    UNKNOWN = "unknown"


RETRYABLE_CODES = {
    grpc.StatusCode.UNAVAILABLE,
    grpc.StatusCode.DEADLINE_EXCEEDED,
    grpc.StatusCode.RESOURCE_EXHAUSTED,
    grpc.StatusCode.ABORTED,
    grpc.StatusCode.INTERNAL,
}


@dataclass
class AmeideRpcError(Exception):
    message: str
    code: grpc.StatusCode
    category: str
    retryable: bool

    def __str__(self) -> str:
        return f"{self.code.name}: {self.message}"


def _categorize(code: grpc.StatusCode) -> str:
    if code in (grpc.StatusCode.UNAUTHENTICATED, grpc.StatusCode.PERMISSION_DENIED):
        return RpcErrorCategory.AUTH
    if code in (
        grpc.StatusCode.INVALID_ARGUMENT,
        grpc.StatusCode.FAILED_PRECONDITION,
        grpc.StatusCode.OUT_OF_RANGE,
        grpc.StatusCode.ALREADY_EXISTS,
    ):
        return RpcErrorCategory.VALIDATION
    if code == grpc.StatusCode.NOT_FOUND:
        return RpcErrorCategory.NOT_FOUND
    if code == grpc.StatusCode.RESOURCE_EXHAUSTED:
        return RpcErrorCategory.RATE_LIMIT
    if code in (
        grpc.StatusCode.UNAVAILABLE,
        grpc.StatusCode.DEADLINE_EXCEEDED,
        grpc.StatusCode.ABORTED,
        grpc.StatusCode.INTERNAL,
    ):
        return RpcErrorCategory.SERVICE
    return RpcErrorCategory.UNKNOWN


def normalize_error(exc: Exception, fallback: str = "unexpected rpc failure") -> AmeideRpcError:
    if isinstance(exc, AmeideRpcError):
        return exc
    if isinstance(exc, grpc.RpcError):
        code = exc.code() or grpc.StatusCode.UNKNOWN
        return AmeideRpcError(
            message=exc.details() or fallback,
            code=code,
            category=_categorize(code),
            retryable=code in RETRYABLE_CODES,
        )
    return AmeideRpcError(
        message=str(exc) or fallback,
        code=grpc.StatusCode.UNKNOWN,
        category=RpcErrorCategory.UNKNOWN,
        retryable=False,
    )
