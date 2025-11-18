from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class KeyStoreConfig:
    """
    KeyStoreConfig
    """
    realm_certificate: bool = None
    store_password: str = None
    key_password: str = None
    key_alias: str = None
    realm_alias: str = None
    format: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'KeyStoreConfig':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
