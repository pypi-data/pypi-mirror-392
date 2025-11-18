from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .MethodConfig import MethodConfig
from .EnforcementMode import EnforcementMode


@dataclass
class PathConfig:
    """
    PathConfig
    """
    name: str = None
    type: str = None
    path: str = None
    methods: List[MethodConfig] = None
    scopes: List[str] = None
    id: str = None
    enforcement_mode: EnforcementMode = None
    claim_information_point: dict = None
    invalidated: bool = None
    static_path: bool = None
    static: bool = None

    @classmethod
    def from_dict(cls, data: dict) -> 'PathConfig':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'methods' in snake_data and snake_data['methods'] is not None:
            snake_data['methods'] = [MethodConfig.from_dict(item) for item in snake_data['methods']]
        if 'enforcement_mode' in snake_data and snake_data['enforcement_mode'] is not None:
            snake_data['enforcement_mode'] = EnforcementMode.from_dict(snake_data['enforcement_mode'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
