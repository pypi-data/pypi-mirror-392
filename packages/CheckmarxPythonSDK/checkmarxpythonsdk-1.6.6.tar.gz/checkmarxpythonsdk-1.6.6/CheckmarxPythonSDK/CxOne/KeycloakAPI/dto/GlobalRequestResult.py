from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class GlobalRequestResult:
    """
    GlobalRequestResult
    """
    success_requests: List[str] = None
    failed_requests: List[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'GlobalRequestResult':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
