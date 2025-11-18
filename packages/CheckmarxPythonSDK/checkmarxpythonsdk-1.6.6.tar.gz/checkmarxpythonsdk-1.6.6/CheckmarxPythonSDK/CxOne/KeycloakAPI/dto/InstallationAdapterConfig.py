from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .PolicyEnforcerConfig import PolicyEnforcerConfig


@dataclass
class InstallationAdapterConfig:
    """
    InstallationAdapterConfig
    """
    realm: str = None
    realm_public_key: str = None
    auth_server_url: str = None
    ssl_required: str = None
    bearer_only: bool = None
    resource: str = None
    public_client: bool = None
    verify_token_audience: bool = None
    credentials: dict = None
    use_resource_role_mappings: bool = None
    confidential_port: int = None
    policy_enforcer: PolicyEnforcerConfig = None

    @classmethod
    def from_dict(cls, data: dict) -> 'InstallationAdapterConfig':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'policy_enforcer' in snake_data and snake_data['policy_enforcer'] is not None:
            snake_data['policy_enforcer'] = PolicyEnforcerConfig.from_dict(snake_data['policy_enforcer'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
