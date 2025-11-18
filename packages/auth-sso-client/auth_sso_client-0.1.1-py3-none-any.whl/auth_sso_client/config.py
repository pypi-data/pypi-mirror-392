from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class AuthServerConfig:
    """auth_server 配置（与具体 Web 框架无关）。"""

    base_url: str
    """auth_server 基地址，例如 https://auth.example.com/agent/auth（结尾不含 /login）。"""

    login_path: str = "/login"
    """登录入口路径，一般保持默认。"""

    exchange_path: str = "/v1/exchange"
    """auth_code 兑换路径，一般保持默认。"""

    provider: str = "wecom"
    """登录提供方，目前仅支持 wecom，用于拼接 /login?provider=...。"""

    timeout_seconds: float = 8.0
    """与 auth_server 通信的 HTTP 超时时间（秒）。"""


@dataclass(slots=True)
class CookieConfig:
    """会话 Cookie 与 CSRF Cookie 配置，由业务侧决定命名与 TTL。"""

    session_cookie_name: str = "aqp_sid"
    session_ttl_seconds: int = 7200
    session_cookie_path: str = "/"
    session_cookie_secure: bool = False
    session_cookie_samesite: str = "lax"
    session_cookie_domain: Optional[str] = None

    csrf_cookie_name: str = "aqp_csrf_token"

