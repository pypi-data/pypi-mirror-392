from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .EnforcementMode import EnforcementMode
from .PathConfig import PathConfig
from .PathCacheConfig import PathCacheConfig


@dataclass
class PolicyEnforcerConfig:
    """
    PolicyEnforcerConfig
    """
    enforcement_mode: EnforcementMode = None
    paths: List[PathConfig] = None
    path_cache: PathCacheConfig = None
    lazy_load_paths: bool = None
    on_deny_redirect_to: str = None
    user_managed_access: dict = None
    claim_information_point: dict = None
    http_method_as_scope: bool = None
    realm: str = None
    auth_server_url: str = None
    credentials: dict = None
    resource: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'PolicyEnforcerConfig':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'enforcement_mode' in snake_data and snake_data['enforcement_mode'] is not None:
            snake_data['enforcement_mode'] = EnforcementMode.from_dict(snake_data['enforcement_mode'])
        if 'paths' in snake_data and snake_data['paths'] is not None:
            snake_data['paths'] = [PathConfig.from_dict(item) for item in snake_data['paths']]
        if 'path_cache' in snake_data and snake_data['path_cache'] is not None:
            snake_data['path_cache'] = PathCacheConfig.from_dict(snake_data['path_cache'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
