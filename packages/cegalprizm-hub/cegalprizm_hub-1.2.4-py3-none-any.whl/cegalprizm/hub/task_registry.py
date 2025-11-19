# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
#
# This file contains the HubTaskRegistry class which is used to register tasks that Hub clients can execute by
# by sending requests to the Hub Connector holding this task registry. The HubTaskRegistry holds registered hub tasks
# that are identified by their wellknown_payload_identifier. The tasks are represented as HubCapabilities. The HubTaskRegistry
# methods enable caller to:
# * Register tasks
# * Retrieve tasks


from types import FunctionType
from typing import Dict, Iterator, Tuple

from . import logger
from .capability import HubCapability, TaskType
from .payload_auth import PayloadAuth


class HubTaskRegistry:

    def __init__(self):
        self._supported_tasks: Dict[str, HubCapability] = {}

    def register_unary_task(self,
                            wellknown_payload_identifier: str,
                            task: FunctionType,
                            friendly_name: str,
                            description: str,
                            payload_auth: PayloadAuth,
                            major_version: int = 0,
                            minor_version: int = 0) -> Tuple[bool, str]:
        capability = HubCapability(TaskType.UNARY, wellknown_payload_identifier, task, friendly_name, description, payload_auth, major_version, minor_version)
        self._supported_tasks[wellknown_payload_identifier] = capability

    def register_server_streaming_task(self,
                                       wellknown_payload_identifier: str,
                                       task: FunctionType,
                                       friendly_name: str,
                                       description: str,
                                       payload_auth: PayloadAuth,
                                       major_version: int = 0,
                                       minor_version: int = 0) -> Tuple[bool, str]:
        capability = HubCapability(TaskType.SERVER_STREAMING, wellknown_payload_identifier, task, friendly_name, description, payload_auth, major_version, minor_version)
        self._supported_tasks[wellknown_payload_identifier] = capability

    def get_supported_tasks(self) -> Iterator[HubCapability]:
        for task in self._supported_tasks.values():
            yield task

    def get_unary_task(self, wellknown_payload_identifier) -> FunctionType:
        capability = self._supported_tasks.get(wellknown_payload_identifier)
        if capability is None:
            return None
        if capability.task_type != TaskType.UNARY:
            logger.warning(f"payload_identifier {wellknown_payload_identifier} is not a UNARY task")
            return None
        return capability.task

    # def get_client_streaming_task(self, wellknown_payload_identifier) -> FunctionType:
    #     capability = self._supported_tasks.get(wellknown_payload_identifier)
    #     if capability is None:
    #         return None
    #     if capability.task_type != TaskType.CLIENT_STREAMING:
    #         logger.warning(f"payload_identifier {wellknown_payload_identifier} is not a CLIENT_STREAMING task")
    #         return None
    #     return capability.task

    def get_server_streaming_task(self, wellknown_payload_identifier) -> FunctionType:
        capability = self._supported_tasks.get(wellknown_payload_identifier)
        if capability is None:
            return None
        if capability.task_type != TaskType.SERVER_STREAMING:
            logger.warning(f"payload_identifier {wellknown_payload_identifier} is not a SERVER_STREAMING task")
            return None
        return capability.task
