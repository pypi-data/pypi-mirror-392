from __future__ import annotations

from typing import Optional
from urllib.parse import urlencode

import httpx

from .config import AuthServerConfig
from .errors import AuthCodeInvalidError, AuthServerNetworkError, AuthServerResponseError
from .models import UserInfo


def build_login_url(config: AuthServerConfig, consume_url: str, rd: Optional[str] = None) -> str:
    """构造 auth_server 登录入口 URL。

    - consume_url: web_app 的 /sso/consume 完整 URL（含 scheme/host/root_path）；
    - rd: 登录完成后的业务前端路由或落地路径。
    """
    consume = consume_url.rstrip("/")
    redirect_target = consume
    params: dict[str, str] = {}
    if rd is not None:
        params["rd"] = rd
    if params:
        redirect_target = f"{consume}?{urlencode(params)}"

    login_base = config.base_url.rstrip("/") + config.login_path
    qs = urlencode({"provider": config.provider, "redirect": redirect_target})
    return f"{login_base}?{qs}"


async def exchange_auth_code(
    config: AuthServerConfig,
    code: str,
    *,
    client: Optional[httpx.AsyncClient] = None,
) -> UserInfo:
    """调用 auth_server /v1/exchange 兑换一次性 auth_code 为用户信息。"""
    if not code:
        raise AuthCodeInvalidError("empty_code")

    exchange_url = config.base_url.rstrip("/") + config.exchange_path
    own_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=config.timeout_seconds)

    try:
        resp = await client.post(exchange_url, json={"code": code})
    except Exception as e:  # noqa: BLE001
        raise AuthServerNetworkError(f"auth_server request failed: {e}") from e
    finally:
        if own_client:
            await client.aclose()

    if resp.status_code == 400:
        # auth_server 约定 400 表示 code 无效或已使用
        raise AuthCodeInvalidError(resp.text.strip() or "code_invalid_or_used")

    if resp.status_code != 200:
        snippet = resp.text[:200] if resp.text else None
        raise AuthServerResponseError(resp.status_code, snippet)

    data = resp.json()
    uid = str(data.get("wecom_uid") or "").strip()
    if not uid:
        raise AuthServerResponseError(resp.status_code, "missing wecom_uid in response")

    return UserInfo(
        wecom_uid=uid,
        wecom_uname=data.get("wecom_uname"),
        wecom_dept_id=data.get("wecom_dept_id"),
        wecom_dept_name=data.get("wecom_dept_name"),
        raw=data,
    )

