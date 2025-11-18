from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class UserConsentRepresentation:
    """
    UserConsentRepresentation
    """
    client_id: str = None
    granted_client_scopes: List[str] = None
    created_date: int = None
    last_updated_date: int = None
    granted_realm_roles: List[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'UserConsentRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
