from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class RequiredActionProviderRepresentation:
    """
    RequiredActionProviderRepresentation
    """
    alias: str = None
    name: str = None
    provider_id: str = None
    enabled: bool = None
    default_action: bool = None
    priority: int = None
    config: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RequiredActionProviderRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
