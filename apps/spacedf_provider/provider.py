import jwt
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from jwt.exceptions import InvalidTokenError

from .views import SpaceDFAdapter


class SpaceDFAccount(ProviderAccount):
    pass


class SpaceDFProvider(OAuth2Provider):
    id = "spacedf"
    name = "SpaceDF"
    account_class = SpaceDFAccount
    oauth2_adapter_class = SpaceDFAdapter

    def extract_uid(self, data):
        return str(data["user_id"])

    def extract_common_fields(self, data):
        user = data.get("user")
        return dict(
            user_id=data.get("user_id"),
            email=user.get("email"),
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            email_verified=True,
        )

    def decode_id_token(self, id_token):
        try:
            return jwt.decode(id_token, options={"verify_signature": False})
        except InvalidTokenError as e:
            raise ValueError(f"Invalid ID token: {str(e)}")


provider_classes = [SpaceDFProvider]
