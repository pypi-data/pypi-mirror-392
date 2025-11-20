"""Custom exceptions for TextQL client"""

import grpc


class TextQLError(Exception):
    """Base exception for all TextQL errors"""
    pass


class AuthenticationError(TextQLError):
    """Raised when authentication fails"""
    pass


class ConnectionError(TextQLError):
    """Raised when connection to TextQL API fails"""
    pass


class InvalidRequestError(TextQLError):
    """Raised when request parameters are invalid"""
    pass


class RateLimitError(TextQLError):
    """Raised when API rate limit is exceeded"""
    pass


class NotFoundError(TextQLError):
    """Raised when a resource is not found"""
    pass


class ServerError(TextQLError):
    """Raised when TextQL server returns an error"""
    pass


def handle_grpc_error(error: grpc.RpcError) -> TextQLError:
    """Convert gRPC errors to TextQL exceptions"""
    if isinstance(error, grpc.Call):
        status_code = error.code()
        details = error.details()

        error_map = {
            grpc.StatusCode.UNAUTHENTICATED: AuthenticationError,
            grpc.StatusCode.PERMISSION_DENIED: AuthenticationError,
            grpc.StatusCode.NOT_FOUND: NotFoundError,
            grpc.StatusCode.INVALID_ARGUMENT: InvalidRequestError,
            grpc.StatusCode.RESOURCE_EXHAUSTED: RateLimitError,
            grpc.StatusCode.UNAVAILABLE: ConnectionError,
            grpc.StatusCode.INTERNAL: ServerError,
        }

        exception_class = error_map.get(status_code, TextQLError)
        return exception_class(f"{status_code.name}: {details}")

    return TextQLError(str(error))
