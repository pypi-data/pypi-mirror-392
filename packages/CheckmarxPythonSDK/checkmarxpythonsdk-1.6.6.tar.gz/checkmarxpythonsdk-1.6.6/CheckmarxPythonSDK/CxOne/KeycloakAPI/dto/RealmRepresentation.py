from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .RolesRepresentation import RolesRepresentation
from .GroupRepresentation import GroupRepresentation
from .RoleRepresentation import RoleRepresentation
from .ClientProfilesRepresentation import ClientProfilesRepresentation
from .ClientPoliciesRepresentation import ClientPoliciesRepresentation
from .UserRepresentation import UserRepresentation
from .UserRepresentation import UserRepresentation
from .ScopeMappingRepresentation import ScopeMappingRepresentation
from .ClientRepresentation import ClientRepresentation
from .ClientScopeRepresentation import ClientScopeRepresentation
from .UserFederationProviderRepresentation import UserFederationProviderRepresentation
from .UserFederationMapperRepresentation import UserFederationMapperRepresentation
from .IdentityProviderRepresentation import IdentityProviderRepresentation
from .IdentityProviderMapperRepresentation import IdentityProviderMapperRepresentation
from .ProtocolMapperRepresentation import ProtocolMapperRepresentation
from .AuthenticationFlowRepresentation import AuthenticationFlowRepresentation
from .AuthenticatorConfigRepresentation import AuthenticatorConfigRepresentation
from .RequiredActionProviderRepresentation import RequiredActionProviderRepresentation
from .ApplicationRepresentation import ApplicationRepresentation
from .OAuthClientRepresentation import OAuthClientRepresentation
from .ClientTemplateRepresentation import ClientTemplateRepresentation


@dataclass
class RealmRepresentation:
    """
    RealmRepresentation
    """
    id: str = None
    realm: str = None
    display_name: str = None
    display_name_html: str = None
    not_before: int = None
    default_signature_algorithm: str = None
    revoke_refresh_token: bool = None
    refresh_token_max_reuse: int = None
    access_token_lifespan: int = None
    access_token_lifespan_for_implicit_flow: int = None
    sso_session_idle_timeout: int = None
    sso_session_max_lifespan: int = None
    sso_session_idle_timeout_remember_me: int = None
    sso_session_max_lifespan_remember_me: int = None
    offline_session_idle_timeout: int = None
    offline_session_max_lifespan_enabled: bool = None
    offline_session_max_lifespan: int = None
    client_session_idle_timeout: int = None
    client_session_max_lifespan: int = None
    client_offline_session_idle_timeout: int = None
    client_offline_session_max_lifespan: int = None
    access_code_lifespan: int = None
    access_code_lifespan_user_action: int = None
    access_code_lifespan_login: int = None
    action_token_generated_by_admin_lifespan: int = None
    action_token_generated_by_user_lifespan: int = None
    oauth2_device_code_lifespan: int = None
    oauth2_device_polling_interval: int = None
    enabled: bool = None
    ssl_required: str = None
    password_credential_grant_allowed: bool = None
    registration_allowed: bool = None
    registration_email_as_username: bool = None
    remember_me: bool = None
    verify_email: bool = None
    login_with_email_allowed: bool = None
    duplicate_emails_allowed: bool = None
    reset_password_allowed: bool = None
    edit_username_allowed: bool = None
    user_cache_enabled: bool = None
    realm_cache_enabled: bool = None
    brute_force_protected: bool = None
    permanent_lockout: bool = None
    max_failure_wait_seconds: int = None
    minimum_quick_login_wait_seconds: int = None
    wait_increment_seconds: int = None
    quick_login_check_milli_seconds: int = None
    max_delta_time_seconds: int = None
    failure_factor: int = None
    private_key: str = None
    public_key: str = None
    certificate: str = None
    code_secret: str = None
    roles: RolesRepresentation = None
    groups: List[GroupRepresentation] = None
    default_roles: List[str] = None
    default_role: RoleRepresentation = None
    default_groups: List[str] = None
    required_credentials: List[str] = None
    password_policy: str = None
    otp_policy_type: str = None
    otp_policy_algorithm: str = None
    otp_policy_initial_counter: int = None
    otp_policy_digits: int = None
    otp_policy_look_ahead_window: int = None
    otp_policy_period: int = None
    otp_policy_code_reusable: bool = None
    otp_supported_applications: List[str] = None
    localization_texts: dict = None
    web_authn_policy_rp_entity_name: str = None
    web_authn_policy_signature_algorithms: List[str] = None
    web_authn_policy_rp_id: str = None
    web_authn_policy_attestation_conveyance_preference: str = None
    web_authn_policy_authenticator_attachment: str = None
    web_authn_policy_require_resident_key: str = None
    web_authn_policy_user_verification_requirement: str = None
    web_authn_policy_create_timeout: int = None
    web_authn_policy_avoid_same_authenticator_register: bool = None
    web_authn_policy_acceptable_aaguids: List[str] = None
    web_authn_policy_extra_origins: List[str] = None
    web_authn_policy_passwordless_rp_entity_name: str = None
    web_authn_policy_passwordless_signature_algorithms: List[str] = None
    web_authn_policy_passwordless_rp_id: str = None
    web_authn_policy_passwordless_attestation_conveyance_preference: str = None
    web_authn_policy_passwordless_authenticator_attachment: str = None
    web_authn_policy_passwordless_require_resident_key: str = None
    web_authn_policy_passwordless_user_verification_requirement: str = None
    web_authn_policy_passwordless_create_timeout: int = None
    web_authn_policy_passwordless_avoid_same_authenticator_register: bool = None
    web_authn_policy_passwordless_acceptable_aaguids: List[str] = None
    web_authn_policy_passwordless_extra_origins: List[str] = None
    client_profiles: ClientProfilesRepresentation = None
    client_policies: ClientPoliciesRepresentation = None
    users: List[UserRepresentation] = None
    federated_users: List[UserRepresentation] = None
    scope_mappings: List[ScopeMappingRepresentation] = None
    client_scope_mappings: dict = None
    clients: List[ClientRepresentation] = None
    client_scopes: List[ClientScopeRepresentation] = None
    default_default_client_scopes: List[str] = None
    default_optional_client_scopes: List[str] = None
    browser_security_headers: dict = None
    smtp_server: dict = None
    user_federation_providers: List[UserFederationProviderRepresentation] = None
    user_federation_mappers: List[UserFederationMapperRepresentation] = None
    login_theme: str = None
    account_theme: str = None
    admin_theme: str = None
    email_theme: str = None
    events_enabled: bool = None
    events_expiration: int = None
    events_listeners: List[str] = None
    enabled_event_types: List[str] = None
    admin_events_enabled: bool = None
    admin_events_details_enabled: bool = None
    identity_providers: List[IdentityProviderRepresentation] = None
    identity_provider_mappers: List[IdentityProviderMapperRepresentation] = None
    protocol_mappers: List[ProtocolMapperRepresentation] = None
    components: dict = None
    internationalization_enabled: bool = None
    supported_locales: List[str] = None
    default_locale: str = None
    authentication_flows: List[AuthenticationFlowRepresentation] = None
    authenticator_config: List[AuthenticatorConfigRepresentation] = None
    required_actions: List[RequiredActionProviderRepresentation] = None
    browser_flow: str = None
    registration_flow: str = None
    direct_grant_flow: str = None
    reset_credentials_flow: str = None
    client_authentication_flow: str = None
    docker_authentication_flow: str = None
    attributes: dict = None
    keycloak_version: str = None
    user_managed_access_allowed: bool = None
    social: bool = None
    update_profile_on_initial_social_login: bool = None
    social_providers: dict = None
    application_scope_mappings: dict = None
    applications: List[ApplicationRepresentation] = None
    oauth_clients: List[OAuthClientRepresentation] = None
    client_templates: List[ClientTemplateRepresentation] = None
    o_auth2_device_code_lifespan: int = None
    o_auth2_device_polling_interval: int = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RealmRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'roles' in snake_data and snake_data['roles'] is not None:
            snake_data['roles'] = RolesRepresentation.from_dict(snake_data['roles'])
        if 'groups' in snake_data and snake_data['groups'] is not None:
            snake_data['groups'] = [GroupRepresentation.from_dict(item) for item in snake_data['groups']]
        if 'default_role' in snake_data and snake_data['default_role'] is not None:
            snake_data['default_role'] = RoleRepresentation.from_dict(snake_data['default_role'])
        if 'client_profiles' in snake_data and snake_data['client_profiles'] is not None:
            snake_data['client_profiles'] = ClientProfilesRepresentation.from_dict(snake_data['client_profiles'])
        if 'client_policies' in snake_data and snake_data['client_policies'] is not None:
            snake_data['client_policies'] = ClientPoliciesRepresentation.from_dict(snake_data['client_policies'])
        if 'users' in snake_data and snake_data['users'] is not None:
            snake_data['users'] = [UserRepresentation.from_dict(item) for item in snake_data['users']]
        if 'federated_users' in snake_data and snake_data['federated_users'] is not None:
            snake_data['federated_users'] = [UserRepresentation.from_dict(item) for item in snake_data['federated_users']]
        if 'scope_mappings' in snake_data and snake_data['scope_mappings'] is not None:
            snake_data['scope_mappings'] = [ScopeMappingRepresentation.from_dict(item) for item in snake_data['scope_mappings']]
        if 'clients' in snake_data and snake_data['clients'] is not None:
            snake_data['clients'] = [ClientRepresentation.from_dict(item) for item in snake_data['clients']]
        if 'client_scopes' in snake_data and snake_data['client_scopes'] is not None:
            snake_data['client_scopes'] = [ClientScopeRepresentation.from_dict(item) for item in snake_data['client_scopes']]
        if 'user_federation_providers' in snake_data and snake_data['user_federation_providers'] is not None:
            snake_data['user_federation_providers'] = [UserFederationProviderRepresentation.from_dict(item) for item in snake_data['user_federation_providers']]
        if 'user_federation_mappers' in snake_data and snake_data['user_federation_mappers'] is not None:
            snake_data['user_federation_mappers'] = [UserFederationMapperRepresentation.from_dict(item) for item in snake_data['user_federation_mappers']]
        if 'identity_providers' in snake_data and snake_data['identity_providers'] is not None:
            snake_data['identity_providers'] = [IdentityProviderRepresentation.from_dict(item) for item in snake_data['identity_providers']]
        if 'identity_provider_mappers' in snake_data and snake_data['identity_provider_mappers'] is not None:
            snake_data['identity_provider_mappers'] = [IdentityProviderMapperRepresentation.from_dict(item) for item in snake_data['identity_provider_mappers']]
        if 'protocol_mappers' in snake_data and snake_data['protocol_mappers'] is not None:
            snake_data['protocol_mappers'] = [ProtocolMapperRepresentation.from_dict(item) for item in snake_data['protocol_mappers']]
        if 'authentication_flows' in snake_data and snake_data['authentication_flows'] is not None:
            snake_data['authentication_flows'] = [AuthenticationFlowRepresentation.from_dict(item) for item in snake_data['authentication_flows']]
        if 'authenticator_config' in snake_data and snake_data['authenticator_config'] is not None:
            snake_data['authenticator_config'] = [AuthenticatorConfigRepresentation.from_dict(item) for item in snake_data['authenticator_config']]
        if 'required_actions' in snake_data and snake_data['required_actions'] is not None:
            snake_data['required_actions'] = [RequiredActionProviderRepresentation.from_dict(item) for item in snake_data['required_actions']]
        if 'applications' in snake_data and snake_data['applications'] is not None:
            snake_data['applications'] = [ApplicationRepresentation.from_dict(item) for item in snake_data['applications']]
        if 'oauth_clients' in snake_data and snake_data['oauth_clients'] is not None:
            snake_data['oauth_clients'] = [OAuthClientRepresentation.from_dict(item) for item in snake_data['oauth_clients']]
        if 'client_templates' in snake_data and snake_data['client_templates'] is not None:
            snake_data['client_templates'] = [ClientTemplateRepresentation.from_dict(item) for item in snake_data['client_templates']]
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
