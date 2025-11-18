from __future__ import annotations

from typing import Awaitable, Callable, Optional
from urllib.parse import urlencode, urlparse

from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse

from .config import AuthServerConfig, CookieConfig
from .core import build_login_url, exchange_auth_code
from .errors import (
    AuthCodeInvalidError,
    AuthSSOError,
    AuthServerNetworkError,
    AuthServerResponseError,
)
from .models import UserInfo


CreateSessionFn = Callable[[UserInfo], Awaitable[str]]


def _external_base_url(request: Request) -> str:
    """基于 X-Forwarded-* 推导对外可见的基础 URL（不依赖项目内部工具）。"""
    headers = request.headers
    proto = headers.get("x-forwarded-proto") or request.url.scheme
    host = headers.get("x-forwarded-host") or headers.get("host")
    if proto and host:
        origin = f"{proto}://{host}"
    else:
        origin = str(request.base_url).rstrip("/")
    return origin.rstrip("/")


def _infer_auth_server_base_url_from_referer(request: Request) -> Optional[str]:
    """根据 Referer 头自动推断 auth_server 基地址（可选兜底）。"""
    referer = request.headers.get("referer") or request.headers.get("referrer")
    if not referer:
        return None
    try:
        parsed = urlparse(referer)
    except Exception:  # noqa: BLE001
        return None
    if not parsed.scheme or not parsed.netloc:
        return None
    path = parsed.path or ""
    if not path:
        return None
    base_path: Optional[str] = None
    for marker in ("/callback/wecom", "/login"):
        idx = path.rfind(marker)
        if idx != -1:
            base_path = path[:idx]
            break
    if base_path is None:
        stripped = path.strip("/")
        if "/" not in stripped:
            return None
        base_path = "/" + stripped.rsplit("/", 1)[0]
    return f"{parsed.scheme}://{parsed.netloc}{base_path}"


def create_sso_router(
    config: AuthServerConfig,
    create_session_cb: CreateSessionFn,
    cookie_config: CookieConfig,
    *,
    allow_infer_auth_base_from_referer: bool = True,
) -> APIRouter:
    """创建基于 auth_server 的 WeCom SSO Router。

    - config: auth_server 的基础配置；
    - create_session_cb: 业务侧创建会话的回调，入参为 UserInfo，返回 sid；
    - cookie_config: 会话与 CSRF Cookie 配置；
    - allow_infer_auth_base_from_referer: 当 config.base_url 为空时，是否尝试从 Referer 推断。
    """
    router = APIRouter(tags=["sso"])

    @router.get(
        "/sso/login/wecom",
        summary="SSO 登录入口：跳转到外部 auth_server（WeCom）",
        description=(
            "业务前端访问的统一 WeCom 登录入口。"
            "服务根据当前请求推导自身对外地址，拼接 /sso/consume 作为回调，"
            "并将 rd 作为业务前端落地路由传递给 auth_server。"
        ),
        responses={302: {"description": "Redirect to auth_server /login"}},
    )
    async def sso_login_wecom(
        request: Request,
        rd: Optional[str] = Query(
            None,
            description="登录完成后的前端路由或调试用落地路径，例如 /agent/aqp/#/mobile 或 /agent/aqp_api/v1/health",
        ),
    ) -> RedirectResponse:
        base = _external_base_url(request)
        # 自动拼接 FastAPI/反向代理的 ROOT_PATH，确保在 /agent/aqp_api 等子路径下部署时，
        # 回调地址为 <origin><ROOT_PATH>/sso/consume（例如 http://localhost/agent/aqp_api/sso/consume）
        root_path = (request.scope.get("root_path") or "").rstrip("/")
        consume_url = f"{base}{root_path}/sso/consume"
        url = build_login_url(config, consume_url, rd)
        return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

    @router.get(
        "/sso/consume",
        summary="SSO 回调：消费 auth_server 的 auth_code 并在业务域落 Cookie",
        description=(
            "业务后端在用户完成企业微信登录后，用 auth_server 下发的一次性 auth_code 换取用户信息，"
            "并在本域创建会话 Cookie 和 CSRF Cookie，随后重定向到首页或指定页面。"
        ),
        responses={302: {"description": "Redirect to business page after SSO"}},
    )
    async def sso_consume(
        request: Request,
        response: Response,
        code: str = Query(..., description="auth_server 下发的一次性 auth_code"),
        rd: Optional[str] = Query(
            None,
            description="可选业务回跳地址，相对路径或完整 URL；为空时默认重定向到 '/'",
        ),
    ) -> Response:
        # 当 base_url 为空且允许推断时，从 Referer 兜底推断 auth_server 基地址
        auth_base = config.base_url
        if not auth_base and allow_infer_auth_base_from_referer:
            inferred = _infer_auth_server_base_url_from_referer(request)
            if not inferred:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="auth_server_base_url_not_configured",
                )
            auth_base = inferred

        if not auth_base:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="auth_server_base_url_not_configured",
            )

        cfg = AuthServerConfig(
            base_url=auth_base,
            login_path=config.login_path,
            exchange_path=config.exchange_path,
            provider=config.provider,
            timeout_seconds=config.timeout_seconds,
        )

        try:
            user = await exchange_auth_code(cfg, code)
        except AuthCodeInvalidError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e) or "auth_code_invalid_or_used",
            ) from e
        except AuthServerNetworkError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"auth_server_network_error: {e}",
            ) from e
        except AuthServerResponseError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"auth_server_response_error: {e}",
            ) from e
        except AuthSSOError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"auth_sso_error: {e}",
            ) from e

        sid = await create_session_cb(user)

        cookie_params = dict(
            key=cookie_config.session_cookie_name,
            value=sid,
            max_age=int(cookie_config.session_ttl_seconds or 7200),
            path=cookie_config.session_cookie_path or "/",
            httponly=True,
            samesite=str(cookie_config.session_cookie_samesite or "lax").lower(),
            secure=bool(cookie_config.session_cookie_secure),
        )
        if cookie_config.session_cookie_domain:
            cookie_params["domain"] = cookie_config.session_cookie_domain

        target = rd or "/"
        final_resp: Response = RedirectResponse(
            url=target, status_code=status.HTTP_302_FOUND
        )
        final_resp.set_cookie(**cookie_params)
        final_resp.set_cookie(
            key=cookie_config.csrf_cookie_name,
            value="1",
            max_age=int(cookie_config.session_ttl_seconds or 7200),
            path=cookie_config.session_cookie_path or "/",
            secure=bool(cookie_config.session_cookie_secure),
            httponly=False,
            samesite=str(cookie_config.session_cookie_samesite or "lax").lower(),
        )
        return final_resp

    return router
