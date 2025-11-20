from .mailapi_freetools import (
    MailAPI,
    AsyncMailAPI,
    MailAPIError, BadRequest, Unauthorized, Forbidden, ServerError,
    GeneratedEmail, Message, Messages,
)

__all__ = [
    "MailAPI", "AsyncMailAPI",
    "MailAPIError", "BadRequest", "Unauthorized", "Forbidden", "ServerError",
    "GeneratedEmail", "Message", "Messages",
]

__version__ = "0.1.0"
