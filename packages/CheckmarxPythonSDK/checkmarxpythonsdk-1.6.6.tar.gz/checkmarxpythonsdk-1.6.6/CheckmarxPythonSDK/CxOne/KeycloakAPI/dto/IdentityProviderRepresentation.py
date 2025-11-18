from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore


@dataclass
class IdentityProviderRepresentation:
    """
    IdentityProviderRepresentation
    """
    alias: str = None
    display_name: str = None
    internal_id: str = None
    provider_id: str = None
    enabled: bool = None
    update_profile_first_login_mode: str = None
    trust_email: bool = None
    store_token: bool = None
    add_read_token_role_on_create: bool = None
    authenticate_by_default: bool = None
    link_only: bool = None
    first_broker_login_flow_alias: str = None
    post_broker_login_flow_alias: str = None
    config: dict = None
    update_profile_first_login: bool = None

    @classmethod
    def from_dict(cls, data: dict) -> 'IdentityProviderRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
