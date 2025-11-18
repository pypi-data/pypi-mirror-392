from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .AuthDetailsRepresentation import AuthDetailsRepresentation


@dataclass
class AdminEventRepresentation:
    """
    AdminEventRepresentation
    """
    time: int = None
    realm_id: str = None
    auth_details: AuthDetailsRepresentation = None
    operation_type: str = None
    resource_type: str = None
    resource_path: str = None
    representation: str = None
    error: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AdminEventRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'auth_details' in snake_data and snake_data['auth_details'] is not None:
            snake_data['auth_details'] = AuthDetailsRepresentation.from_dict(snake_data['auth_details'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
