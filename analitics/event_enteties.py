from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class BaseEvent:
    user_id: int
    event_name: str
    properties:  Optional[dict] = None

    def dict(self):
        return asdict(self)


@dataclass
class UserEvent:
    user_id: int
    first_name: str
    last_name: str
    tg_link: str
    other_properties: Optional[dict]

    def dict(self):
        return asdict(self)