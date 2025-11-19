"""Functions to send HTTP requests via requests and aiohttp modules."""

import asyncio
import json
import socket
from functools import wraps
from typing import Any, Dict, Union
from xml.etree import ElementTree

import requests
from aiohttp import (
    BasicAuth,
    ClientConnectionError,
    ClientConnectorCertificateError,
    ClientOSError,
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    InvalidURL,
    ServerDisconnectedError,
)

from .exceptions import (
    TinyToolsRequestConnectionError,
    TinyToolsRequestError,
    TinyToolsRequestHTTPError,
    TinyToolsRequestInternalServerError,
    TinyToolsRequestNotFound,
    TinyToolsRequestSSLError,
    TinyToolsRequestTimeout,
    TinyToolsRequestUnauthenticated,
)

DEFAULT_TIMEOUT = 3
DEFAULT_RETRIES = 1


def _parse_parameters(
    host, path, schema, port, username, password, timeout, retries, verify
):
    """Parse parameters for request - url, auth, timeout."""
    # Small modification to also handle general purpose requests
    if (host.startswith("http://") or host.startswith("https://")) and path is None:
        url = host
        # Always verify when given complete URL
        verify = True
    else:
        url = f"{schema}://{host}:{port}{path}"
        if verify is None:
            # Disable ssl verification for tinycontrol devices, which by default use insecure
            # certificates, so they can be easily handled with library.
            verify = schema != "https"
    if username:
        auth = (username, password)
    else:
        auth = None
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    if retries is None:
        retries = DEFAULT_RETRIES
    return url, auth, timeout, retries, verify


def _handle_errors(exc, response=None):
    """Handle errors for request.

    Unifies errors for asyncio and basic version.
    """
    try:
        raise exc
    except (requests.exceptions.ConnectTimeout, asyncio.TimeoutError) as exc:
        raise TinyToolsRequestTimeout("Timed out") from exc
    except (requests.exceptions.SSLError, ClientConnectorCertificateError) as exc:
        raise TinyToolsRequestSSLError("SSL error") from exc
    except (
        requests.exceptions.ConnectionError,
        ClientConnectionError,
        socket.gaierror,
    ) as exc:
        raise TinyToolsRequestConnectionError("Connection error") from exc
    except (requests.exceptions.InvalidURL, InvalidURL) as exc:
        raise TinyToolsRequestError("Invalid URL") from exc
    except (requests.exceptions.HTTPError, ClientResponseError) as exc:
        if hasattr(response, "status_code"):
            status_code = response.status_code
        else:  # For aiohttp it will be status
            status_code = response.status
        if status_code == 401:
            raise TinyToolsRequestUnauthenticated("Authentication error") from exc
        elif status_code == 404:
            raise TinyToolsRequestNotFound("Not found") from exc
        elif status_code == 500:
            raise TinyToolsRequestInternalServerError("Server error") from exc
        else:
            raise TinyToolsRequestHTTPError(f"HTTP {status_code} error") from exc
    except Exception as exc:
        raise TinyToolsRequestError("Unexpected request error") from exc


def _handle_content(content_type, content, response):
    """Handle response content and pack it into TinyToolsResponse."""
    result = {
        "_response": response,
        "parsed": None,
    }
    # TODO: Add ping for requests method (ATM missing for aiohttp).
    if hasattr(response, "elapsed"):
        result["elapsed"] = response.elapsed.total_seconds()
        result["ping"] = round(result["elapsed"] * 1000, 3)
    try:
        if content_type == "application/json":
            result["parsed"] = json.loads(content)
        elif content_type == "text/html":
            result["parsed"] = {}
        elif content_type == "text/xml":
            result["parsed"] = {
                item.tag: item.text for item in ElementTree.fromstring(content)
            }
    except (ElementTree.ParseError, ValueError) as exc:
        raise TinyToolsRequestError("Cannot parse response") from exc
    return result


def request(
    method: str,
    host: str,
    path: str,
    schema: str = "http",
    port: int = 80,
    username: str = "",
    password: str = "",
    timeout: Union[int, None] = None,
    retries: Union[int, None] = None,
    verify: Union[bool, None] = None,
    data: Union[Any, None] = None,
    headers: Union[Dict[str, str], None] = None,
    session: Union[requests.Session, None] = None,
):
    """Send request to device and return dict with response or errors."""
    url, auth, timeout, retries, verify = _parse_parameters(
        host, path, schema, port, username, password, timeout, retries, verify
    )
    response = None
    try:
        if session is not None:
            _request = session.request
        else:
            _request = requests.request
        response = _request(
            method,
            url,
            auth=auth,
            data=data,
            headers=headers,
            timeout=timeout,
            verify=verify,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectTimeout as exc:
        if retries:
            return request(
                method,
                host,
                path,
                schema,
                port,
                username,
                password,
                timeout,
                retries - 1,
                verify,
                data,
                headers,
            )
        _handle_errors(exc, response)
    except Exception as exc:
        _handle_errors(exc, response)
    else:
        return _handle_content(
            response.headers.get("content-type"), response.content, response
        )


@wraps(request)
def get(*args, silent=False, **kwargs):
    """Send GET request.

    Accepts the same parameters as request(), except method (GET).
    Also accepts param `silent`, defining whether to raise errors.
    """
    try:
        return request("GET", *args, **kwargs)
    except TinyToolsRequestError:
        if silent:
            return None
        raise


@wraps(request)
def post(*args, **kwargs):
    """Send POST request.

    Accepts the same parameters as request(), except method (POST).
    Also sets headers.
    """
    return request(
        "POST",
        *args,
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        **kwargs,
    )


async def async_request(
    method,
    host,
    path,
    schema="http",
    port=80,
    username=None,
    password=None,
    timeout=None,
    retries=None,
    verify=None,
    params=None,
    data=None,
    headers=None,
    session: Union[ClientSession, None] = None,
):
    """Async request with aiohttp for given resource.

    It can return text or json-parsed response, else raise exception.
    """
    url, auth, timeout, retries, verify = _parse_parameters(
        host, path, schema, port, username, password, timeout, retries, verify
    )
    if auth:
        auth = BasicAuth(*auth)
    response = None
    try:
        async with session.request(
            method,
            url,
            auth=auth,
            params=params,
            timeout=ClientTimeout(total=timeout),
            verify_ssl=verify,
        ) as response:
            response.raise_for_status()
            content = await response.text()
    except (asyncio.TimeoutError, ClientOSError, ServerDisconnectedError) as exc:
        # Retry only on timeout and few specific client connection errors
        # (they happen randomly at least on Windows).
        if retries:
            return await async_request(
                method,
                host,
                path,
                schema,
                port,
                username,
                password,
                timeout,
                retries - 1,
                verify,
                params,
                data,
                headers,
                session,
            )
        _handle_errors(exc, response)
    except Exception as exc:
        _handle_errors(exc, response)
    return _handle_content(response.content_type, content, response)


@wraps(async_request)
async def async_get(*args, silent=False, **kwargs):
    """Send async GET request.

    Accepts the same parameters as request(), except method (GET).
    Also accepts param `silent`, defining whether to raise errors.
    """
    try:
        return await async_request("GET", *args, **kwargs)
    except TinyToolsRequestError:
        if silent:
            return None
        raise
