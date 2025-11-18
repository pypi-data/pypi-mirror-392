# infra/uia/selectors/resolver.py
from __future__ import annotations
import json, os, re, time
from collections import deque
from typing import Any, Dict, List, Optional, Callable
import uiautomation as uia
import importlib.resources as ir

class VersionError(RuntimeError): ...
class SelectorNotFound(KeyError): ...
class StrategyBuildError(RuntimeError): ...

def is_supported_version_str(ver: str) -> bool:
    m = re.match(r"^(\d+)\.(\d+)", str(ver).strip())
    if not m: return False
    major, minor = int(m.group(1)), int(m.group(2))
    return (major > 4) or (major == 4 and minor >= 1)

class SelectorResolver:
    """
    解析 + 执行 + 便捷封装，一站式使用：
      - get(logical)              -> 策略链（原样）
      - find_one / resolve_one    -> 执行策略链，取首个命中
      - resolve_all               -> 执行策略链，取一组命中（适用于列表/消息等）
      - wait_for                  -> 在超时内等待某 logical 出现
      - clear_cache               -> 清理定位缓存
    同时内置常用控件便捷方法与候选列表（联系人+群聊）解析。
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None, path: Optional[str] = None):
        if data is None:
            if path:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                # 自动从包内资源加载（weixinauto/infra/uia/selectors/wechat_4_1_plus.json）
                try:
                    txt = ir.files("weixinauto.infra.uia.selectors").joinpath("wechat_4_1_plus.json").read_text(encoding="utf-8")
                    data = json.loads(txt)
                except Exception as e:
                    raise FileNotFoundError("无法加载内置选择器 JSON：weixinauto/infra/uia/selectors/wechat_4_1_plus.json") from e

        self._doc: Dict[str, Any] = data
        self._globals: Dict[str, Any] = self._doc.get("globals", {})
        self._selectors: Dict[str, Any] = self._doc.get("selectors", {})
        self._range = self._doc.get("version_range", ">=4.1")
        self._locale = self._globals.get("locale_names", {})
        self._timeouts = self._globals.get("timeouts", {})
        self._cache: Dict[str, uia.Control] = {}

        self._ctype_map = {
            "Window": "WindowControl",
            "Group":  "GroupControl",
            "Edit":   "EditControl",
            "Button": "ButtonControl",
            "List":   "ListControl",
            "ListItem": "ListItemControl",
            "Pane":   "PaneControl",
            "Text":   "TextControl",
            "ToolBar":"ToolBarControl",
        }

    # ========== 公共 API ==========
    def clear_cache(self):
        self._cache.clear()

    def get(self, logical_name: str, **vars) -> List[Dict[str, Any]]:
        node = self._selectors.get(logical_name)
        if not node:
            raise SelectorNotFound(logical_name)
        strategies = node.get("strategies", [])
        built: List[Dict[str, Any]] = []
        for s in strategies:
            built.append(self._build_strategy(s, **vars))
        return built

    # 兼容老签名
    def find_one(self, logical_name: str, *, root: Optional[uia.Control] = None, **vars) -> Optional[uia.Control]:
        return self.resolve_one(logical_name, root=root, **vars)

    def resolve_one(self, logical_name: str, *, root: Optional[uia.Control] = None, **vars) -> Optional[uia.Control]:
        """
        执行策略链，返回第一个命中的控件；带活性校验与缓存。
        """
        cached = self._cache.get(logical_name)
        if self._is_alive(cached):
            return cached

        try:
            strategies = self.get(logical_name, **vars)
        except SelectorNotFound:
            return None

        main = root or self._default_root()
        end_node = None
        for s in strategies:
            node = self._exec_strategy(s, main)
            if self._is_alive(node):
                end_node = node
                break

        if self._is_alive(end_node):
            self._cache[logical_name] = end_node
        return end_node

    def resolve_all(self, logical_name: str, *, root: Optional[uia.Control] = None, **vars) -> List[uia.Control]:
        """
        执行策略链，返回首个命中的“结果集合”（适配 control/path 两类）。
        """
        try:
            strategies = self.get(logical_name, **vars)
        except SelectorNotFound:
            return []
        main = root or self._default_root()
        for s in strategies:
            arr = self._exec_strategy_all(s, main)
            if arr:
                return arr
        return []

    def wait_for(
        self,
        logical_name: str,
        *,
        root: Optional[uia.Control] = None,
        timeout: float = 2.0,
        **vars
    ) -> Optional[uia.Control]:
        """
        在超时内等待某 logical 命中。
        """
        end = time.time() + max(0.05, timeout)
        while time.time() < end:
            ctl = self.resolve_one(logical_name, root=root, **vars)
            if self._is_alive(ctl):
                return ctl
            time.sleep(0.05)
        return None

    # ========== 便捷方法（主窗 / 搜索框 / 输入框 / 发送按钮） ==========
    def get_main_window(self) -> Optional[uia.Control]:
        return self.resolve_one("MAIN_WINDOW")

    def get_chat_search_box(self, *, root: Optional[uia.Control] = None) -> Optional[uia.Control]:
        main = root or self.get_main_window()
        if not main: return None
        return self.resolve_one("CHAT_SEARCH_BOX", root=main)

    def get_chat_input(self, *, root: Optional[uia.Control] = None) -> Optional[uia.Control]:
        main = root or self.get_main_window()
        if not main: return None
        return self.resolve_one("CHAT_INPUT", root=main)

    def get_send_button(self, *, root: Optional[uia.Control] = None) -> Optional[uia.Control]:
        main = root or self.get_main_window()
        if not main: return None
        return self.resolve_one("SEND_BUTTON", root=main)

    # ========== 搜索候选列表（联系人 + 群聊） ==========
    def find_search_list(self, *, root: Optional[uia.Control] = None) -> Optional[uia.Control]:
        """
        在 MainWindow 下定位搜索候选列表：ClassName='mmui::XTableView', AutomationId='search_list'
        """
        main = root or self.get_main_window()
        if not main: return None

        def _pred(n: uia.Control) -> bool:
            try:
                if getattr(n, "ControlTypeName", "") != "ListControl":
                    return False
                if getattr(n, "ClassName", "") != "mmui::XTableView":
                    return False
                if getattr(n, "AutomationId", "") != "search_list":
                    return False
                return True
            except Exception:
                return False

        return self._find_descendant(main, _pred, max_nodes=12000)

    def wait_search_list_ready(self, *, root: Optional[uia.Control] = None, timeout: float = 0.8) -> bool:
        end = time.time() + max(0.1, timeout)
        while time.time() < end:
            lst = self.find_search_list(root=root)
            if lst:
                try:
                    kids = lst.GetChildren()
                    if kids and len(kids) > 0:
                        return True
                except Exception:
                    return True  # 列表已出现但枚举失败，也算 ready
            time.sleep(0.03)
        return False

    def collect_candidates_both_sections(self, *, root: Optional[uia.Control] = None) -> List[str]:
        """
        解析候选列表，合并“联系人”与“群聊”两段的可点项，去除“查看全部…”类目。
        返回：按候选顺序的名称集合。
        """
        lst = self.find_search_list(root=root)
        if not lst:
            return []

        # 拉平可见项名称
        raw_items: List[str] = []
        try:
            for node in lst.GetChildren() or []:
                if getattr(node, "ControlTypeName", "") != "ListItemControl":
                    continue
                nm = (getattr(node, "Name", "") or "").strip()
                if not nm:
                    # 再从 TextControl 兜底
                    try:
                        for ch in node.GetChildren() or []:
                            if getattr(ch, "ControlTypeName", "") == "TextControl":
                                t = (getattr(ch, "Name", "") or "").strip()
                                if t:
                                    nm = t
                                    break
                    except Exception:
                        pass
                raw_items.append(nm)
        except Exception:
            pass

        if not raw_items:
            return []

        # 分段提取：联系人 + 群聊
        out: List[str] = []
        in_contacts = in_groups = False
        for nm in raw_items:
            if not nm:
                continue
            if nm == "联系人":
                in_contacts, in_groups = True, False
                continue
            if nm == "群聊":
                in_contacts, in_groups = False, True
                continue
            if nm in ("服务号", "聊天记录"):
                # 到了后面的分区，结束
                if in_contacts or in_groups:
                    break
            if (in_contacts or in_groups) and not nm.startswith("查看全部"):
                out.append(nm)
        return out

    # ========== 构建策略 ==========
    def _build_strategy(self, s: Dict[str, Any], **vars) -> Dict[str, Any]:
        def subst_value(v):
            if isinstance(v, str):
                try:
                    v2 = v.format(**vars)
                except KeyError:
                    v2 = v
                if v2.startswith("@"):
                    if v2.startswith("@timeouts."):
                        key = v2.split(".", 1)[1]
                        return float(self._timeouts.get(key, 1.5))
                    key = v2[1:]
                    arr = self._locale.get(key)
                    if arr: return arr
                return v2
            elif isinstance(v, list):
                return [subst_value(x) for x in v]
            elif isinstance(v, dict):
                return {k: subst_value(val) for k, val in v.items()}
            else:
                return v

        out = {k: subst_value(v) for k, v in s.items()}
        if "by" not in out:
            raise StrategyBuildError(f"strategy missing 'by': {s}")
        if "timeout" in out:
            out["timeout"] = float(out["timeout"])
        return out

    # ========== 策略执行 ==========
    def _exec_strategy(self, s: Dict[str, Any], main: uia.Control) -> Optional[uia.Control]:
        by = s.get("by")
        timeout = float(s.get("timeout", 0.6))
        deadline = time.time() + max(0.05, timeout)

        _norm = self._norm_type
        _bfs  = self._iter_bfs
        _ok_name_in = self._name_in_ok

        # window
        if by == "window":
            class_name = s.get("class_name")
            name_in = s.get("name_in")
            while time.time() < deadline:
                root = uia.GetRootControl()
                for n in _bfs(root, 18000):
                    if getattr(n, "ControlTypeName", "") != "WindowControl":
                        continue
                    if class_name and getattr(n, "ClassName", "") != class_name:
                        continue
                    if not _ok_name_in(n, name_in):
                        continue
                    return n
                time.sleep(0.03)
            return None

        # control
        if by == "control":
            ctype = _norm(s.get("control_type", ""))
            expect = {
                "ControlTypeName": ctype or None,
                "ClassName": s.get("class_name"),
                "AutomationId": s.get("automation_id"),
                "Name": s.get("name"),
            }
            expect = {k: v for k, v in expect.items() if v}
            name_in = s.get("name_in")
            while time.time() < deadline:
                for n in _bfs(main, 8000):
                    if not self._match_attrs(n, expect):
                        continue
                    if not _ok_name_in(n, name_in):
                        continue
                    return n
                time.sleep(0.03)
            return None

        # near_text
        if by == "near_text":
            anchor_in = s.get("anchor_in")
            tgt_type  = _norm(s.get("control_type", ""))
            while time.time() < deadline:
                anchors = [n for n in _bfs(main, 6000)
                           if getattr(n, "ControlTypeName", "") == "TextControl" and _ok_name_in(n, anchor_in)]
                for a in anchors:
                    parent = a.GetParentControl()
                    # 先从同级找
                    for sib in self._children_safe(parent):
                        if getattr(sib, "ControlTypeName", "") == tgt_type:
                            return sib
                    # 再扩大一层上下文
                    p2 = parent.GetParentControl() if parent else None
                    ctx = p2 or parent or main
                    for n in _bfs(ctx, 2500):
                        if getattr(n, "ControlTypeName", "") == tgt_type:
                            return n
                time.sleep(0.03)
            return None

        # path
        if by == "path":
            seq = s.get("path", [])
            cur = main
            ok = True
            for hop in seq:
                hop_type = _norm(hop.get("control_type", ""))
                hop_expect = {
                    "ControlTypeName": hop_type or None,
                    "ClassName": hop.get("class_name"),
                    "AutomationId": hop.get("automation_id"),
                    "Name": hop.get("name"),
                }
                hop_expect = {k: v for k, v in hop_expect.items() if v}
                next_cur = None
                for ch in _bfs(cur, 2500):
                    if self._match_attrs(ch, hop_expect):
                        next_cur = ch; break
                if not next_cur:
                    ok = False; break
                cur = next_cur
            # 尾节点附加 name/name_in/regex 过滤（若配置）
            if ok and cur:
                nm = (cur.Name or "").strip()
                if not self._extra_name_filter(nm, s):
                    return None
            return cur if ok and self._is_alive(cur) else None

        # list_item：用于搜索候选中的命中项（若有）
        if by == "list_item":
            ctype = _norm(s.get("control_type", "ListItem"))
            name = s.get("name")
            name_regex = s.get("name_regex")
            child_text_regex = s.get("child_text_regex")
            re_name  = re.compile(name_regex) if name_regex else None
            re_child = re.compile(child_text_regex) if child_text_regex else None

            def _hit(n) -> bool:
                if getattr(n, "ControlTypeName", "") != ctype:
                    return False
                nm = (n.Name or "")
                if name and nm == name:
                    return True
                if re_name and re_name.match(nm or ""):
                    return True
                if re_child:
                    for ch in self._children_safe(n):
                        if getattr(ch, "ControlTypeName", "") == "TextControl" and re_child.match(ch.Name or ""):
                            return True
                return False

            while time.time() < deadline:
                for n in _bfs(main, 6000):
                    if _hit(n):
                        return n
                time.sleep(0.03)
            return None

        # 其它 by 可按需扩展
        return None

    def _exec_strategy_all(self, s: Dict[str, Any], main: uia.Control) -> List[uia.Control]:
        by = s.get("by")
        if by not in ("control", "path"):
            return []
        _norm = self._norm_type
        _bfs  = self._iter_bfs

        if by == "control":
            ctype = _norm(s.get("control_type", ""))
            expect = {
                "ControlTypeName": ctype or None,
                "ClassName": s.get("class_name"),
                "AutomationId": s.get("automation_id"),
                "Name": s.get("name"),
            }
            expect = {k: v for k, v in expect.items() if v}
            name_in = s.get("name_in")

            out: List[uia.Control] = []
            for n in _bfs(main, 12000):
                if not self._match_attrs(n, expect):
                    continue
                if not self._name_in_ok(n, name_in):
                    continue
                out.append(n)
            return out

        if by == "path":
            # path/all 的需求较少，先返回尾节点单个（如需真正 all，可在此扩展）
            hit = self._exec_strategy(s, main)
            return [hit] if hit else []

        return []
    def iter_bfs(self, root: uia.Control, max_nodes: int = 6000):
        """对外暴露的 BFS 迭代器（避免重复造轮子）"""
        yield from self._iter_bfs(root, max_nodes)

    def first_match(self, root: uia.Control, predicate, max_nodes: int = 6000) -> Optional[uia.Control]:
        """从 root 开始 BFS，返回首个满足 predicate 的节点"""
        for n in self._iter_bfs(root, max_nodes):
            try:
                if predicate(n):
                    return n
            except Exception:
                pass
        return None

    def find_children(self, root: uia.Control, *, control_type: str = "", class_name: str = "", automation_id: str = "", name: str = "", max_nodes: int = 6000) -> list:
        """轻量过滤，返回满足基本属性的所有子节点"""
        ct = self._ctype_map.get(control_type, control_type) if control_type else ""
        out = []
        for n in self._iter_bfs(root, max_nodes):
            try:
                if ct and getattr(n, "ControlTypeName", "") != ct:
                    continue
                if class_name and getattr(n, "ClassName", "") != class_name:
                    continue
                if automation_id and getattr(n, "AutomationId", "") != automation_id:
                    continue
                if name and (n.Name or "") != name:
                    continue
                out.append(n)
            except Exception:
                pass
        return out

    # ========== 工具 ==========
    @staticmethod
    def _default_root() -> uia.Control:
        return uia.GetRootControl()

    def _norm_type(self, t: str) -> str:
        return self._ctype_map.get(t, t)

    @staticmethod
    def _is_alive(ctrl: Optional[uia.Control]) -> bool:
        if not ctrl: return False
        try:
            _ = ctrl.BoundingRectangle
            return ctrl.Exists(0, 0)
        except Exception:
            return False

    @staticmethod
    def _children_safe(node) -> List[uia.Control]:
        try:
            return node.GetChildren()
        except Exception:
            return []

    def _iter_bfs(self, root: uia.Control, max_nodes=6000):
        q = deque([root]); seen = 0
        while q and seen < max_nodes:
            n = q.popleft(); seen += 1
            yield n
            try:
                ch = n.GetChildren()
                if ch:
                    q.extend(ch)
            except Exception:
                pass

    @staticmethod
    def _name_in_ok(node, arr: Optional[List[str]]) -> bool:
        if not arr: return True
        nm = (node.Name or "")
        # 支持“包含”判断（为兼容「搜索」「Search」这类多语言前缀）
        return any((k in nm) for k in arr)

    @staticmethod
    def _match_attrs(node, expect: Dict[str, Any]) -> bool:
        try:
            if "ControlTypeName" in expect and getattr(node, "ControlTypeName", "") != expect["ControlTypeName"]:
                return False
            if "ClassName" in expect and getattr(node, "ClassName", "") != expect["ClassName"]:
                return False
            if "AutomationId" in expect and getattr(node, "AutomationId", "") != expect["AutomationId"]:
                return False
            if "Name" in expect and (node.Name or "") != expect["Name"]:
                return False
            return True
        except Exception:
            return False

    @staticmethod
    def _extra_name_filter(name: str, s: Dict[str, Any]) -> bool:
        eq = s.get("name")
        in_list = s.get("name_in")
        regex = s.get("name_regex")
        if eq is not None and name != eq:
            return False
        if in_list and name not in in_list:
            return False
        if regex:
            try:
                if not re.search(regex, name):
                    return False
            except re.error:
                return False
        return True
