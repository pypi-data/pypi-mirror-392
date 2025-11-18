from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .ClientProfileRepresentation import ClientProfileRepresentation
from .ClientProfileRepresentation import ClientProfileRepresentation


@dataclass
class ClientProfilesRepresentation:
    """
    ClientProfilesRepresentation
    """
    profiles: List[ClientProfileRepresentation] = None
    global_profiles: List[ClientProfileRepresentation] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ClientProfilesRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'profiles' in snake_data and snake_data['profiles'] is not None:
            snake_data['profiles'] = [ClientProfileRepresentation.from_dict(item) for item in snake_data['profiles']]
        if 'global_profiles' in snake_data and snake_data['global_profiles'] is not None:
            snake_data['global_profiles'] = [ClientProfileRepresentation.from_dict(item) for item in snake_data['global_profiles']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
