from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .ClientPolicyRepresentation import ClientPolicyRepresentation


@dataclass
class ClientPoliciesRepresentation:
    """
    ClientPoliciesRepresentation
    """
    policies: List[ClientPolicyRepresentation] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ClientPoliciesRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'policies' in snake_data and snake_data['policies'] is not None:
            snake_data['policies'] = [ClientPolicyRepresentation.from_dict(item) for item in snake_data['policies']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
