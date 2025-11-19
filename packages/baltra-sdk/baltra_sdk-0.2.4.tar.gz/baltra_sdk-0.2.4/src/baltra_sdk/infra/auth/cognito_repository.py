import jwt
import logging

from baltra_sdk.domain.auth.ports import AuthRepository
from baltra_sdk.infra.aws.cognito_config import load_cognito_config

class CognitoAuthRepository(AuthRepository):
    def __init__(self):
        self._config = load_cognito_config(require_app_client_id=True)
        self.jwk_client = jwt.PyJWKClient(self._config.jwks_url)

    def get_user_from_token(self, token: str) -> dict | None:
        """Validates the token and returns the decoded payload if successful."""
        try:
            # Get the signing key from the JWKS using the token's kid
            signing_key = self.jwk_client.get_signing_key_from_jwt(token)

            # Decode and validate the token
            payload = jwt.decode(
                token,
                signing_key.key, # Use the actual key object from PyJWKClient
                algorithms=["RS256"],
                audience=self._config.app_client_id,
                issuer=self._config.issuer
            )

            # Token is valid, return the payload
            return payload

        except jwt.ExpiredSignatureError:
            logging.info("Token has expired.")
            return None
        except jwt.PyJWTError as e:
            logging.warning(f"Token validation failed: {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred during token validation: {e}")
            return None
