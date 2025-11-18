from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .ScopeRepresentation import ScopeRepresentation
from .ResourceRepresentationOwner import ResourceRepresentationOwner
from .ScopeRepresentation import ScopeRepresentation


@dataclass
class ResourceRepresentation:
    """
    ResourceRepresentation
    """
    id: str = None
    name: str = None
    uris: List[str] = None
    type: str = None
    scopes: List[ScopeRepresentation] = None
    icon_uri: str = None
    owner: ResourceRepresentationOwner = None
    owner_managed_access: bool = None
    display_name: str = None
    attributes: dict = None
    uri: str = None
    scopes_uma: List[ScopeRepresentation] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ResourceRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'scopes' in snake_data and snake_data['scopes'] is not None:
            snake_data['scopes'] = [ScopeRepresentation.from_dict(item) for item in snake_data['scopes']]
        if 'owner' in snake_data and snake_data['owner'] is not None:
            snake_data['owner'] = ResourceRepresentationOwner.from_dict(snake_data['owner'])
        if 'scopes_uma' in snake_data and snake_data['scopes_uma'] is not None:
            snake_data['scopes_uma'] = [ScopeRepresentation.from_dict(item) for item in snake_data['scopes_uma']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
