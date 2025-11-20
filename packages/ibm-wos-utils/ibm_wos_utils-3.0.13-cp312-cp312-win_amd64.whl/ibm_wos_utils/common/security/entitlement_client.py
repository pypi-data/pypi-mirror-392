# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023, 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from aiohttp import ClientSession

from ibm_wos_utils.joblib.utils.environment import Environment as Env
from ibm_wos_utils.joblib.utils.python_utils import get
from ibm_wos_utils.joblib.utils.rest_async_util import RestAsyncUtil
from ibm_wos_utils.joblib.utils.rest_util import RestUtil


class EntitlementClient:

    def __init__(self, bearer_token, data_mart_id, accept_language, project_id, space_id, enable_task_credentials=None, container_type=None, container_id=None, client_session: ClientSession | None = None):
        self.bearer_token = bearer_token
        self.data_mart_id = data_mart_id
        self.project_id = project_id
        self.space_id = space_id
        self.accept_language = accept_language
        self.container_type = container_type
        self.container_id = container_id
        self.entitlements_url = "{}/v1/entitlements".format(
            Env.get_gateway_url())
        self.enable_task_credentials = enable_task_credentials
        self.client_session = client_session

    def _parse_entitlements(self, entitlements_json):
        entitlements = []
        os_entitlements = get(
            entitlements_json, "entitlements.ai_openscale", None)
        if os_entitlements:
            entitlements = [
                i for i in os_entitlements if i.get("id") == self.data_mart_id]
            if not entitlements:
                entitlements = [i for i in os_entitlements if i.get(
                    "service_instance_guid") == self.data_mart_id]

        if len(entitlements) == 0:
            raise Exception("The user entitlement does not exist.")

        return entitlements[0]

    def _get_entitlement_url(self):
        query_params = self.__get_query_params()
        return "{}?{}".format(self.entitlements_url, query_params)

    async def get_entitlement_async(self):
        retry_client = RestAsyncUtil.get_retry_client(
            client_session=self.client_session)
        try:
            response = await retry_client.get(
                self._get_entitlement_url(),
                headers=self.__get_headers(),
            )
            response.raise_for_status()
            return self._parse_entitlements(await response.json())
        except Exception as _:
            raise Exception("Failed while getting user entitlement.")
        finally:
            if not self.client_session:
                await retry_client.close()

    def get_entitlement(self):
        url = self._get_entitlement_url()
        response = RestUtil.request_with_retry(verify_ssl=True).get(url,
                                                                    headers=self.__get_headers())
        if not response.ok:
            raise Exception("Failed while getting user entitlement.")

        return self._parse_entitlements(response.json())

    def __get_query_params(self):
        query_params = [
            "instance_id="+self.data_mart_id
        ]
        if self.project_id:
            query_params.append("project_id="+self.project_id)
        if self.space_id:
            query_params.append("space_id="+self.space_id)
        if self.enable_task_credentials:
            query_params.append("enable_task_credentials=" +
                                str(self.enable_task_credentials).lower())
        if self.container_type:
            query_params.append("container_type="+self.container_type)
        if self.container_id:
            query_params.append("container_id="+self.container_id)
        return "&".join(query_params)

    def __get_headers(self):
        headers = {"Authorization": self.bearer_token,
                   "Accept": "application/json",
                   "Content-Type": "application/json",
                   "Accept-Language": self.accept_language}
        return headers
