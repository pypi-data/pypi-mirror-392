# weixinauto/infra/uia/message.pyi
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class ChatMessage:
    group: str
    text: str
    ts: float
    mtype: str
    raw_text: Optional[str]
    is_self: Optional[bool]
    sender: Optional[str]
    internal_tag: Optional[str]
