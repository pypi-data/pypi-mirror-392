from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .PolicyEnforcementMode import PolicyEnforcementMode
from .ResourceRepresentation import ResourceRepresentation
from .PolicyRepresentation import PolicyRepresentation
from .ScopeRepresentation import ScopeRepresentation
from .DecisionStrategy import DecisionStrategy


@dataclass
class ResourceServerRepresentation:
    """
    ResourceServerRepresentation
    """
    id: str = None
    client_id: str = None
    name: str = None
    allow_remote_resource_management: bool = None
    policy_enforcement_mode: PolicyEnforcementMode = None
    resources: List[ResourceRepresentation] = None
    policies: List[PolicyRepresentation] = None
    scopes: List[ScopeRepresentation] = None
    decision_strategy: DecisionStrategy = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ResourceServerRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'policy_enforcement_mode' in snake_data and snake_data['policy_enforcement_mode'] is not None:
            snake_data['policy_enforcement_mode'] = PolicyEnforcementMode.from_dict(snake_data['policy_enforcement_mode'])
        if 'resources' in snake_data and snake_data['resources'] is not None:
            snake_data['resources'] = [ResourceRepresentation.from_dict(item) for item in snake_data['resources']]
        if 'policies' in snake_data and snake_data['policies'] is not None:
            snake_data['policies'] = [PolicyRepresentation.from_dict(item) for item in snake_data['policies']]
        if 'scopes' in snake_data and snake_data['scopes'] is not None:
            snake_data['scopes'] = [ScopeRepresentation.from_dict(item) for item in snake_data['scopes']]
        if 'decision_strategy' in snake_data and snake_data['decision_strategy'] is not None:
            snake_data['decision_strategy'] = DecisionStrategy.from_dict(snake_data['decision_strategy'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
