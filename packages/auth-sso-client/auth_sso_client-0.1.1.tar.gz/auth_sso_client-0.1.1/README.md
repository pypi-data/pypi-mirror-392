## auth_sso_client 简介

`auth_sso_client` 是一个围绕 auth_server 协议封装的轻量级 Python/ FastAPI SDK，用于：

- 生成跳转到外部 auth_server 的企业微信登录地址；
- 调用 auth_server `/v1/exchange` 兑换一次性 `auth_code` 为用户信息；
- 在 FastAPI 中一行挂载 `/sso/login/wecom` 与 `/sso/consume` 路由，并在本域创建会话 Cookie。

---

## 核心模型与配置

- `AuthServerConfig`
  - `base_url`: auth_server 基地址，例如 `https://auth.example.com/agent/auth`（不含 `/login`）。
  - `login_path`: 登录入口路径，默认 `/login`。
  - `exchange_path`: 兑换入口路径，默认 `/v1/exchange`。
  - `provider`: 登录提供方，默认 `"wecom"`。
  - `timeout_seconds`: 与 auth_server 通信的 HTTP 超时时间（秒），默认 `8.0`。
- `CookieConfig`
  - `session_cookie_name`: 会话 Cookie 名，默认 `app_sid`。
  - `session_ttl_seconds`: 会话 TTL（秒），默认 `7200`。
  - `session_cookie_path`: 会话 Cookie 路径，默认 `/`。
  - `session_cookie_secure`: 是否仅在 HTTPS 下发送 Cookie。
  - `session_cookie_samesite`: `lax|strict|none`，默认 `lax`。
  - `session_cookie_domain`: 可选 Cookie 域；为空时为 host-only Cookie。
  - `csrf_cookie_name`: CSRF Cookie 名，默认 `app_csrf_token`。
- `UserInfo`
  - `wecom_uid`: 企业微信用户 UserId。
  - `wecom_uname`: 企业微信用户姓名（可选）。
  - `wecom_dept_id`: 主部门 ID（可选）。
  - `wecom_dept_name`: 主部门名称（可选）。
  - `raw`: 原始响应字典，便于扩展。

---

## 纯逻辑 API

模块：`auth_sso_client.core`

```python
from auth_sso_client.config import AuthServerConfig
from auth_sso_client.core import build_login_url, exchange_auth_code
from auth_sso_client.models import UserInfo

config = AuthServerConfig(base_url="https://auth.example.com/agent/auth")

# 1) 生成登录 URL，供 302 跳转使用
login_url = build_login_url(
    config=config,
    consume_url="https://web-app.example.com/sso/consume",
    rd="/agent/app/#/mobile",
)

# 2) 在 /sso/consume 中兑换一次性 auth_code
user: UserInfo = await exchange_auth_code(config, code="一次性auth_code")
print(user.wecom_uid, user.wecom_uname)
```

错误会被统一封装为异常（见“错误处理”一节），调用方可按需捕获：

```python
from auth_sso_client.errors import (
    AuthCodeInvalidError,
    AuthServerNetworkError,
    AuthServerResponseError,
)
```

---

## FastAPI 集成示例（推荐）

模块：`auth_sso_client.fastapi`

在任意 FastAPI 应用中，一行挂载 SSO 路由：

```python
from fastapi import APIRouter

from auth_sso_client.config import AuthServerConfig, CookieConfig
from auth_sso_client.fastapi import create_sso_router
from auth_sso_client.models import UserInfo

from core.settings import get_settings
from services.session_service import create_session  # 业务侧会话创建逻辑

settings = get_settings()

auth_config = AuthServerConfig(
    base_url=getattr(settings, "AUTH_SERVER_BASE_URL", ""),  # 可留空，允许从 Referer 推断
)

cookie_config = CookieConfig(
    session_cookie_name=getattr(settings, "SESSION_COOKIE_NAME", "app_sid"),
    session_ttl_seconds=int(getattr(settings, "SESSION_TTL_SECONDS", 7200) or 7200),
    session_cookie_path=getattr(settings, "SESSION_COOKIE_PATH", "/"),
    session_cookie_secure=bool(getattr(settings, "COOKIE_SECURE", False)),
    session_cookie_samesite=str(getattr(settings, "SESSION_COOKIE_SAMESITE", "lax")).lower(),
    session_cookie_domain=getattr(settings, "SESSION_COOKIE_DOMAIN", None),
    csrf_cookie_name=getattr(settings, "CSRF_COOKIE_NAME", "app_csrf_token"),
)


async def create_session_from_user(user: UserInfo) -> str:
    # 业务可以根据需要使用 user.raw 里的更多字段
    return await create_session(uid=user.wecom_uid)


router = APIRouter()
router.include_router(
    create_sso_router(
        config=auth_config,
        create_session_cb=create_session_from_user,
        cookie_config=cookie_config,
    )
)
```

挂载后，该应用会自动对外提供：

- `GET /sso/login/wecom`: 统一登录入口，内部 302 到 `<AUTH_BASE>/login?provider=wecom&redirect=...`。
- `GET /sso/consume`: 回调入口，内部调用 `<AUTH_BASE>/v1/exchange`，根据返回用户信息创建本域会话 Cookie，并 302 到 `rd` 或 `/`。

行为与当前 web_app 中的 `/sso/login/wecom` 与 `/sso/consume` 保持一致。

---

## 错误处理约定

模块：`auth_sso_client.errors`

- `AuthSSOError`: 所有 SDK 异常的基类。
- `AuthServerNetworkError`:
  - 网络相关错误（超时、连接失败等），一般可视情况进行重试或降级。
- `AuthServerResponseError`:
  - auth_server 返回非预期响应（如 5xx 或响应体非 JSON），包含 `status_code` 与截断后的响应体片段。
- `AuthCodeInvalidError`:
  - 一次性 `auth_code` 不存在、已使用或已过期。

FastAPI 适配层会把这些异常映射为合适的 HTTP 状态码：

- `AuthCodeInvalidError` → 400；
- 其它错误 → 502。

如果直接使用 `core.exchange_auth_code`，建议在业务侧捕获上述异常并做好日志与兜底处理。
