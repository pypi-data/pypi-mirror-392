from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class ClaimRepresentation:
    """
    ClaimRepresentation
    """
    name: bool = None
    username: bool = None
    profile: bool = None
    picture: bool = None
    website: bool = None
    email: bool = None
    gender: bool = None
    locale: bool = None
    address: bool = None
    phone: bool = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ClaimRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
