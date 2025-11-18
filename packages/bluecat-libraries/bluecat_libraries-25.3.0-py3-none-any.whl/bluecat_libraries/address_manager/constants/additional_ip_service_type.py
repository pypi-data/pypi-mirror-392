# Copyright 2025 BlueCat Networks (USA) Inc. and its affiliates and licensors. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Values used in the additional IP address API methods. in BlueCat Address Manager."""
from ._enum import StrEnum


class AdditionalIPServiceType(StrEnum):
    """Additional IP Service Type"""

    LOOPBACK = "loopback"
    SERVICE = "service"
