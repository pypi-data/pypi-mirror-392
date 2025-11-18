from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .ClientPolicyConditionRepresentation import ClientPolicyConditionRepresentation


@dataclass
class ClientPolicyRepresentation:
    """
    ClientPolicyRepresentation
    """
    name: str = None
    description: str = None
    enabled: bool = None
    conditions: List[ClientPolicyConditionRepresentation] = None
    profiles: List[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ClientPolicyRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'conditions' in snake_data and snake_data['conditions'] is not None:
            snake_data['conditions'] = [ClientPolicyConditionRepresentation.from_dict(item) for item in snake_data['conditions']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
