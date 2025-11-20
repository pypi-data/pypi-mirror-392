# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from aiohttp import ClientResponseError, ClientSession

from ibm_wos_utils.joblib.exceptions.client_errors import AuthenticationError, ObjectNotFoundError, DependentServiceError
from ibm_wos_utils.joblib.utils.environment import Environment as Env
from ibm_wos_utils.joblib.utils.rest_async_util import RestAsyncUtil
from ibm_wos_utils.joblib.utils.rest_util import RestUtil


class TaskCredentialsClient:

    def __init__(self, bearer_token, account_id, iam_id, client_session: ClientSession | None = None):
        self.bearer_token = bearer_token
        self.apikey_url = "{}/openscale/v2/credentials/{}?iam_id={}".format(
            Env.get_gateway_url(), account_id, iam_id)
        self._headers = {
            "Authorization": "bearer {}".format(self.bearer_token)}
        self._client_session = client_session

    def _handle_status_code(self, status_code, response):
        if status_code == 401:
            raise AuthenticationError(
                "The credentials provided to get apiKey are invalid.", response)
        elif status_code == 404:
            raise ObjectNotFoundError(
                "ApiKey is not found", response)
        else:
            raise DependentServiceError(
                "Getting apiKey has failed", response)

    def get_apikey(self):
        response = RestUtil.request().get(url=self.apikey_url, headers=self._headers)

        if response.ok:
            apikey = response.json().get("api_key")
        else:
            self._handle_status_code(response.status_code, response)

        return apikey

    async def get_apikey_async(self):
        retry_client = RestAsyncUtil.get_retry_client(self._client_session)
        try:
            response = await retry_client.get(self.apikey_url, headers=self._headers)
            response.raise_for_status()
            json_response = await response.json()
            return json_response.get("api_key")
        except ClientResponseError as e:
            raise Exception(
                f"Failed to get task credentials api key. Status: {e.status}, Response: {e.message}")
        except Exception as e:
            raise Exception(f"Failed to get task credentials api key. {e}")
        finally:
            if not self._client_session:
                await retry_client.close()
