from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class ConfigPropertyRepresentation:
    """
    ConfigPropertyRepresentation
    """
    name: str = None
    label: str = None
    help_text: str = None
    type: str = None
    default_value: dict = None
    options: List[str] = None
    secret: bool = None
    required: bool = None
    read_only: bool = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ConfigPropertyRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
