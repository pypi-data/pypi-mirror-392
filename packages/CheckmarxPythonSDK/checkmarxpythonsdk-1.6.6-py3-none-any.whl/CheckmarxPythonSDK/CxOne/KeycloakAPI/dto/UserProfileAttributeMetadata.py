from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class UserProfileAttributeMetadata:
    """
    UserProfileAttributeMetadata
    """
    name: str = None
    display_name: str = None
    required: bool = None
    read_only: bool = None
    annotations: dict = None
    validators: dict = None
    group: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'UserProfileAttributeMetadata':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
