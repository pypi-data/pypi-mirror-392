# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

from aiohttp import ClientSession

from ibm_wos_utils.common.activity_tracking.activity_tracker_utils import ActivityTrackerUtils, ActivityTrackingInfo
from ibm_wos_utils.common.security.user import User


class ActivityTracker:

    """
    Class for Activity tracking.

    Arguments:
    data_mart_id: The data mart id.
    client_session: optional client session for async requests.
    """

    def __init__(self, service_instance_id, client_session: ClientSession | None = None):
        self.service_instance_id = service_instance_id
        self.client_session = client_session

    def _get_activity_tracking_info(
        self,
        object_type: str,
        action_event: str,
        data_event: bool,
        message: str,
        component: str,
    ) -> ActivityTrackingInfo:
        return ActivityTrackingInfo(
            action="aiopenscale.{}.{}".format(object_type, action_event),
            data_event=data_event,
            message="Watson Openscale: {}.{} {} {}".format(object_type, action_event, component,
                                                           message)
        )

    def log(self, user: User, object_type: str, action_event: str, data_event: bool, message: str,  component: str, outcome: str, request_path: str, request_method: str, response_status_code: int, request_user_agent: str):
        """
        Logs activity for the  action.

        Arguments:
        :user: A user object for setting user details in Activity log.
        :object_type: The object-type can be quality-monitor_enable, quality-monitor_run, drift_v2-monitor_enable, drift_v2-monitor_run, etc., 
        :action_event: Action related to the activity.
        :data_event: Whether the activity is data event.
        :message: The message associated with the activity.
        :component: Which service has called this activity.
        :outcome: The outcome of the action.
        :request_path: Value of request.path.
        :request_method: Value of request.method.
        :request_user_agent: Value of the context-header user-agent.
        :response_status_code: The status code of the response.
        """

        # Initializing AT related variables
        at_event_info = self._get_activity_tracking_info(
            object_type=object_type,
            action_event=action_event,
            data_event=data_event,
            message=message,
            component=component,
        )

        # Logging the AT event
        ActivityTrackerUtils.log_event(
            at_event_info=at_event_info,
            outcome=outcome,
            status_code=response_status_code,
            user=user,
            service_instance_id=self.service_instance_id,
            request_path=request_path,
            request_method=request_method,
            request_user_agent=request_user_agent or ""
        )

    async def log_async(self, user: User, object_type: str, action_event: str, data_event: bool, message: str,  component: str, outcome: str, request_path: str, request_method: str, response_status_code: int, request_user_agent: str):
        """
        Logs activity for the  action.

        Arguments:
        :user: A user object for setting user details in Activity log.
        :object_type: The object-type can be quality-monitor_enable, quality-monitor_run, drift_v2-monitor_enable, drift_v2-monitor_run, etc., 
        :action_event: Action related to the activity.
        :data_event: Whether the activity is data event.
        :message: The message associated with the activity.
        :component: Which service has called this activity.
        :outcome: The outcome of the action.
        :request_path: Value of request.path.
        :request_method: Value of request.method.
        :request_user_agent: Value of the context-header user-agent.
        :response_status_code: The status code of the response.
        """

        # Initializing AT related variables
        at_event_info = self._get_activity_tracking_info(
            object_type=object_type,
            action_event=action_event,
            data_event=data_event,
            message=message,
            component=component,
        )

        # Logging the AT event
        await ActivityTrackerUtils.log_event_async(
            at_event_info=at_event_info,
            outcome=outcome,
            status_code=response_status_code,
            user=user,
            service_instance_id=self.service_instance_id,
            request_path=request_path,
            request_method=request_method,
            request_user_agent=request_user_agent or "",
            client_session=self.client_session,
        )
