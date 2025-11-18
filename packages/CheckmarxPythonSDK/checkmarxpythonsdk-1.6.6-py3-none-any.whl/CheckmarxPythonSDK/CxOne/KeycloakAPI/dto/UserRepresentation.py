from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .CredentialRepresentation import CredentialRepresentation
from .FederatedIdentityRepresentation import FederatedIdentityRepresentation
from .UserConsentRepresentation import UserConsentRepresentation
from .SocialLinkRepresentation import SocialLinkRepresentation
from .UserProfileMetadata import UserProfileMetadata


@dataclass
class UserRepresentation:
    """
    UserRepresentation
    """
    self: str = None
    id: str = None
    origin: str = None
    created_timestamp: int = None
    username: str = None
    enabled: bool = None
    totp: bool = None
    email_verified: bool = None
    first_name: str = None
    last_name: str = None
    email: str = None
    federation_link: str = None
    service_account_client_id: str = None
    attributes: dict = None
    credentials: List[CredentialRepresentation] = None
    disableable_credential_types: List[str] = None
    required_actions: List[str] = None
    federated_identities: List[FederatedIdentityRepresentation] = None
    realm_roles: List[str] = None
    client_roles: dict = None
    client_consents: List[UserConsentRepresentation] = None
    not_before: int = None
    application_roles: dict = None
    social_links: List[SocialLinkRepresentation] = None
    groups: List[str] = None
    access: dict = None
    user_profile_metadata: UserProfileMetadata = None

    @classmethod
    def from_dict(cls, data: dict) -> 'UserRepresentation':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'credentials' in snake_data and snake_data['credentials'] is not None:
            snake_data['credentials'] = [CredentialRepresentation.from_dict(item) for item in snake_data['credentials']]
        if 'federated_identities' in snake_data and snake_data['federated_identities'] is not None:
            snake_data['federated_identities'] = [FederatedIdentityRepresentation.from_dict(item) for item in snake_data['federated_identities']]
        if 'client_consents' in snake_data and snake_data['client_consents'] is not None:
            snake_data['client_consents'] = [UserConsentRepresentation.from_dict(item) for item in snake_data['client_consents']]
        if 'social_links' in snake_data and snake_data['social_links'] is not None:
            snake_data['social_links'] = [SocialLinkRepresentation.from_dict(item) for item in snake_data['social_links']]
        if 'user_profile_metadata' in snake_data and snake_data['user_profile_metadata'] is not None:
            snake_data['user_profile_metadata'] = UserProfileMetadata.from_dict(snake_data['user_profile_metadata'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
