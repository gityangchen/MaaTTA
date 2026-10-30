"""CDK 授权桩（一期）。

两档：

- ``base``：长期核心。一期领奖/邮件，以及之后的每日任务、刷关。
- ``activity``：限时内容。钓鱼、围猎、MVP 礼盒，以及四期钓鱼赛跑。

发码服务器和防篡改都还没做。本模块默认开发放行，避免模板联调被挡住。

环境变量：

- ``MAATTA_DEV_SKIP_CDK``：未设置、空串，或 ``1`` / ``true`` / ``yes`` / ``on``
  时直接通过。只有 ``0`` / ``false`` / ``no`` / ``off`` 会关掉放行。
  写错的其它值也按放行处理。
- ``MAATTA_CDK``：预留的授权串。关掉放行后，非空即视为本地占位通过，
  不会发到任何服务器，也不会校验签名。两档共用这一条，档位参数先留给以后的服务端。

不要把 CDK 写进仓库。
"""

from __future__ import annotations

import json
import os
from typing import Literal

Feature = Literal["base", "activity"]

_FEATURES = ("base", "activity")
_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off"}


def dev_skip_enabled() -> bool:
    """默认 True。只有明确的假值才要求本地 CDK 占位串。"""
    raw = os.environ.get("MAATTA_DEV_SKIP_CDK")
    if raw is None:
        return True
    value = raw.strip().lower()
    if value == "" or value in _TRUTHY:
        return True
    if value in _FALSY:
        return False
    return True


def check_license(feature: Literal["base", "activity"]) -> bool:
    """返回该档当前是否可用。未知档位一律 False，避免拼错名字还放行。"""
    if feature not in _FEATURES:
        return False
    if dev_skip_enabled():
        return True
    return bool(os.environ.get("MAATTA_CDK", "").strip())


def load_param(raw: object) -> dict | None:
    """解析 CustomAction / CustomRecognition 传入的 JSON 对象参数。"""
    if raw is None or raw == "":
        return {}
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def cdk_is_present() -> bool:
    """日志用。只报告有没有串，不返回内容。"""
    return bool(os.environ.get("MAATTA_CDK", "").strip())


if __name__ == "__main__":
    for name in _FEATURES:
        print(
            f"{name}: ok={check_license(name)} dev_skip={dev_skip_enabled()} cdk_present={cdk_is_present()}"
        )
