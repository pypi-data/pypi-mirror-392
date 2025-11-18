from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .PolicyRepresentation import PolicyRepresentation
from .ResourceRepresentation import ResourceRepresentation


@dataclass
class ScopeRepresentation:
    """
    ScopeRepresentation
    """
    id: str = None
    name: str = None
    icon_uri: str = None
    policies: List[PolicyRepresentation] = None
    resources: List[ResourceRepresentation] = None
    display_name: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ScopeRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'policies' in snake_data and snake_data['policies'] is not None:
            snake_data['policies'] = [PolicyRepresentation.from_dict(item) for item in snake_data['policies']]
        if 'resources' in snake_data and snake_data['resources'] is not None:
            snake_data['resources'] = [ResourceRepresentation.from_dict(item) for item in snake_data['resources']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
