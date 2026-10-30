"""MuMu 点击必须走 AdbShell。

竖屏短边 720 的截图坐标系里，AdbController 的默认输入会先试 Maatouch，
再试 minitouch，最后才是 AdbShell。MuMu 上前两种会报告点击成功，但触摸
映射和这张 720×1280 画面不一致，邮件入口点了邮箱也不开。AdbShell 执行
``adb shell input tap``，坐标和截图一致。

Project Interface v2 没有 Adb 输入字段，协议是自动检测。``assets/interface.json``
里的 ``adb.input = 1`` 只给打包的 MFAAvalonia 用（1 = AdbShell）。MaaDebugger
的 Connect 不读这个字段，自己写 Python 控制器时调用 ``connect_adb``。
"""

from __future__ import annotations

from typing import Any, Optional

# MaaAdbInputMethod_AdbShell。不要改成别的位：2/4/8 会回到点偏的快路径。
ADB_SHELL_INPUT = 1


def adb_shell_input_methods():
    """返回 maafw 的 AdbShell 枚举。调用时才导入 maa，静态检查不需要装框架。"""
    from maa.define import MaaAdbInputMethodEnum

    value = MaaAdbInputMethodEnum.AdbShell
    if int(value) != ADB_SHELL_INPUT:
        raise RuntimeError(
            f"MaaAdbInputMethodEnum.AdbShell 是 {int(value)}，不是 {ADB_SHELL_INPUT}"
        )
    return value


def connect_adb(
    adb_path,
    address: str,
    *,
    screencap_methods: Optional[int] = None,
    config: Optional[dict[str, Any]] = None,
    agent_path=None,
):
    """连接 MuMu。截图方式保持框架默认，输入只允许 AdbShell。"""
    from maa.controller import AdbController
    from maa.define import MaaAdbScreencapMethodEnum

    kwargs: dict[str, Any] = {
        "adb_path": adb_path,
        "address": address,
        "screencap_methods": (
            MaaAdbScreencapMethodEnum.Default
            if screencap_methods is None
            else screencap_methods
        ),
        "input_methods": adb_shell_input_methods(),
        "config": {} if config is None else config,
    }
    if agent_path is not None:
        kwargs["agent_path"] = agent_path
    return AdbController(**kwargs)
