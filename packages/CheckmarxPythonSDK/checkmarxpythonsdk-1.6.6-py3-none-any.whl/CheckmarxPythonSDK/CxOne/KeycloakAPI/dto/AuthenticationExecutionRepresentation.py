from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class AuthenticationExecutionRepresentation:
    """
    AuthenticationExecutionRepresentation
    """
    authenticator_config: str = None
    authenticator: str = None
    authenticator_flow: bool = None
    requirement: str = None
    priority: int = None
    autheticator_flow: bool = None
    id: str = None
    flow_id: str = None
    parent_flow: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AuthenticationExecutionRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
