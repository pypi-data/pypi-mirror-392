from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class EventRepresentation:
    """
    EventRepresentation
    """
    time: int = None
    type: str = None
    realm_id: str = None
    client_id: str = None
    user_id: str = None
    session_id: str = None
    ip_address: str = None
    error: str = None
    details: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> 'EventRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
