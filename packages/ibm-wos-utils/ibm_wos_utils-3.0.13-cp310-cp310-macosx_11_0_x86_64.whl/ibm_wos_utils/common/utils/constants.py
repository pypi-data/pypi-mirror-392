# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-B7T
# ©Copyright IBM Corp. 2025
# The source code for this program is not published or otherwise divested of its trade secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

from enum import Enum


class ContainerType(Enum):
    PROJECT = "project"
    SPACE = "space"
    WXO = "wxo"

SUPPORTED_CONTAINER_TYPES = [c.value for c in ContainerType]
