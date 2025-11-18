from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .ClientPolicyExecutorRepresentation import ClientPolicyExecutorRepresentation


@dataclass
class ClientProfileRepresentation:
    """
    ClientProfileRepresentation
    """
    name: str = None
    description: str = None
    executors: List[ClientPolicyExecutorRepresentation] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ClientProfileRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'executors' in snake_data and snake_data['executors'] is not None:
            snake_data['executors'] = [ClientPolicyExecutorRepresentation.from_dict(item) for item in snake_data['executors']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
