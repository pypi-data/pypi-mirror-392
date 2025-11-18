from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable, Optional, Dict, Iterable, List

from weixinauto.domain.license_manager import LicenseManager
from weixinauto.infra.uia.wechat_driver import WeChatDriver
from .message import ChatMessage

# ====== 类型别名 ======
OnMessage = Callable[..., None]


# ====== ChatWnd：对外暴露的子窗口对象 ======
@dataclass(eq=False)
class ChatWnd:
    """
    对外暴露的微信子窗口对象：
      - title: 群名 / 聊天窗口标题
      - reply(text): 发送回复（带自回声抑制）
    """
    title: str

    def reply(self, text: str) -> bool: ...
    # 内部方法在 stub 里不暴露，避免用户误用
    # def _update_reply_fn(self, fn: Callable[[str], bool]) -> None: ...
    # def _record_incoming(self, text: str, is_self: Optional[bool]) -> None: ...


# ====== 单窗监听线程（高级用户可直接用） ======
class ChatWindowListener(threading.Thread):
    """
    单个聊天窗口监听线程。

    一般不直接给最终用户使用，建议优先用 MultiChatManager。
    """

    title: str
    need_nickname: bool
    poll: float
    debug_nick: bool

    def __init__(
        self,
        title: str,
        on_message: OnMessage,
        *,
        driver: WeChatDriver,
        need_nickname: bool = True,
        license_manager: Optional[LicenseManager] = None,
        poll_sec: float = ...,
        debug_nick: bool = False,
    ) -> None: ...

    def stop(self) -> None: ...
    def push_outgoing_preview(self, text: str) -> None: ...
    # run/start 继承自 Thread，这里不必重复声明


# ====== 多群管理：对外推荐入口 ======
class MultiChatManager:
    """
    多个聊天窗口的统一管理器：

    - 构造时传入要监听的群名列表 titles
    - 调用 start_all() 启动所有监听
    - 轮询 get_listen_messages() 获取新消息：
        for chat_wnd, msgs in manager.get_listen_messages().items():
            for msg in msgs:
                chat_wnd.reply("你的回复")
    """

    def __init__(
        self,
        titles: Iterable[str],
        on_message: Optional[OnMessage] = None,
        *,
        driver: WeChatDriver,
        need_nickname: bool = True,
        poll_sec: float = 0.15,
        license_manager: Optional[LicenseManager] = None,
        bring_front_on_new: Optional[bool] = None,
    ) -> None: ...

    def add_listens(
        self,
        titles: Iterable[str],
        *,
        need_nickname: Optional[bool] = None,
        poll_sec: Optional[float] = None,
    ) -> None: ...

    def start_all(self) -> None: ...
    def stop_all(self, *, join: bool = True, timeout: float = 1.5) -> None: ...

    def alive(self) -> Dict[str, bool]: ...
    def push_outgoing_preview(self, title: str, text: str) -> None: ...

    def get_listen_messages(self, *, clear: bool = True) -> Dict[ChatWnd, List[ChatMessage]]: ...
    def get_chat_wnd(self, title: str) -> Optional[ChatWnd]: ...


__all__ = [
    "OnMessage",
    "ChatWnd",
    "ChatWindowListener",
    "MultiChatManager",
]
