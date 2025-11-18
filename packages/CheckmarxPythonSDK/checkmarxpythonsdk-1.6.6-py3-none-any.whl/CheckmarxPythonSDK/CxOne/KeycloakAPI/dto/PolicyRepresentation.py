from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .Logic import Logic
from .DecisionStrategy import DecisionStrategy
from .ResourceRepresentation import ResourceRepresentation
from .ScopeRepresentation import ScopeRepresentation


@dataclass
class PolicyRepresentation:
    """
    PolicyRepresentation
    """
    id: str = None
    name: str = None
    description: str = None
    type: str = None
    policies: List[str] = None
    resources: List[str] = None
    scopes: List[str] = None
    logic: Logic = None
    decision_strategy: DecisionStrategy = None
    owner: str = None
    resources_data: List[ResourceRepresentation] = None
    scopes_data: List[ScopeRepresentation] = None
    config: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> 'PolicyRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'logic' in snake_data and snake_data['logic'] is not None:
            snake_data['logic'] = Logic.from_dict(snake_data['logic'])
        if 'decision_strategy' in snake_data and snake_data['decision_strategy'] is not None:
            snake_data['decision_strategy'] = DecisionStrategy.from_dict(snake_data['decision_strategy'])
        if 'resources_data' in snake_data and snake_data['resources_data'] is not None:
            snake_data['resources_data'] = [ResourceRepresentation.from_dict(item) for item in snake_data['resources_data']]
        if 'scopes_data' in snake_data and snake_data['scopes_data'] is not None:
            snake_data['scopes_data'] = [ScopeRepresentation.from_dict(item) for item in snake_data['scopes_data']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
