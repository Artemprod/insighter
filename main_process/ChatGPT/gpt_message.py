from dataclasses import dataclass
from enum import Enum


class GPTRole(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


@dataclass
class GPTMessage:
    role: GPTRole
    content: str
