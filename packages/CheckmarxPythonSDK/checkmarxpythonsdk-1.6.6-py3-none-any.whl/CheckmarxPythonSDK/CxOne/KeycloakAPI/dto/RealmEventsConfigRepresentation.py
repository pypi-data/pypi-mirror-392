from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class RealmEventsConfigRepresentation:
    """
    RealmEventsConfigRepresentation
    """
    events_enabled: bool = None
    events_expiration: int = None
    events_listeners: List[str] = None
    enabled_event_types: List[str] = None
    admin_events_enabled: bool = None
    admin_events_details_enabled: bool = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RealmEventsConfigRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
