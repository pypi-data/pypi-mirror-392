from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .Composites import Composites


@dataclass
class RoleRepresentation:
    """
    RoleRepresentation
    """
    id: str = None
    name: str = None
    description: str = None
    scope_param_required: bool = None
    composite: bool = None
    composites: Composites = None
    client_role: bool = None
    container_id: str = None
    attributes: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RoleRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'composites' in snake_data and snake_data['composites'] is not None:
            snake_data['composites'] = Composites.from_dict(snake_data['composites'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
