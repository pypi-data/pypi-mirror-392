from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class UserSessionRepresentation:
    """
    UserSessionRepresentation
    """
    id: str = None
    username: str = None
    user_id: str = None
    ip_address: str = None
    start: int = None
    last_access: int = None
    remember_me: bool = None
    clients: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> 'UserSessionRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
