from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .KeyUse import KeyUse


@dataclass
class KeyMetadataRepresentation:
    """
    KeyMetadataRepresentation
    """
    provider_id: str = None
    provider_priority: int = None
    kid: str = None
    status: str = None
    type: str = None
    algorithm: str = None
    public_key: str = None
    certificate: str = None
    use: KeyUse = None
    valid_to: int = None

    @classmethod
    def from_dict(cls, data: dict) -> 'KeyMetadataRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'use' in snake_data and snake_data['use'] is not None:
            snake_data['use'] = KeyUse.from_dict(snake_data['use'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
