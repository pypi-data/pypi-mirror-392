# Copyright 2025 BlueCat Networks (USA) Inc. and its affiliates and licensors. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Values for traversal method used as parameters in APIs."""
from ._enum import StrEnum


class TraversalMethod(StrEnum):
    """Values for traversal method used in APIs that search through hierarchies of objects."""

    BREADTH_FIRST = "BREADTH_FIRST"
    DEPTH_FIRST = "DEPTH_FIRST"
    NO_TRAVERSAL = "NO_TRAVERSAL"
