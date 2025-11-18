from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(slots=True)
class UserInfo:
    """auth_server /v1/exchange 返回的最小化用户信息视图。"""

    wecom_uid: str
    wecom_uname: Optional[str] = None
    wecom_dept_id: Optional[int] = None
    wecom_dept_name: Optional[str] = None
    raw: Dict[str, Any] | None = None

