from __future__ import annotations


class AuthSSOError(Exception):
    """SDK 顶层异常基类。"""


class AuthServerNetworkError(AuthSSOError):
    """auth_server 网络异常（连接失败、超时等）。"""


class AuthServerResponseError(AuthSSOError):
    """auth_server 返回非预期响应（状态码或响应体异常）。"""

    def __init__(self, status_code: int, body_snippet: str | None = None) -> None:
        msg = f"auth_server unexpected response: {status_code}"
        if body_snippet:
            msg = f"{msg}, body={body_snippet}"
        super().__init__(msg)
        self.status_code = status_code
        self.body_snippet = body_snippet


class AuthCodeInvalidError(AuthSSOError):
    """一次性 auth_code 不存在、已被使用或已过期。"""

