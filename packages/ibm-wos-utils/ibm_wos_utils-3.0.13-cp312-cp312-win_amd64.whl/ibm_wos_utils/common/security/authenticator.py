# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import re
from threading import RLock
from typing import Any

import aiofiles
from aiohttp import ClientSession
import jwt
from async_lru import alru_cache
from cachetools import TTLCache, cached
from jwt.api_jwk import PyJWK

from ibm_wos_utils.joblib.utils.constants import SERVICE_ID
from ibm_wos_utils.joblib.utils.environment import Environment as Env
from ibm_wos_utils.joblib.utils.rest_async_util import RestAsyncUtil
from ibm_wos_utils.joblib.utils.rest_util import RestUtil

ALL_ASYMMETRIC_ALGORITHMS = ["RS256", "RS384",
                             "RS512", "ES256", "ES384", "ES512"]
INTERNAL_SERVICE = "internal-service"
AIOS_SERVICE_CREDENTIALS_PATH = "/etc/.secrets/svc-pwd"


class Authenticator():
    """Class to authenticate the user token."""

    def __init__(self, bearer_token, verify_exp: bool = True, client_session: ClientSession | None = None):
        self.access_token = bearer_token
        self.is_cpd = Env.is_cpd()
        self.iam_public_keys_url = Env.get_cpd_iam_public_keys_url(
        ) if self.is_cpd else Env.get_cloud_iam_public_keys_url()
        self.verify_exp = verify_exp
        self._client_session = client_session

    @property
    def access_token(self):
        return self.__access_token

    @access_token.setter
    def access_token(self, bearer_token):
        if not bearer_token:
            raise ValueError("The IAM token is invalid.")

        token = re.search("[B|b]earer(.*)", bearer_token)
        if not token:
            raise ValueError("The IAM token is invalid.")

        self.__access_token = token.group(1).strip()

    @property
    def iam_public_keys_url(self):
        return self.__iam_public_keys_url

    @iam_public_keys_url.setter
    def iam_public_keys_url(self, iam_public_keys_url):
        if not iam_public_keys_url:
            raise ValueError("The IAM public keys url is invalid.")

        self.__iam_public_keys_url = iam_public_keys_url

    def _get_authenticator(self):
        if self.is_cpd:
            return CPDTokenAuthenticator(access_token=self.access_token,
                                         iam_public_keys_url=self.iam_public_keys_url,
                                         verify_exp=self.verify_exp,
                                         client_session=self._client_session,
                                         )
        else:
            return CloudTokenAuthenticator(access_token=self.access_token,
                                           iam_public_keys_url=self.iam_public_keys_url,
                                           verify_exp=self.verify_exp,
                                           client_session=self._client_session,
                                           )

    def authenticate(self):
        try:
            authenticator = self._get_authenticator()
            return authenticator.validate()
        except jwt.ExpiredSignatureError as _:
            raise ValueError("The IAM Token expired.")
        except (jwt.InvalidAlgorithmError, TypeError, UnboundLocalError) as e:
            raise ValueError("The IAM token is invalid.")

    async def authenticate_async(self):
        try:
            authenticator = self._get_authenticator()
            return await authenticator.validate_async()
        except jwt.ExpiredSignatureError as _:
            raise ValueError("The IAM Token expired.")
        except (jwt.InvalidAlgorithmError, TypeError, UnboundLocalError) as e:
            raise ValueError("The IAM token is invalid.")


class CloudTokenAuthenticator():
    """Class to authenticate the access token in Cloud environment."""

    def __init__(self, access_token, iam_public_keys_url, verify_exp: bool = True, client_session: ClientSession | None = None):
        self.access_token = access_token
        self.iam_public_keys_url = iam_public_keys_url
        self.verify_exp = verify_exp
        self._client_session = client_session

    def _jwt_decode(self, pubkey):
        options = {
            "verify_iat": False,
            "verify_exp": self.verify_exp,
            "verify_aud": False
        }
        return jwt.decode(jwt=self.access_token,
                          key=pubkey,
                          algorithms=ALL_ASYMMETRIC_ALGORITHMS,
                          options=options)

    def validate(self):
        pubkey = get_cloud_pubkey(
            self.access_token, self.iam_public_keys_url)
        return self._jwt_decode(pubkey)

    async def validate_async(self):
        pubkey = await get_cloud_pubkey_async(
            self.access_token, self.iam_public_keys_url, self._client_session)
        return self._jwt_decode(pubkey)


class CPDTokenAuthenticator():
    """Class to authenticate the access token in CPD environment."""

    def __init__(self, access_token, iam_public_keys_url, verify_exp: bool = True, client_session: ClientSession | None = None):
        self.access_token = access_token
        self.iam_public_keys_url = iam_public_keys_url
        self.verify_exp = verify_exp
        self._client_session = client_session

    def _validate_service_credentials(self, service_creds: str) -> dict[str, Any]:
        if self.access_token != service_creds:
            raise ValueError("The service access token is invalid.")

        return {
            "name": INTERNAL_SERVICE,
            "email": INTERNAL_SERVICE,
            "sub": INTERNAL_SERVICE,
            "sub_type": SERVICE_ID,
            "iam_id": INTERNAL_SERVICE,
            "account": {"bss": INTERNAL_SERVICE}
        }

    def _validate_jwt_token(self, pubkey: str) -> dict[str, Any]:
        pubkey = get_cpd_pubkey(self.iam_public_keys_url)
        options = {
            "verify_iat": False,
            "verify_aud": False,
            "verify_exp": self.verify_exp
        }

        payload = jwt.decode(jwt=self.access_token,
                             key=pubkey,
                             algorithms=ALL_ASYMMETRIC_ALGORITHMS,
                             options=options)

        return {
            "name": payload.get("username"),
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "iam_id": payload.get("uid"),
            "account": {"bss": payload.get("uid")},
            "iat": payload.get("iat"),
            "exp": payload.get("exp"),
        }

    def validate(self):
        if self.access_token.startswith("aios-"):
            with open(AIOS_SERVICE_CREDENTIALS_PATH, "r") as f:
                service_creds = f.read()

            return self._validate_service_credentials(service_creds)

        pubkey = get_cpd_pubkey(self.iam_public_keys_url)
        return self._validate_jwt_token(pubkey)

    async def validate_async(self):
        if self.access_token.startswith("aios-"):
            async with aiofiles.open(AIOS_SERVICE_CREDENTIALS_PATH, 'r') as f:
                service_creds = await f.read()

            return self._validate_service_credentials(service_creds)

        pubkey = await get_cpd_pubkey_async(self.iam_public_keys_url, self._client_session)
        return self._validate_jwt_token(pubkey)


cloud_pubkey_cache_lock = RLock()


def _parse_kid_from_access_token(access_token: str):
    jwt_header = jwt.get_unverified_header(access_token)

    try:
        kid = jwt_header["kid"]
    except Exception as e:
        raise ValueError("The IAM token is invalid.")

    return kid


def _parse_cloud_pubkey(fetched_resp, kid):
    fetched_keys = []
    if fetched_resp is not None and isinstance(fetched_resp, list):
        fetched_keys = fetched_resp
    if fetched_resp is not None and isinstance(fetched_resp, dict):
        if fetched_resp.get("keys"):
            fetched_keys = fetched_resp.get("keys")

    signing_key = next(
        (key for key in fetched_keys if key["kid"] == kid), None)

    # It can happen that the expected "kid" is not found in the list
    if signing_key is None or signing_key["n"] is None or signing_key["e"] is None:
        raise ValueError("The IAM token is invalid.")

    py_signing_key = PyJWK(signing_key, algorithm=signing_key["alg"])
    return py_signing_key.key


@cached(cache=TTLCache(maxsize=1024, ttl=7200), lock=cloud_pubkey_cache_lock)
def get_cloud_pubkey(access_token, iam_public_keys_url):
    kid = _parse_kid_from_access_token(access_token)

    # fetch public keys by making Http request to jwks url
    response = RestUtil.request_with_retry(
        verify_ssl=True).get(iam_public_keys_url)
    if response.ok:
        return _parse_cloud_pubkey(response.json(), kid)
    else:
        raise Exception("Failed while getting IAM public keys.")


@alru_cache(maxsize=1024, ttl=7200)
async def get_cloud_pubkey_async(access_token: str, iam_public_keys_url: str, client_session: ClientSession | None = None):
    kid = _parse_kid_from_access_token(access_token)
    retry_client = RestAsyncUtil.get_retry_client(
        client_session=client_session)
    try:
        response = await retry_client.get(iam_public_keys_url)
        response.raise_for_status()
        return _parse_cloud_pubkey(await response.json(), kid)
    except Exception as _:
        raise Exception("Failed while getting IAM public keys.")
    finally:
        if not client_session:
            await retry_client.close()


cpd_pubkey_cache_lock = RLock()


@cached(cache=TTLCache(maxsize=1024, ttl=7200), lock=cpd_pubkey_cache_lock)
def get_cpd_pubkey(iam_public_keys_url):
    # fetch public keys by making Http request to jwks url
    response = RestUtil.request_with_retry(
        verify_ssl=False).get(iam_public_keys_url)
    if response.ok:
        return response.content.decode("utf-8")

    raise Exception("Failed while getting IAM public keys.")


@alru_cache(maxsize=1024, ttl=7200)
async def get_cpd_pubkey_async(iam_public_keys_url: str, client_session: ClientSession | None = None):
    retry_client = RestAsyncUtil.get_retry_client(
        client_session=client_session)
    try:
        response = await retry_client.get(iam_public_keys_url, ssl=False)
        response.raise_for_status()
        return await response.json()
    except Exception as _:
        raise Exception("Failed while getting IAM public keys.")
    finally:
        if not client_session:
            await retry_client.close()
