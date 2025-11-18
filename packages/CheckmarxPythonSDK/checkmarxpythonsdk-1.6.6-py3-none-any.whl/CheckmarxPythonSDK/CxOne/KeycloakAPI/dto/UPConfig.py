from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .UPAttribute import UPAttribute
from .UPGroup import UPGroup


@dataclass
class UPConfig:
    """
    UPConfig
    """
    attributes: List[UPAttribute] = None
    groups: List[UPGroup] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'UPConfig':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'attributes' in snake_data and snake_data['attributes'] is not None:
            snake_data['attributes'] = [UPAttribute.from_dict(item) for item in snake_data['attributes']]
        if 'groups' in snake_data and snake_data['groups'] is not None:
            snake_data['groups'] = [UPGroup.from_dict(item) for item in snake_data['groups']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
