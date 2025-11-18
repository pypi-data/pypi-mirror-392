from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class ProtocolMapperEvaluationRepresentation:
    """
    ProtocolMapperEvaluationRepresentation
    """
    mapper_id: str = None
    mapper_name: str = None
    container_id: str = None
    container_name: str = None
    container_type: str = None
    protocol_mapper: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ProtocolMapperEvaluationRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
