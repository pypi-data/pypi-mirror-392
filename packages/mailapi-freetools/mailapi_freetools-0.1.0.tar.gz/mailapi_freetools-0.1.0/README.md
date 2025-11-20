# MailAPI Python SDK

A lightweight, typed Python client for the **MailAPI-Freetools** service (https://mailapi.freetools.fr) to generate disposable inboxes and fetch messages.

---

## Features
- Synchronous (`MailAPI`) and asynchronous (`AsyncMailAPI`) clients.
- Endpoints: `/ping`, `/get_email`, `/{email}`.
- High-level `wait_for_message()` utility for polling a mailbox.
- Typed dataclasses for responses (`GeneratedEmail`, `Message`, `Messages`).
- Detailed error classes: `BadRequest`, `Unauthorized`, `Forbidden`, `ServerError`, `MailAPIError`.

---

## Installation
```bash
pip install mailapi_freetools
```

---

## Quick Start (Synchronous)
```python
from mailapi_freetools import MailAPI

client = MailAPI(api_key="YOUR_API_KEY")
info = client.get_email()
print(info.email)           # generated address
print(info.mails_endpoint)  # endpoint to poll messages

msgs = client.get_messages(info.email)
for m in msgs.messages:
    print(m.subject, m.received_at)
```

## Quick Start (Asynchronous)
```python
import asyncio
from mailapi_freetools import AsyncMailAPI

async def main():
    client = AsyncMailAPI(api_key="YOUR_API_KEY")
    info = await client.get_email()
    print(info.email)
    await client.aclose()

asyncio.run(main())
```

---

## Waiting for a Specific Email
```python
from mailapi_freetools import MailAPI

client = MailAPI(api_key="YOUR_API_KEY")
addr = client.get_email().email
msg = client.wait_for_message(addr, subject_contains="Your code", timeout=60)
if msg:
    print("Found:", msg.subject)
else:
    print("Timed out.")
```

---

## Error Handling
```python
from mailapi_freetools import MailAPI, MailAPIError

try:
    MailAPI(api_key="...").ping()
except MailAPIError as e:
    print(e.status_code, e)
```


