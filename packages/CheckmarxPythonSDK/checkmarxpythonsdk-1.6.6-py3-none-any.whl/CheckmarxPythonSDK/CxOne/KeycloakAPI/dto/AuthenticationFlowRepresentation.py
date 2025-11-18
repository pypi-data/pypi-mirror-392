from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .AuthenticationExecutionExportRepresentation import AuthenticationExecutionExportRepresentation


@dataclass
class AuthenticationFlowRepresentation:
    """
    AuthenticationFlowRepresentation
    """
    id: str = None
    alias: str = None
    description: str = None
    provider_id: str = None
    top_level: bool = None
    built_in: bool = None
    authentication_executions: List[AuthenticationExecutionExportRepresentation] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AuthenticationFlowRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'authentication_executions' in snake_data and snake_data['authentication_executions'] is not None:
            snake_data['authentication_executions'] = [AuthenticationExecutionExportRepresentation.from_dict(item) for item in snake_data['authentication_executions']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
