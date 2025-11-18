from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class ClientInitialAccessPresentation:
    """
    ClientInitialAccessPresentation
    """
    id: str = None
    token: str = None
    timestamp: int = None
    expiration: int = None
    count: int = None
    remaining_count: int = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ClientInitialAccessPresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
