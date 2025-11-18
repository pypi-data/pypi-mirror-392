from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class IdentityProviderMapperRepresentation:
    """
    IdentityProviderMapperRepresentation
    """
    id: str = None
    name: str = None
    identity_provider_alias: str = None
    identity_provider_mapper: str = None
    config: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> 'IdentityProviderMapperRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
