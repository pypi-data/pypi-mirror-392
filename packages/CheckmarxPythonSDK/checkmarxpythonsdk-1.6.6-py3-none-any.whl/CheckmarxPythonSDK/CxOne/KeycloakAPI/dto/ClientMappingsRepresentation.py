from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .RoleRepresentation import RoleRepresentation


@dataclass
class ClientMappingsRepresentation:
    """
    ClientMappingsRepresentation
    """
    id: str = None
    client: str = None
    mappings: List[RoleRepresentation] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ClientMappingsRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'mappings' in snake_data and snake_data['mappings'] is not None:
            snake_data['mappings'] = [RoleRepresentation.from_dict(item) for item in snake_data['mappings']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
