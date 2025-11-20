# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023, 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from aiohttp import ClientSession
from ibm_wos_utils.common.activity_tracking.activity_tracker import ActivityTracker
from ibm_wos_utils.common.utils.constants import SUPPORTED_CONTAINER_TYPES
from ibm_wos_utils.joblib.exceptions.client_errors import BadRequestError
from ibm_wos_utils.joblib.utils.environment import Environment as Env
from ibm_wos_utils.common.security.authenticator import Authenticator
from ibm_wos_utils.common.security.user import User
from ibm_wos_utils.common.security.entitlement_client import EntitlementClient


class Auth:
    """Class to validate the user and user permissions for the operation.

    Arguments:
        data_mart_id: The data mart id. Not required when authenticating service users.
        request: The request object. Below attributes are used from the request object
            endpoint: The request endpoint
            method: The HTTP request method
            headers: The HTTP request headers
            args: The arguments from URL
        endpoints_roles_map: The dictionary with request endpoint as key and roles permission as value
            Eg: {
                    "api.ExplanationTasks_explanation_tasks": {
                        "permissions": {
                            "administrator": ["get","post", "put","delete"],
                            "editor": ["get", "put", "delete"],
                            "viewer": ["get"]
                        }
                    }
                }
        service_ids_allowlist: The list of service ids allowed to perform the operation
        environment: The environment variables dictionary. Can be passed instead of setting in the environment
        Environment variables to be set
        ENABLE_ICP
        IAM_PUBLIC_KEYS_URL: Required if ENABLE_ICP is false
        ICP4D_JWT_PUBLIC_KEY_URL: Required if ENABLE_ICP is true
        AIOS_GATEWAY_URL
    """

    def __init__(self, request, endpoints_roles_map, service_ids_allowlist, data_mart_id: str | None = None, environment={}, is_fast_api: bool = False, client_session: ClientSession | None = None) -> None:
        self.data_mart_id = data_mart_id
        self.request_method = request.method
        if is_fast_api:
            self.request_endpoint = request.url.path
            self.request_path = request.url.path
        else:
            self.request_endpoint = request.endpoint
            self.request_path = request.path
        self.request_user_agent = request.headers.get("user-agent")
        if is_fast_api:
            self.bearer_token = request.headers.get("authorization")
        else:
            self.bearer_token = request.headers.get("Authorization")
        self.delegated_by = request.headers.get("X-IBM-DELEGATED-BY")
        self.accept_language = request.headers.get("Accept-Language", "en")
        if is_fast_api:
            query_params = request.query_params._dict
            self.project_id = query_params.get("project_id")
            self.space_id = query_params.get("space_id")
            self.container_type = query_params.get("container_type")
            self.container_id = query_params.get("container_id")
        else:
            self.project_id = request.args.get("project_id")
            self.space_id = request.args.get("space_id")
            self.container_type = request.args.get("container_type")
            self.container_id = request.args.get("container_id")
        self.endpoints_roles_map = endpoints_roles_map or {}
        self.service_ids_allowlist = service_ids_allowlist or []
        self.activity_tracker = ActivityTracker(
            self.data_mart_id, client_session=client_session)
        self._client_session = client_session
        Env.set_environment(environment)

    def validate(self):
        """Validate the user and user permissions"""
        user = self.authenticate()
        return self.authorize(user=user)

    async def validate_async(self):
        """Validate the user and user permissions"""
        user = await self.authenticate_async()
        return await self.authorize_async(user=user)

    def authenticate(self):
        """Validates the user and returns the User object."""
        authenticator = Authenticator(
            self.bearer_token, client_session=self._client_session)
        return User(authenticator.authenticate())

    async def authenticate_async(self):
        """Validates the user and returns the User object."""
        authenticator = Authenticator(
            self.bearer_token, client_session=self._client_session)
        return User(await authenticator.authenticate_async())

    def _validate_project_or_space_id(self):
        if self.project_id and self.space_id:
            raise Exception(
                "Both the project id and space id are provided in the request. Please provide only one of them.")

        # Validate container_type
        if self.container_type:
            if self.container_type not in SUPPORTED_CONTAINER_TYPES:
                raise BadRequestError(
                    f"Unsupported container_type '{self.container_type}' specified. Supported container types are {SUPPORTED_CONTAINER_TYPES}.")

            if not self.container_id:
                raise BadRequestError(
                    "Required query parameter 'container_id' is missing in the request.")

    def _authorize_service_id(self, user):
        if not Env.is_cpd():
            if not (self.service_ids_allowlist and user.sub in self.service_ids_allowlist):
                raise Exception("The service user is not authorized.")

    def _log_authorization_failed_in_activity_tracker(self, user, error):
        self.activity_tracker.log(user, "auth", "authorize", False,
                                  str(error), "ibm-wos-utils-api", "failed",
                                  self.request_path, self.request_method, 401, self.request_user_agent)

    async def _log_authorization_failed_in_activity_tracker_async(self, user, error):
        await self.activity_tracker.log_async(user, "auth", "authorize", False,
                                              str(error), "ibm-wos-utils-api", "failed",
                                              self.request_path, self.request_method, 401, self.request_user_agent)

    def authorize(self, user):
        """Validate the user permissions and return the User object."""
        try:
            self._validate_project_or_space_id()

            if user.is_service_id:
                self._authorize_service_id(user)
            else:
                # Datamart id is required for users authorization
                if not self.data_mart_id:
                    raise ValueError("The data mart id value is invalid.")

                self.__is_user_entitled(
                    bearer_token=self.bearer_token, user=user)

        except Exception as e:
            self._log_authorization_failed_in_activity_tracker(user, e)
            raise e

        return user

    async def authorize_async(self, user):
        """Validate the user permissions and return the User object."""
        try:
            self._validate_project_or_space_id()

            if user.is_service_id:
                self._authorize_service_id(user)
            else:
                # Datamart id is required for users authorization
                if not self.data_mart_id:
                    raise ValueError("The data mart id value is invalid.")

                await self.__is_user_entitled_async(
                    bearer_token=self.bearer_token, user=user)

        except Exception as e:
            await self._log_authorization_failed_in_activity_tracker_async(user, e)
            raise e

        return user

    @property
    def request_method(self):
        return self.__request_method

    @request_method.setter
    def request_method(self, request_method):
        if not request_method:
            raise ValueError("The request method value is invalid.")

        self.__request_method = request_method

    @property
    def request_endpoint(self):
        return self.__request_endpoint

    @request_endpoint.setter
    def request_endpoint(self, request_endpoint):
        if not request_endpoint:
            raise ValueError("The request endpoint value is invalid.")

        self.__request_endpoint = request_endpoint

    @property
    def bearer_token(self):
        return self.__bearer_token

    @bearer_token.setter
    def bearer_token(self, bearer_token):
        if not bearer_token:
            raise ValueError("The bearer token value is invalid.")

        self.__bearer_token = bearer_token

    def _parse_user_entitlement(self, user, entitlement):
        endpoint_roles_map = self.endpoints_roles_map.get(
            self.request_endpoint) or {}
        endpoint_permissions = endpoint_roles_map.get("permissions") or {}
        allowed_methods = []
        for r in entitlement.get("roles"):
            role_permissions = endpoint_permissions.get(r.lower()) or []
            allowed_methods.extend(role_permissions)

        if self.request_method.lower() not in set(allowed_methods):
            raise Exception("The user is not authorized.")

        # Update user object with details from entitlement
        user.plan_name = entitlement.get("plan_name")
        user.crn = entitlement.get("crn")
        user.plan_id = entitlement.get("plan_id")

    def __is_user_entitled(self, bearer_token, user):
        entitlement_client = EntitlementClient(bearer_token=bearer_token,
                                               data_mart_id=self.data_mart_id,
                                               accept_language=self.accept_language,
                                               project_id=self.project_id,
                                               space_id=self.space_id,
                                               enable_task_credentials=Env.get_property_value(
                                                   "ENABLE_TASK_CREDENTIALS"),
                                               container_type=self.container_type,
                                               container_id=self.container_id)
        entitlement = entitlement_client.get_entitlement()
        self._parse_user_entitlement(user, entitlement)

    async def __is_user_entitled_async(self, bearer_token, user):
        entitlement_client = EntitlementClient(bearer_token=bearer_token,
                                               data_mart_id=self.data_mart_id,
                                               accept_language=self.accept_language,
                                               project_id=self.project_id,
                                               space_id=self.space_id,
                                               enable_task_credentials=Env.get_property_value(
                                                   "ENABLE_TASK_CREDENTIALS"),
                                               container_type=self.container_type,
                                               container_id=self.container_id,
                                               client_session=self._client_session,
                                               )
        entitlement = await entitlement_client.get_entitlement_async()
        self._parse_user_entitlement(user, entitlement)
