from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .UPAttributeRequired import UPAttributeRequired
from .UPAttributePermissions import UPAttributePermissions
from .UPAttributeSelector import UPAttributeSelector


@dataclass
class UPAttribute:
    """
    UPAttribute
    """
    name: str = None
    display_name: str = None
    validations: dict = None
    annotations: dict = None
    required: UPAttributeRequired = None
    permissions: UPAttributePermissions = None
    selector: UPAttributeSelector = None
    group: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'UPAttribute':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'required' in snake_data and snake_data['required'] is not None:
            snake_data['required'] = UPAttributeRequired.from_dict(snake_data['required'])
        if 'permissions' in snake_data and snake_data['permissions'] is not None:
            snake_data['permissions'] = UPAttributePermissions.from_dict(snake_data['permissions'])
        if 'selector' in snake_data and snake_data['selector'] is not None:
            snake_data['selector'] = UPAttributeSelector.from_dict(snake_data['selector'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
