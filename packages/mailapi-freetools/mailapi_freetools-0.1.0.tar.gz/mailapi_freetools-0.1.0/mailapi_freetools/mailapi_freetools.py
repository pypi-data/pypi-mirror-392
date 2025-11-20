"""
MailAPI Python SDK
===================

Lightweight client for the MailAPI (https://mailapi.freetools.fr).

Features:
- Synchronous (`MailAPI`) and asynchronous (`AsyncMailAPI`) clients.
- Methods: `get_email()`, `get_messages(email)`, `ping()`.
- Utility method: `wait_for_message(...)` to wait for an email matching a criterion.
- Data models via `dataclasses`.
- Error handling (400/401/403/5xx) with dedicated exceptions.
- Timeouts, User-Agent header, and simple retries on 5xx errors.

Dependencies installation:
    pip install httpx

Usage example (sync):
    from mailapi import MailAPI

    client = MailAPI(api_key="YOUR_API_KEY")
    gen = client.get_email()
    print(gen.email)            # generated address
    print(gen.mails_endpoint)   # endpoint to check the mailbox

    messages = client.get_messages(gen.email)
    for m in messages.messages:
        print(m.subject, m.received_at)

Usage example (async):
    import asyncio
    from mailapi import AsyncMailAPI

    async def main():
        client = AsyncMailAPI(api_key="YOUR_API_KEY")
        gen = await client.get_email()
        print(gen.email)
        await client.aclose()

    asyncio.run(main())

License: MIT
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence
import time
import urllib.parse

import httpx

__all__ = [
    "MailAPI",
    "AsyncMailAPI",
    "MailAPIError",
    "BadRequest",
    "Unauthorized",
    "Forbidden",
    "ServerError",
    "GeneratedEmail",
    "Message",
    "Messages",
]

BASE_URL = "https://mailapi.freetools.fr"
USER_AGENT = "mailapi-sdk-python/1.0 (+https://mailapi.freetools.fr)"


# ----------------------------
# Exceptions
# ----------------------------
class MailAPIError(Exception):
    """Generic SDK-side error."""

    def __init__(self, message: str, *, status_code: Optional[int] = None, payload: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


class BadRequest(MailAPIError):
    """400 – invalid email format or incorrect request."""


class Unauthorized(MailAPIError):
    """401 – missing API key."""


class Forbidden(MailAPIError):
    """403 – invalid or expired API key."""


class ServerError(MailAPIError):
    """5xx – server error."""


# ----------------------------
# Data models
# ----------------------------
@dataclass
class GeneratedEmail:
    status: str
    email: str
    mails_endpoint: str
    uptime: Optional[str] = None
    contact: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GeneratedEmail":
        # The docs expose the "generate_email" and "mails_endpoint" keys
        email = data.get("generate_email") or data.get("email") or ""
        return GeneratedEmail(
            status=data.get("status", ""),
            email=email,
            mails_endpoint=data.get("mails_endpoint", f"/{email}"),
            uptime=data.get("uptime"),
            contact=data.get("contact", {}) or {},
        )


@dataclass
class Message:
    sender_email: str
    subject: str
    received_at: Optional[datetime]
    created_at: Optional[datetime]
    message: str
    links: List[str] = field(default_factory=list)

    @staticmethod
    def _parse_ts(ts: Optional[str]) -> Optional[datetime]:
        if not ts:
            return None
        try:
            cleaned = ts.replace(" (UTC)", "")
            return cleaned
        except Exception:
            return None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Message":
        return Message(
            sender_email=data.get("sender_email", ""),
            subject=data.get("subject", ""),
            received_at=Message._parse_ts(data.get("received_at")),
            created_at=Message._parse_ts(data.get("created_at")),
            message=data.get("message", ""),
            links=list(data.get("links", []) or [])
        )

@dataclass
class Messages:
    status: str
    email: str
    messages: List[Message]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Messages":
        msgs = [Message.from_dict(m) for m in data.get("messages", [])]
        return Messages(
            status=data.get("status", ""),
            email=data.get("email", ""),
            messages=msgs
        )



# ----------------------------
# Internal utilities
# ----------------------------

def _build_headers(api_key: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {"MailAPI-Key": api_key, "User-Agent": USER_AGENT}
    if extra:
        headers.update(extra)
    return headers


def _raise_for_status(status_code: int, payload: Optional[dict] = None) -> None:
    if status_code == 400:
        raise BadRequest("Invalid request (400)", status_code=400, payload=payload)
    if status_code == 401:
        raise Unauthorized("Missing API key (401)", status_code=401, payload=payload)
    if status_code == 403:
        raise Forbidden("Invalid or expired API key (403)", status_code=403, payload=payload)
    if 500 <= status_code:
        raise ServerError(f"Server error ({status_code})", status_code=status_code, payload=payload)


# ----------------------------
# Synchronous client
# ----------------------------
class MailAPI:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        timeout: float = 10.0,
        max_retries: int = 2,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        """Synchronous client for MailAPI.

        :param api_key: API key (header `MailAPI-Key`).
        :param base_url: Base URL, defaults to https://mailapi.freetools.fr
        :param timeout: Timeout in seconds for each request.
        :param max_retries: Number of retries on 5xx / network errors.
        :param transport: Optional httpx transport (testing/mocking).
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout, headers=_build_headers(api_key), transport=transport)

    # Context
    def __enter__(self) -> "MailAPI":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # Resources
    def close(self) -> None:
        self._client.close()

    # Requests
    def _get(self, path: str) -> Dict[str, Any]:
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                
                r = self._client.get(path)
                if r.status_code >= 400:
                    # Try to parse JSON to enrich the error
                    payload = None
                    try:
                        payload = r.json()
                    except Exception:
                        payload = None
                    _raise_for_status(r.status_code, payload)
                return r.json()
            except (httpx.HTTPError, ServerError) as e:
                last_exc = e
                # Retry only on network or 5xx errors
                if isinstance(e, ServerError) or (isinstance(e, httpx.HTTPError)):
                    if attempt < self.max_retries:
                        time.sleep(min(2 ** attempt, 3))
                        continue
                break
        if last_exc:
            raise last_exc
        raise MailAPIError("An unknown error occurred")

    # Public API
    def ping(self) -> Dict[str, Any]:
        """GET /ping → {"status": "OK"}"""
        return self._get("/ping")

    def get_email(self) -> GeneratedEmail:
        """GET /get_email → generated temporary address."""
        data = self._get("/get_email")
        return GeneratedEmail.from_dict(data)

    def get_messages(self, email: str) -> Messages:
        """GET /{email} → messages received for the given address.

        The email is encoded to be safe in the URL.
        """
        safe_email = urllib.parse.quote(email, safe="")
        data = self._get(f"/get_mails?mail={safe_email}")
        return Messages.from_dict(data)

    # High-level utility
    def wait_for_message(
        self,
        email: str,
        *,
        subject_contains: Optional[str] = None,
        timeout: float = 60.0,
        interval: float = 2.0,
    ) -> Optional[Message]:
        """Wait for a message to arrive for `email`.

        :param email: address to monitor
        :param subject_contains: if provided, only returns a message whose subject contains this substring (case-insensitive)
        :param timeout: maximum wait duration in seconds
        :param interval: polling period in seconds
        :return: found `Message` or `None` if timeout
        """
        deadline = time.monotonic() + timeout
        seen_ids: set[str] = set()

        def match(m: Message) -> bool:
            if subject_contains is None:
                return True
            return subject_contains.lower() in (m.subject or "").lower()

        while time.monotonic() < deadline:
            messages = self.get_messages(email)
            for m in messages.messages:
                # Build a stable identifier (timestamp + subject + sender)
                mid = f"{m.received_at if m.received_at else ''}|{m.subject}|{m.sender_email}"
                if mid in seen_ids:
                    continue
                seen_ids.add(mid)
                if match(m):
                    return m
            time.sleep(max(0.1, interval))
        return None


# ----------------------------
# Asynchronous client
# ----------------------------
class AsyncMailAPI:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        timeout: float = 10.0,
        max_retries: int = 2,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout, headers=_build_headers(api_key), transport=transport)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str) -> Dict[str, Any]:
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                r = await self._client.get(path)
                if r.status_code >= 400:
                    payload = None
                    try:
                        payload = r.json()
                    except Exception:
                        payload = None
                    _raise_for_status(r.status_code, payload)
                return r.json()
            except (httpx.HTTPError, ServerError) as e:
                last_exc = e
                if isinstance(e, ServerError) or (isinstance(e, httpx.HTTPError)):
                    if attempt < self.max_retries:
                        await _async_sleep(min(2 ** attempt, 3))
                        continue
                break
        if last_exc:
            raise last_exc
        raise MailAPIError("An unknown error occurred")

    async def ping(self) -> Dict[str, Any]:
        return await self._get("/ping")

    async def get_email(self) -> GeneratedEmail:
        data = await self._get("/get_email")
        return GeneratedEmail.from_dict(data)

    async def get_messages(self, email: str) -> Messages:
        safe_email = urllib.parse.quote(email, safe="")
        data = await self._get(f"/{safe_email}")
        return Messages.from_dict(data)

    async def wait_for_message(
        self,
        email: str,
        *,
        subject_contains: Optional[str] = None,
        timeout: float = 60.0,
        interval: float = 2.0,
    ) -> Optional[Message]:
        deadline = time.monotonic() + timeout
        seen_ids: set[str] = set()

        def match(m: Message) -> bool:
            if subject_contains is None:
                return True
            return subject_contains.lower() in (m.subject or "").lower()

        while time.monotonic() < deadline:
            messages = await self.get_messages(email)
            for m in messages.messages:
                mid = f"{int(m.received_at.timestamp()) if m.received_at else ''}|{m.subject}|{m.sender_email}"
                if mid in seen_ids:
                    continue
                seen_ids.add(mid)
                if match(m):
                    return m
            await _async_sleep(max(0.1, interval))
        return None


# Small helper to sleep async without importing asyncio at top-level
async def _async_sleep(seconds: float) -> None:
    import asyncio

    await asyncio.sleep(seconds)
