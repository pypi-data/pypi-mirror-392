from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .ProtocolMapperRepresentation import ProtocolMapperRepresentation
from .ResourceServerRepresentation import ResourceServerRepresentation


@dataclass
class ClientRepresentation:
    """
    ClientRepresentation
    """
    id: str = None
    client_id: str = None
    name: str = None
    description: str = None
    root_url: str = None
    admin_url: str = None
    base_url: str = None
    surrogate_auth_required: bool = None
    enabled: bool = None
    always_display_in_console: bool = None
    client_authenticator_type: str = None
    secret: str = None
    registration_access_token: str = None
    default_roles: List[str] = None
    redirect_uris: List[str] = None
    web_origins: List[str] = None
    not_before: int = None
    bearer_only: bool = None
    consent_required: bool = None
    standard_flow_enabled: bool = None
    implicit_flow_enabled: bool = None
    direct_access_grants_enabled: bool = None
    service_accounts_enabled: bool = None
    oauth2_device_authorization_grant_enabled: bool = None
    authorization_services_enabled: bool = None
    direct_grants_only: bool = None
    public_client: bool = None
    frontchannel_logout: bool = None
    protocol: str = None
    attributes: dict = None
    authentication_flow_binding_overrides: dict = None
    full_scope_allowed: bool = None
    node_re_registration_timeout: int = None
    registered_nodes: dict = None
    protocol_mappers: List[ProtocolMapperRepresentation] = None
    client_template: str = None
    use_template_config: bool = None
    use_template_scope: bool = None
    use_template_mappers: bool = None
    default_client_scopes: List[str] = None
    optional_client_scopes: List[str] = None
    authorization_settings: ResourceServerRepresentation = None
    access: dict = None
    origin: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ClientRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'protocol_mappers' in snake_data and snake_data['protocol_mappers'] is not None:
            snake_data['protocol_mappers'] = [ProtocolMapperRepresentation.from_dict(item) for item in snake_data['protocol_mappers']]
        if 'authorization_settings' in snake_data and snake_data['authorization_settings'] is not None:
            snake_data['authorization_settings'] = ResourceServerRepresentation.from_dict(snake_data['authorization_settings'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
