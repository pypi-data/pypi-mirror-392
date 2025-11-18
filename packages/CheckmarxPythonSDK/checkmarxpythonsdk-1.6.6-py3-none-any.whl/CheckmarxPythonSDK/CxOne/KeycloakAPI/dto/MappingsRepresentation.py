from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .RoleRepresentation import RoleRepresentation


@dataclass
class MappingsRepresentation:
    """
    MappingsRepresentation
    """
    realm_mappings: List[RoleRepresentation] = None
    client_mappings: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> 'MappingsRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'realm_mappings' in snake_data and snake_data['realm_mappings'] is not None:
            snake_data['realm_mappings'] = [RoleRepresentation.from_dict(item) for item in snake_data['realm_mappings']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
