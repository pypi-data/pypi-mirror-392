from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .KeyMetadataRepresentation import KeyMetadataRepresentation


@dataclass
class KeysMetadataRepresentation:
    """
    KeysMetadataRepresentation
    """
    active: dict = None
    keys: List[KeyMetadataRepresentation] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'KeysMetadataRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'keys' in snake_data and snake_data['keys'] is not None:
            snake_data['keys'] = [KeyMetadataRepresentation.from_dict(item) for item in snake_data['keys']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
