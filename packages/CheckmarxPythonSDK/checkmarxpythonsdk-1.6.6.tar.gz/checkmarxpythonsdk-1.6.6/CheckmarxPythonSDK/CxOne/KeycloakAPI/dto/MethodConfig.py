from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .ScopeEnforcementMode import ScopeEnforcementMode


@dataclass
class MethodConfig:
    """
    MethodConfig
    """
    method: str = None
    scopes: List[str] = None
    scopes_enforcement_mode: ScopeEnforcementMode = None

    @classmethod
    def from_dict(cls, data: dict) -> 'MethodConfig':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'scopes_enforcement_mode' in snake_data and snake_data['scopes_enforcement_mode'] is not None:
            snake_data['scopes_enforcement_mode'] = ScopeEnforcementMode.from_dict(snake_data['scopes_enforcement_mode'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
