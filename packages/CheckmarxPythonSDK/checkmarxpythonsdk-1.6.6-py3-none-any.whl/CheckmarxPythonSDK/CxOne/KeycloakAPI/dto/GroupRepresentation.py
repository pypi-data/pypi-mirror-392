from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .GroupRepresentation import GroupRepresentation


@dataclass
class GroupRepresentation:
    """
    GroupRepresentation
    """
    id: str = None
    name: str = None
    path: str = None
    parent_id: str = None
    sub_group_count: int = None
    sub_groups: List[GroupRepresentation] = None
    attributes: dict = None
    realm_roles: List[str] = None
    client_roles: dict = None
    access: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> 'GroupRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'sub_groups' in snake_data and snake_data['sub_groups'] is not None:
            snake_data['sub_groups'] = [GroupRepresentation.from_dict(item) for item in snake_data['sub_groups']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
