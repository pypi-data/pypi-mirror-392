"""Social authentication token validators for Apple and Google."""
import time
from typing import Any

import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flerity_core.utils.errors import BadRequest, FailedDependency

from .schemas import SocialUserInfo


class AppleTokenValidator:
    """Apple Sign In token validator."""

    APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
    APPLE_ISSUER = "https://appleid.apple.com"

    def __init__(self, client_id: str):
        self.client_id = client_id
        self._keys_cache: dict[str, Any] | None = None
        self._keys_cache_time: float | None = None

    async def validate_token(self, identity_token: str) -> SocialUserInfo:
        """Validate Apple identity token and return user information."""
        if not identity_token or not identity_token.strip():
            raise BadRequest("Token Apple não pode estar vazio")

        try:
            # Decode header to get kid
            header = jwt.get_unverified_header(identity_token)
            kid = header.get('kid')

            if not kid:
                raise BadRequest("Token Apple inválido: kid não encontrado")

            # Get Apple public keys
            apple_keys = await self._get_apple_keys()
            public_key = self._get_public_key(apple_keys, kid)

            # Decode without validation first to see what's inside
            unverified_payload = jwt.decode(identity_token, options={"verify_signature": False})
            print("🔍 Apple token debug:")
            print(f"  aud (token): {unverified_payload.get('aud')}")
            print(f"  iss (token): {unverified_payload.get('iss')}")
            print(f"  sub (token): {unverified_payload.get('sub')}")
            print(f"  expected aud: {self.client_id}")

            # Validate and decode token
            try:
                payload = jwt.decode(
                    identity_token,
                    public_key,
                    algorithms=['RS256'],
                    audience=self.client_id,
                    issuer=self.APPLE_ISSUER
                )
                print("✅ Token validated successfully!")
            except jwt.InvalidAudienceError as e:
                print(f"❌ Audience mismatch: {str(e)}")
                raise BadRequest(f"Token Apple inválido: audience mismatch. Expected '{self.client_id}', got '{unverified_payload.get('aud')}'")
            except jwt.InvalidIssuerError as e:
                print(f"❌ Issuer mismatch: {str(e)}")
                raise BadRequest("Token Apple inválido: issuer mismatch")
            except jwt.ExpiredSignatureError as e:
                print(f"❌ Token expired: {str(e)}")
                raise BadRequest("Token Apple expirado")
            except jwt.InvalidSignatureError as e:
                print(f"❌ Invalid signature: {str(e)}")
                raise BadRequest("Token Apple inválido: assinatura inválida")
            except Exception as e:
                print(f"❌ JWT decode error: {type(e).__name__}: {str(e)}")
                raise BadRequest(f"Token Apple inválido: {str(e)}")

            return SocialUserInfo(
                provider_user_id=payload['sub'],
                email=payload.get('email'),
                name=None,  # Apple doesn't provide name in token
                email_verified=payload.get('email_verified', False)
            )

        except jwt.InvalidTokenError as e:
            print(f"❌ InvalidTokenError: {str(e)}")
            raise BadRequest(f"Token Apple inválido: {str(e)}")
        except Exception as e:
            print(f"❌ General exception: {type(e).__name__}: {str(e)}")
            raise FailedDependency(f"Erro ao validar token Apple: {str(e)}")

    async def _get_apple_keys(self) -> dict[str, Any]:
        """Fetch Apple public keys with caching."""
        # Cache for 1 hour
        if (self._keys_cache and self._keys_cache_time and
            time.time() - self._keys_cache_time < 3600):
            return self._keys_cache

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.APPLE_KEYS_URL)
                response.raise_for_status()

                self._keys_cache = response.json()
                self._keys_cache_time = time.time()
                return self._keys_cache
        except httpx.RequestError as e:
            raise FailedDependency(f"Erro ao buscar chaves Apple: {str(e)}")

    def _get_public_key(self, keys: dict[str, Any], kid: str) -> bytes:
        """Convert JWK to public key."""
        for key in keys['keys']:
            if key['kid'] == kid:
                # Convert JWK to PEM
                try:
                    public_numbers = rsa.RSAPublicNumbers(
                        e=int.from_bytes(
                            jwt.utils.base64url_decode(key['e']), 'big'
                        ),
                        n=int.from_bytes(
                            jwt.utils.base64url_decode(key['n']), 'big'
                        )
                    )
                    public_key = public_numbers.public_key()
                    return public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                except Exception as e:
                    raise BadRequest(f"Erro ao processar chave Apple: {str(e)}")

        raise BadRequest("Chave pública Apple não encontrada")


class GoogleTokenValidator:
    """Google OAuth token validator."""

    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    async def validate_token(self, access_token: str) -> SocialUserInfo:
        """Validate Google access token and fetch user information."""
        if not access_token or not access_token.strip():
            raise BadRequest("Token Google não pode estar vazio")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )

                if response.status_code == 401:
                    raise BadRequest("Token Google inválido ou expirado")
                elif response.status_code == 403:
                    raise BadRequest("Token Google sem permissões necessárias")
                elif response.status_code == 429:
                    raise FailedDependency("Muitas requisições para API Google - tente novamente")
                elif response.status_code != 200:
                    raise FailedDependency(f"Erro na API Google: {response.status_code}")

                user_data = response.json()

                return SocialUserInfo(
                    provider_user_id=user_data['id'],
                    email=user_data.get('email'),
                    name=user_data.get('name'),
                    avatar_url=user_data.get('picture'),
                    email_verified=user_data.get('verified_email', False)
                )

        except httpx.RequestError as e:
            raise FailedDependency(f"Erro ao validar token Google: {str(e)}")
        except KeyError as e:
            raise BadRequest(f"Resposta inválida da API Google: campo {str(e)} não encontrado")
