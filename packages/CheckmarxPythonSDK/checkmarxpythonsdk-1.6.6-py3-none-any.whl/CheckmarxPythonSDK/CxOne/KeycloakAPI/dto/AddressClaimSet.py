from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class AddressClaimSet:
    """
    AddressClaimSet
    """
    formatted: str = None
    street_address: str = None
    locality: str = None
    region: str = None
    postal_code: str = None
    country: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AddressClaimSet':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
