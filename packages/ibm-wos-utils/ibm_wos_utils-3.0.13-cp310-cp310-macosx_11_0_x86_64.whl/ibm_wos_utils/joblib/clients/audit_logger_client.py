# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import logging
import ssl
from typing import Any

from aiohttp import ClientResponseError, ClientSession

from ibm_wos_utils.joblib.utils.environment import Environment as Env
from ibm_wos_utils.joblib.utils.rest_async_util import RestAsyncUtil
from ibm_wos_utils.joblib.utils.rest_util import RestUtil

logging.basicConfig(
    format="%(message)s", level=logging.INFO,)


class AuditLoggerClient():
    """
    Client class to call Audit Logger APIs.
    """

    def __init__(self, client_session: ClientSession | None = None):
        self.audit_svc_url = "{}/records".format(Env.get_gateway_url())
        self._client_session = client_session

    def log_event(self, payload: dict) -> None:
        """
        Makes the call to log event in Audit Logger in CPD.
        :payload: The event payload to log.

        :returns: None.
        """

        # Generating the headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Making the call
        response = RestUtil.request_with_retry().post(
            self.audit_svc_url,
            json=payload,
            headers=headers,
            cert=(Env.get_tls_cert(), Env.get_tls_cert_key())
        )
        if not response.ok:
            logging.error("Failed to audit log event {}. Error status code: {}".format(
                payload["action"], response.status_code))

        return

    async def log_event_async(self, payload: dict[str, Any]) -> None:
        """
        Makes the call to log event in Audit Logger in CPD.
        :payload: The event payload to log.

        :returns: None.
        """

        # Generating the headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        retry_client = RestAsyncUtil.get_retry_client(
            client_session=self._client_session)
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_cert_chain(
            certfile=Env.get_tls_cert(), keyfile=Env.get_tls_cert_key())
        try:
            response = await retry_client.post(
                self.audit_svc_url,
                headers=headers,
                json=payload,
                ssl=ssl_context,
            )
            response.raise_for_status()

        except ClientResponseError as e:
            logging.error("Failed to audit log event {}. Error status code: {}".format(
                payload["action"], e.status))
        except Exception as e:
            logging.error("Failed to audit log event {}. Error {}".format(
                payload["action"], e))
        finally:
            if not self._client_session:
                await retry_client.close()

        return
