from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .ProtocolMapperRepresentation import ProtocolMapperRepresentation


@dataclass
class ClientScopeRepresentation:
    """
    ClientScopeRepresentation
    """
    id: str = None
    name: str = None
    description: str = None
    protocol: str = None
    attributes: dict = None
    protocol_mappers: List[ProtocolMapperRepresentation] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ClientScopeRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'protocol_mappers' in snake_data and snake_data['protocol_mappers'] is not None:
            snake_data['protocol_mappers'] = [ProtocolMapperRepresentation.from_dict(item) for item in snake_data['protocol_mappers']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
