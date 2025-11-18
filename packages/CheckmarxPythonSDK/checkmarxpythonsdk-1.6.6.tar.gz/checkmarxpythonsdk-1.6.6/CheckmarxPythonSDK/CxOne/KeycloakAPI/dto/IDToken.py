from dataclasses import dataclass, asdict
from typing import List
from inflection import camelize, underscore
from .AddressClaimSet import AddressClaimSet


@dataclass
class IDToken:
    """
    IDToken
    """
    jti: str = None
    exp: int = None
    nbf: int = None
    iat: int = None
    iss: str = None
    sub: str = None
    typ: str = None
    azp: str = None
    other_claims: dict = None
    nonce: str = None
    auth_time: int = None
    session_state: str = None
    at_hash: str = None
    c_hash: str = None
    name: str = None
    given_name: str = None
    family_name: str = None
    middle_name: str = None
    nickname: str = None
    preferred_username: str = None
    profile: str = None
    picture: str = None
    website: str = None
    email: str = None
    email_verified: bool = None
    gender: str = None
    birthdate: str = None
    zoneinfo: str = None
    locale: str = None
    phone_number: str = None
    phone_number_verified: bool = None
    address: AddressClaimSet = None
    updated_at: int = None
    claims_locales: str = None
    acr: str = None
    s_hash: str = None
    auth_time: int = None
    sid: str = None

    @classmethod
    def from_dict(cls, data: dict) -> 'IDToken':
        snake_data: dict = {underscore(k): v for k, v in data.items()}
        if 'address' in snake_data and snake_data['address'] is not None:
            snake_data['address'] = AddressClaimSet.from_dict(snake_data['address'])
        return cls(**snake_data)

    def to_dict(self) -> dict:
        return {camelize(k, False): v for k, v in asdict(self).items() if v is not None}
