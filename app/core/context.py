from contextvars import ContextVar
from typing import Optional

client_ip_ctx: ContextVar[Optional[str]] = ContextVar("client_ip_ctx", default=None)

