from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .ConfigPropertyRepresentation import ConfigPropertyRepresentation


@dataclass
class AuthenticatorConfigInfoRepresentation:
    """
    AuthenticatorConfigInfoRepresentation
    """
    name: str = None
    provider_id: str = None
    help_text: str = None
    properties: List[ConfigPropertyRepresentation] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AuthenticatorConfigInfoRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'properties' in snake_data and snake_data['properties'] is not None:
            snake_data['properties'] = [ConfigPropertyRepresentation.from_dict(item) for item in snake_data['properties']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
