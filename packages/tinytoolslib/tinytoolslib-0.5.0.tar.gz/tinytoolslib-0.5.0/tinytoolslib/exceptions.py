"""Exceptions for tinyToolsLib."""


class TinyToolsError(Exception):
    """Generic tinyTools exception."""


class TinyToolsUnsupported(TinyToolsError):
    """Unsupported action of tinycontrol device."""


# region Request related errors
class TinyToolsRequestError(TinyToolsError):
    """Base exception for request errors."""


class TinyToolsRequestTimeout(TinyToolsRequestError):
    """Request timed out while trying to connect to server."""


class TinyToolsRequestConnectionError(TinyToolsRequestError):
    """Connection error occurred."""


class TinyToolsRequestSSLError(TinyToolsRequestConnectionError):
    """An SSL error occurred."""


class TinyToolsRequestHTTPError(TinyToolsRequestError):
    """HTTP error occurred while handling request(HTTP 4xx/5xx)."""


class TinyToolsRequestUnauthenticated(TinyToolsRequestHTTPError):
    """Request requires authentication or is invalid (HTTP 401)."""


class TinyToolsRequestNotFound(TinyToolsRequestHTTPError):
    """Server could not find the requested resource (HTTP 404)."""


class TinyToolsRequestInternalServerError(TinyToolsRequestHTTPError):
    """Server has encountered a situation it does not know how to handle. (HTTP 500)."""


# endregion


class TinyToolsFlashError(TinyToolsError):
    """tinyTools flashing exception."""
