from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class CredentialRepresentation:
    """
    CredentialRepresentation
    """
    id: str = None
    type: str = None
    user_label: str = None
    created_date: int = None
    secret_data: str = None
    credential_data: str = None
    priority: int = None
    value: str = None
    temporary: bool = None
    device: str = None
    hashed_salted_value: str = None
    salt: str = None
    hash_iterations: int = None
    counter: int = None
    algorithm: str = None
    digits: int = None
    period: int = None
    config: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> 'CredentialRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
