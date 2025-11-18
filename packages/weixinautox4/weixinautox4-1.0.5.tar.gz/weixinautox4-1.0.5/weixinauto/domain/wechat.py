# -*- coding: utf-8 -*-
# wechat.py
from __future__ import annotations
from typing import Callable, Optional, List, Iterable, Dict

from .license_manager import LicenseManager, LicenseNotActivatedError
from ..infra.uia.chat_listener import ChatWindowListener, MultiChatManager, ChatWnd
from ..infra.uia.message import ChatMessage
from ..infra.uia.wechat_driver import WeChatDriver


class Wechat:
    """
    Wechat类：封装了窗口定位、子窗口管理和消息监听等功能。
    设计目标：简化操作，通过 WeChatDriver 与 ChatWindowListener 实现自动化操作。
    同时接入 LicenseManager，在未激活时不会创建 WeChatDriver。
    """

    def __init__(self, backend=None, *, wait_seconds: float = 10.0, license_manager: LicenseManager | None = None):
        # 先不直接创建 driver，等确认已激活后再创建
        self._driver: WeChatDriver | None = None
        self._single_listeners: Dict[str, ChatWindowListener] = {}
        self._multi_manager: MultiChatManager | None = None
        self._login = None

        # License 管理器：如果外面没传，就用默认的
        self._license_mgr = license_manager or LicenseManager()
        self._wait_seconds = wait_seconds

    # ---------- 内部：确保 driver 存在 ----------

    def _ensure_driver(self) -> bool:
        """
        确保 _driver 已经可用：
        - 已经有 driver：直接返回 True
        - 没有 driver：尝试通过 LicenseManager 创建
        - 如果未激活：返回 False，并打印提示
        """
        if self._driver is not None:
            return True

        try:
            drv = self._license_mgr.create_wechat_driver(silent=True)
        except LicenseNotActivatedError:
            drv = None

        if drv is None:
            print("[Wechat] 当前设备尚未激活，请先调用 Wechat.activate('激活码') 完成激活。")
            return False

        self._driver = drv
        return True

    # ---------- 激活相关 ----------

    def activate(
        self,
        license_key: str,
        *,
        current_version: Optional[str] = None,
        package_name: Optional[str] = None,
        timeout: float = 8.0,
    ):
        """
        手动调用激活：
        - license_key: 激活码
        - current_version: 当前 SDK/壳的版本号（不传则使用 self.version()）
        - package_name: 产品名（不传则在 license_core 里用默认的 weixinauto）
        """
        current_version = current_version or self.version()

        ok, update_info = self._license_mgr.activate_with_server(
            license_key=license_key,
            package_name=package_name,
            current_version=current_version,
            timeout=timeout,
        )
        if ok:
            # 激活成功后，重新创建 driver（这时候已经有 license 了）
            self._driver = self._license_mgr.create_wechat_driver(silent=False)
            print("[Wechat] 激活成功，核心已就绪。")
        return ok, update_info

    # ---------- 登录相关（先占位） ----------

    def is_logged_in(self) -> bool:
        """
        这里先简单一点：
        - 确保 driver 存在
        - 后续如果 WeChatDriver 有专门的 is_logged_in，可以在这里调用它
        """
        if not self._ensure_driver():
            return False
        print("微信启动成功")
        return True

    # ---------- 窗口操作 ----------

    def open_or_focus_child_window(self, title: str) -> bool:
        """
        打开或聚焦一个指定标题的聊天窗口。
        如果子窗口已经打开，则激活并前置；否则尝试打开它。
        """
        if not self._ensure_driver():
            return False
        return self._driver.ensure_chat_window_open_fast(title)

    # ---------- 单个窗口监听（ChatWindowListener 模式） ----------

    def add_listen_chat(
        self,
        title: str,
        on_new: Callable[..., None],
        *,
        interval_sec: float = 0.18,
        need_nickname: bool = False,
    ) -> bool:
        """
        监听【单个】聊天窗口。
        - title: 会话标题（群名/好友昵称）
        - on_new: 回调函数，推荐签名为 on_new(group: str, msg: ChatMessage, reply_callable)
        - interval_sec: 轮询间隔
        - need_nickname: 是否需要通过点击头像获取昵称
        """
        title = (title or "").strip()
        if not title:
            return False

        if not self._ensure_driver():
            print(f"[add_listen_chat] 当前设备未激活，无法监听窗口：{title!r}")
            return False

        # 确保子窗口已打开
        if not self.open_or_focus_child_window(title):
            print(f"[add_listen_chat] 无法打开/激活窗口：{title!r}")
            return False

        # 如果该 title 已经有监听器，先停掉旧的
        old = self._single_listeners.get(title)
        if old and old.is_alive():
            old.stop()

        # 创建并启动新的监听线程
        listener = ChatWindowListener(
            title,
            on_message=on_new,
            driver=self._driver,
            need_nickname=need_nickname,
            poll_sec=interval_sec,
        )
        listener.start()
        self._single_listeners[title] = listener
        return True

    # ---------- 批量窗口监听（MultiChatManager 模式） ----------

    def add_listens(
        self,
        titles: Iterable[str],
        *,
        need_nickname: bool = True,
        poll_sec: float = 0.15,
    ) -> None:
        """
        动态添加批量监听窗口（依赖 MultiChatManager）：
        1. 先一个个尝试打开聊天子窗口
        2. 打开成功的才交给 MultiChatManager 做监听
        """
        if not titles:
            return

        if not self._ensure_driver():
            print("[add_listens] 当前设备未激活，无法添加监听。")
            return

        normalized: List[str] = []
        for t in titles:
            name = (t or "").strip()
            if not name:
                continue

            try:
                ok = self._driver.ensure_chat_window_open_fast(name, fuzzy=False)
            except Exception as e:
                print(f"[add_listens] 打开会话窗口 {name!r} 失败: {e}")
                ok = False

            if not ok:
                print(f"[add_listens] 跳过未能成功打开的会话：{name!r}")
                continue

            normalized.append(name)

        if not normalized:
            print("[add_listens] 没有任何会话成功打开，未添加监听。")
            return

        # 第一次：创建 MultiChatManager
        if self._multi_manager is None:
            self._multi_manager = MultiChatManager(
                titles=normalized,
                on_message=None,   # 如需回调，可以替换成你自己的函数
                driver=self._driver,
                need_nickname=need_nickname,
                poll_sec=poll_sec,
            )
        else:
            # 后续：追加监听会话
            self._multi_manager.add_listens(
                normalized,
                need_nickname=need_nickname,
                poll_sec=poll_sec,
            )

    # ---------- 启停监听 ----------

    def start_listen(self) -> None:
        """统一启动所有监听线程（单个 + 批量）"""
        # 启动单窗口监听器
        for ls in self._single_listeners.values():
            if not ls.is_alive():
                ls.start()
        # 启动批量监听器
        if self._multi_manager:
            self._multi_manager.start_all()

    def stop_listen(
        self,
        title: Optional[str] = None,
        *,
        join: bool = True,
        timeout: float = 1.5,
    ) -> None:
        """
        停止监听：
        - title 有值：仅停止该 title 的单个监听（add_listen_chat 创建的）
        - title 为空：停止所有单个监听 + 所有批量监听
        """
        # 1) 处理单窗口监听器
        if title:
            t = (title or "").strip()
            ls = self._single_listeners.pop(t, None)
            if ls:
                ls.stop()
                if join:
                    ls.join(timeout=timeout)
        else:
            # 停止所有单窗口监听
            for ls in self._single_listeners.values():
                ls.stop()
            if join:
                for ls in self._single_listeners.values():
                    ls.join(timeout=timeout)
            self._single_listeners.clear()

        # 2) 处理 MultiChatManager（只在 title 为空时整体停）
        if not title and self._multi_manager:
            self._multi_manager.stop_all(join=join, timeout=timeout)

    # ---------- 消息获取（批量监听模式专用） ----------

    def get_listen_messages(self, clear: bool = True) -> Dict[ChatWnd, List[ChatMessage]]:
        """
        获取 MultiChatManager 模式下所有监听窗口的新消息：
        返回结构：
            { ChatWnd(title='工作群'): [ChatMessage, ...], ... }
        clear=True 表示取出后清空内部队列
        """
        if not self._multi_manager:
            return {}
        return self._multi_manager.get_listen_messages(clear=clear)

    def get_listen_message(self, clear: bool = True) -> Dict[str, List[ChatMessage]]:
        """
        如果你外面不想处理 ChatWnd 对象，可以用这个：
        直接把 key 换成群名字符串。
        """
        raw = self.get_listen_messages(clear=clear)
        return {cw.title: msgs for cw, msgs in raw.items()}

    # ---------- 发送消息 ----------

    def send_message(
        self,
        target: str,
        text: str,
        *,
        wait_seconds: float = 1.6,
        debug: bool = False,
    ) -> bool:
        """
        向指定聊天窗口发送文本消息。
        """
        if not self._ensure_driver():
            print("[send_message] 当前设备未激活，无法发送消息。")
            return False

        return self._driver.send_text_to_chat(
            chat_name=target,
            text=text,
            strict=False,
            wait_child_sec=wait_seconds,
            wait_btn_sec=1.2,
        )

    # ---------- 内部 ----------

    def shutdown(self) -> None:
        # 先停监听
        self.stop_listen()
        if self._driver and hasattr(self._driver, "shutdown"):
            try:
                self._driver.shutdown()
            except Exception:
                pass

    def version(self) -> str:
        """
        壳的版本号，可以在发布 PyPI 时同步更新。
        这里先写一个固定值，后续你要的话可以挪到单独的 version.py 里。
        """
        return "0.1.0"
