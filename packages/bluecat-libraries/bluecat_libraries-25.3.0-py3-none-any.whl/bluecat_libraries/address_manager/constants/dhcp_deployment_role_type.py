# Copyright 2025 BlueCat Networks (USA) Inc. and its affiliates and licensors. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Values used in the DHCP Deployment Role API methods in BlueCat Address Manager."""
from ._enum import StrEnum


class DHCPDeploymentRoleType(StrEnum):
    """DHCP Deployment Role Type"""

    NONE = "NONE"
    MASTER = "MASTER"
