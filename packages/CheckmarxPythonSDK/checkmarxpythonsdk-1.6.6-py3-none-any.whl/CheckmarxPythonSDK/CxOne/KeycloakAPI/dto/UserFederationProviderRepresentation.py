from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class UserFederationProviderRepresentation:
    """
    UserFederationProviderRepresentation
    """
    id: str = None
    display_name: str = None
    provider_name: str = None
    config: dict = None
    priority: int = None
    full_sync_period: int = None
    changed_sync_period: int = None
    last_sync: int = None

    @classmethod
    def from_dict(cls, data: dict) -> 'UserFederationProviderRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
