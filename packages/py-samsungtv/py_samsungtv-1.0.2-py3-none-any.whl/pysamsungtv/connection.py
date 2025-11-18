"""Low-level HTTPS connection helper for Samsung TVs."""
from __future__ import annotations

import json
import ssl
from typing import Any, Mapping, MutableMapping

import aiohttp

from .exceptions import SamsungTVError, SamsungTVProtocolError


class SamsungTVConnection:
    """Wraps the aiohttp session lifecycle and request/response parsing."""

    def __init__(
        self,
        host: str,
        *,
        port: int,
        verify_ssl: bool,
        request_timeout: float,
        headers: Mapping[str, str],
    ) -> None:
        self._host = host
        self._port = port
        self._timeout = aiohttp.ClientTimeout(total=request_timeout)
        self._headers: MutableMapping[str, str] = dict(headers)
        # older models only allow DH group 1 (<2016)
        self._verify_ssl = verify_ssl
        self._security_level = 2
        self._session: aiohttp.ClientSession | None = None
        self._ssl_context: ssl.SSLContext | None = None

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def request(self, payload: Mapping[str, Any]) -> Any:
        await self._ensure_session()
        try:
            return await self._execute_request(payload)
        # fall back to older security level for old TVs
        except aiohttp.ClientConnectorSSLError as exc:
            if self._security_level > 1 and self._is_dh_key_error(exc):
                await self._reset_session(security_level=1)
                await self._ensure_session()
                return await self._execute_request(payload)
            raise SamsungTVError(f"Failed to send request: {exc}") from exc
        except aiohttp.ClientError as exc:  # pragma: no cover - transport failure
            raise SamsungTVError(f"Failed to send request: {exc}") from exc

    async def _execute_request(self, payload: Mapping[str, Any]) -> Any:
        if self._session is None:
            raise SamsungTVError("HTTP session was not initialized")
        url = f"https://{self._host}:{self._port}/"
        response = await self._session.post(
            url,
            headers=self._headers,
            json=payload,
            ssl=self._ssl_context if self._ssl_context is not None else False,
        )
        async with response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as exc:
                body = await response.text()
                raise SamsungTVProtocolError(
                    f"HTTP {exc.status} returned for {payload.get('method')}: {body.strip()}"
                ) from exc
            text = await response.text()
            if not text.strip():
                raise SamsungTVProtocolError("TV returned an empty response body")
            try:
                return json.loads(text)
            except json.JSONDecodeError as exc:
                raise SamsungTVProtocolError(f"Invalid JSON response: {text}") from exc

    async def _ensure_session(self) -> None:
        if self._session is None or self._session.closed:
            self._ssl_context = self._build_ssl_context()
            connector = aiohttp.TCPConnector(ssl=self._ssl_context)
            self._session = aiohttp.ClientSession(
                timeout=self._timeout, connector=connector
            )

    async def _reset_session(self, *, security_level: int) -> None:
        self._security_level = security_level
        if self._session is not None:
            await self._session.close()
        self._session = None
        self._ssl_context = None

    def _build_ssl_context(self) -> ssl.SSLContext:
        context = ssl.create_default_context()
        if not self._verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        if self._security_level == 1:
            try:
                context.set_ciphers("DEFAULT:@SECLEVEL=1")
            except ssl.SSLError:
                pass
        return context

    @staticmethod
    def _is_dh_key_error(exc: aiohttp.ClientConnectorSSLError) -> bool:
        message = str(exc).lower()
        if "dh key too small" in message:
            return True
        os_error = getattr(exc, "os_error", None)
        if os_error and "dh key too small" in str(os_error).lower():
            return True
        return False


__all__ = ["SamsungTVConnection"]
