from typing import Callable, Dict, Any

import jwt
from async_lru import alru_cache
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWK
from starlette import status

from sirius.common import is_test_environment, get_environmental_secret, is_production_environment
from sirius.constants import SiriusEnvironmentSecretKey
from sirius.exceptions import ApplicationException


async def get_private_key() -> str:
    generate_private_key: Callable[[], str] = lambda: rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    if is_test_environment():
        return generate_private_key()

    try:
        return await get_environmental_secret(SiriusEnvironmentSecretKey.PRIVATE_KEY)
    except ApplicationException:
        return await get_environmental_secret(SiriusEnvironmentSecretKey.PRIVATE_KEY, generate_private_key())


@alru_cache(maxsize=50, ttl=86_400)  # 24 hour cache
async def get_public_key() -> str:
    private_key_string: str = await get_private_key()
    return (serialization.load_pem_private_key(private_key_string.encode("utf-8"), password=None)
            .public_key()
            .public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode("utf-8"))


@alru_cache(maxsize=50, ttl=86_400)  # 24 hour cache
async def get_oidc_config(oidc_config_url: str) -> Dict[str, Any]:
    from sirius.http_requests import AsyncHTTPSession
    return (await AsyncHTTPSession(oidc_config_url).get(oidc_config_url)).data


async def is_token_valid(token: str, oidc_config_url: str | None = None, audience: str | None = None, issuer: str | None = None) -> bool:
    tenant_id: str = await get_environmental_secret(SiriusEnvironmentSecretKey.MICROSOFT_TENANT_ID)
    audience = await get_environmental_secret(SiriusEnvironmentSecretKey.MICROSOFT_CLIENT_ID) if not audience else audience
    issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0" if not issuer else issuer
    oidc_config_url = f"https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration" if not oidc_config_url else oidc_config_url
    oidc_config: Dict[str, Any] = await get_oidc_config(oidc_config_url)
    jwks_uri: str = oidc_config.get("jwks_uri")
    jwks_client = jwt.PyJWKClient(jwks_uri)

    try:
        signing_key: PyJWK = jwks_client.get_signing_key(jwt.get_unverified_header(token)["kid"])
        jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
            verify=True
        )
    except Exception:
        return False

    return True


async def verify_token(token: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> None:
    if not is_production_environment():
        return

    if not await is_token_valid(token.credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"}, )
