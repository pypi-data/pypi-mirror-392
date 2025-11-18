from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .RoleRepresentation import RoleRepresentation


@dataclass
class RolesRepresentation:
    """
    RolesRepresentation
    """
    realm: List[RoleRepresentation] = None
    client: dict = None
    application: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RolesRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'realm' in snake_data and snake_data['realm'] is not None:
            snake_data['realm'] = [RoleRepresentation.from_dict(item) for item in snake_data['realm']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
