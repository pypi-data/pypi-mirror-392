from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class AuthenticationExecutionInfoRepresentation:
    """
    AuthenticationExecutionInfoRepresentation
    """
    id: str = None
    requirement: str = None
    display_name: str = None
    alias: str = None
    description: str = None
    requirement_choices: List[str] = None
    configurable: bool = None
    authentication_flow: bool = None
    provider_id: str = None
    authentication_config: str = None
    flow_id: str = None
    level: int = None
    index: int = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AuthenticationExecutionInfoRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
