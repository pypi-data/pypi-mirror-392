# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
#
# This file holds the HubConnector class which is used to connect to a Cegal Hub Server and provide a set of tasks that can be executed 
# through the Hub Server. The HubConnector class manages a connection to Hub and handles requests and deliveres responses to the Hub instance. 
# Connection parameters and information is specified in the constructor of the HubConnector class, whilst tasks are made available through 
# the HubTaskRegistry that is passed to it as an argument to the start method.
#
# The connection to Hub, and handling of responses and requests are handled on an seperate thread that runs _do_connector_tasks in an indefinite 
# loop.
#
# Requests from hub are yielded from an iterator set up by calling connector_task_stub.DoConnectorTasks, whilst responses from the connector 
# are delivered by emplacing them in the _response_q Queue.


import inspect
from typing import Dict, Iterable

import os
import threading
import socket
import sys
import time
import queue
import traceback

from multiprocessing.pool import ThreadPool

import grpc

from . import logger
from .capability import TaskType
from .connection_parameters import ConnectionParameters
from .connector_task_service_pb2 import CONNECTOR_UNARY, CONNECTOR_STREAMING, Connect, ConnectorResponse, ConnectorTaskResult
from .connector_task_service_pb2_grpc import ConnectorTaskServiceStub
from .hub_channel import HubChannel
from .server_service_pb2_grpc import ServerServiceStub
from .server_service_pb2 import CancellationEventsRequest
from .task_registry import HubTaskRegistry
from .threadsafe import ConcurrentDictionary, CooperativeCancellationToken

class NotCancellable():
    pass

class TaskContext():
    def __init__(self, major_version = None, minor_version = None, cancellation_token = None, metadata = None):
        self.major_version = major_version
        self.minor_version = minor_version
        self.cancellation_token = cancellation_token
        self.metadata = metadata

def _create_success_result(rpc_type, request_id, payload):
    task_result = ConnectorTaskResult()
    task_result.request_id = request_id
    task_result.rpc_type = rpc_type
    task_result.logical_request_completed = True
    task_result.ok = True
    task_result.payload.Pack(payload)
    return task_result

def _create_failure_result(rpc_type, request_id, error_message, is_complete: bool = True):
    task_result = ConnectorTaskResult()
    task_result.request_id = request_id
    task_result.rpc_type = rpc_type
    task_result.logical_request_completed = is_complete
    task_result.ok = False
    task_result.error_message = error_message
    return task_result

def _create_streaming_result(rpc_type, request_id, payload, is_complete):
    task_result = ConnectorTaskResult()
    task_result.request_id = request_id
    task_result.rpc_type = rpc_type
    task_result.logical_request_completed = is_complete
    task_result.ok = True
    if payload:
        task_result.payload.Pack(payload)
    return task_result


def _get_hub_user_identity(metadata: Dict[str, str]) -> str:
    if 'identity' in metadata.keys():
        return metadata['identity']
    else:   
        return "anonymous"


def handle_unary_task(task_registry, response_q, connectorTask, task_cancel_dict):
    logger.info(f"Start Unary: Identity: '{_get_hub_user_identity(connectorTask.metadata)}' Request: {connectorTask.request_id} Task: {connectorTask.payload_identifier} ")
    task = task_registry.get_unary_task(connectorTask.payload_identifier)
    if task:
        sig = inspect.signature(task)
        if 'ctx' in sig.parameters:
            cancellation_token = task_cancel_dict.set_if_not_present(connectorTask.request_id, CooperativeCancellationToken())
            ctx = TaskContext(connectorTask.payload_major_version, connectorTask.payload_minor_version, cancellation_token, connectorTask.metadata)
            result = task(ctx, connectorTask.payload)
        else:
            task_cancel_dict.set_if_not_present(connectorTask.request_id, NotCancellable())
            result = task(connectorTask.payload)
        logger.debug(f"Unary result: {result}")
        if result[0]:
            task_result = _create_success_result(connectorTask.rpc_type, connectorTask.request_id, result[1])
        else:
            task_result = _create_failure_result(connectorTask.rpc_type, connectorTask.request_id, result[2])
    response_q.put(task_result)
    task_cancel_dict.remove(connectorTask.request_id)
    logger.info(f"Complete Unary: Identity: '{_get_hub_user_identity(connectorTask.metadata)}' Request: {connectorTask.request_id} Task: {connectorTask.payload_identifier} ")


def handle_server_streaming(task_registry, connectorTask, response_q, task_cancel_dict):
    logger.info(f"Start ServerStreaming: Identity: '{_get_hub_user_identity(connectorTask.metadata)}' Request: {connectorTask.request_id} Task: {connectorTask.payload_identifier} ")
    task = task_registry.get_server_streaming_task(connectorTask.payload_identifier)
    if task:
        sig = inspect.signature(task)
        if 'ctx' in sig.parameters:
            cancellation_token = task_cancel_dict.set_if_not_present(connectorTask.request_id, CooperativeCancellationToken())
            ctx = TaskContext(connectorTask.payload_major_version, connectorTask.payload_minor_version, cancellation_token, connectorTask.metadata)
            result_it = task(ctx, connectorTask.payload)
        else:
            task_cancel_dict.set_if_not_present(connectorTask.request_id, NotCancellable())
            result_it = task(connectorTask.payload)
        for result in result_it:
            logger.debug(f"Streaming result: {result}")
            if result[0]:
                task_result = _create_streaming_result(connectorTask.rpc_type, connectorTask.request_id, result[2], result[1])
            else:
                task_result = _create_failure_result(connectorTask.rpc_type, connectorTask.request_id, result[3], result[1])
            response_q.put(task_result)
        logger.debug("Stream complete")
    else:
        logger.warning(f"payload_identifier {connectorTask.payload_identifier} not recognised")
        task_result = _create_failure_result(connectorTask.rpc_type, connectorTask.request_id, "Server streaming not supported")
        response_q.put(task_result)
    task_cancel_dict.remove(connectorTask.request_id)
    logger.info(f"Finish ServerStreaming: Identity: '{_get_hub_user_identity(connectorTask.metadata)}' Request: {connectorTask.request_id} Task: {connectorTask.payload_identifier} ")

class _HubConnectorSession():
    """A generic HubConnector which can be extended by concrete implementations. This API is considered experimental.

    Args:
        HubChannel ([HubChannel]): A HubChannel object which defines the connection to a Cegal Hub Server

    """

    def __init__(self, wellknown_identifier: str,
                 friendly_name: str,
                 description: str,
                 version: str,
                 build_version: str,
                 connection_parameters: ConnectionParameters = None,
                 token_provider=None,
                 join_token: str = "",
                 supports_public_requests: bool = False,
                 additional_labels: Dict[str, str] = None,
                 num_of_concurrent_tasks: int = 1):
        self._response_q = queue.Queue()
        self._wellknown_identifier = wellknown_identifier
        self._friendly_name = friendly_name
        self._description = description
        self._version = version
        self._build_version = build_version
        self._connection_parameters = connection_parameters
        self._token_provider = token_provider
        self._join_token = join_token
        self._supports_public_requests = supports_public_requests
        self._additional_labels = additional_labels
        self._num_of_concurrent_tasks = num_of_concurrent_tasks
        self._reconnect_id = ""
        self._lock = threading.Lock()
        self._cancellation_stream_iterator = None
        self._do_connector_tasks_iterator = None


    def start(self, task_registry: HubTaskRegistry):
        logger.debug("Starting DoConnectorTask")
        self._task_cancel_dict = ConcurrentDictionary()
        connector_id_queue = queue.Queue()
        self._stop = threading.Event()
        self._connector_task_thread = threading.Thread(target=self._do_connector_tasks,args=(task_registry,connector_id_queue), daemon=True)
        self._cancellation_subscription_thread = threading.Thread(target=self._subscribe_to_cancellations, args=(connector_id_queue,), daemon=True)
        self._connector_task_thread.start()
        self._cancellation_subscription_thread.start()
        while self._connector_task_thread.is_alive():
            time.sleep(0.1)
        self.stop()


    def stop(self):
        with self._lock:
            self._stop.set()
            if self._cancellation_stream_iterator is not None:
                self._cancellation_stream_iterator.cancel()
            if self._do_connector_tasks_iterator is not None:
                self._do_connector_tasks_iterator.cancel()


    @property
    def cancellation_stream_iterator(self):
        with self._lock:
            return self._cancellation_stream_iterator
        

    @cancellation_stream_iterator.setter
    def cancellation_stream_iterator(self, value):
        with self._lock:
            self._cancellation_stream_iterator = value


    @property
    def do_connector_tasks_iterator(self):
        with self._lock:
            return self._do_connector_tasks_iterator
        

    @do_connector_tasks_iterator.setter
    def do_connector_tasks_iterator(self, value):
        with self._lock:
            self._do_connector_tasks_iterator = value


    def _create_initial_message(self, task_registry: HubTaskRegistry):
        try:
            hostname = os.environ["HOSTNAME"]
        except Exception:
            hostname = socket.gethostname()

        connectorInfo = Connect()
        connectorInfo.wellknown_identifier = self._wellknown_identifier
        connectorInfo.friendly_name = self._friendly_name
        connectorInfo.description = self._description
        connectorInfo.host_name = hostname
        connectorInfo.operating_system = sys.platform
        connectorInfo.version = self._version
        connectorInfo.build_version = self._build_version
        connectorInfo.supports_public_requests = self._supports_public_requests
        connectorInfo.join_token = self._join_token
        connectorInfo.reconnect_id = self._reconnect_id
        
        for task in task_registry.get_supported_tasks():
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].wellknown_payload_identifier = task.wellknown_payload_identifier
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].friendly_name = task.friendly_name
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].description = task.description
            if task.task_type == TaskType.UNARY:
                connectorInfo.supported_payloads[task.wellknown_payload_identifier].supported_rpc_types.append(CONNECTOR_UNARY)
            elif task.task_type == TaskType.SERVER_STREAMING:
                connectorInfo.supported_payloads[task.wellknown_payload_identifier].supported_rpc_types.append(CONNECTOR_STREAMING)
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].major_version = task.major_version
            connectorInfo.supported_payloads[task.wellknown_payload_identifier].minor_version = task.minor_version
            if task.payload_auth is not None:
                for audience in task.payload_auth.required_audiences:
                    connectorInfo.supported_payloads[task.wellknown_payload_identifier].auth.required_audience.append(audience)
                for claim in task.payload_auth.required_app_claims:
                    connectorInfo.supported_payloads[task.wellknown_payload_identifier].auth.required_blueback_app_claims.append(claim)

        if self._additional_labels:
            for key in self._additional_labels.keys():
                connectorInfo.labels[key] = self._additional_labels[key]
        return connectorInfo


    def _connector_tasks_iterator(self, task_registry) -> Iterable[ConnectorResponse]:
        info = self._create_initial_message(task_registry)
        initial_response = ConnectorResponse(connect=info)
        yield initial_response

        try:
            while True:
                try:
                    task_result = self._response_q.get(block=True, timeout=2)
                    response = ConnectorResponse(task_result=task_result)
                    yield response
                    self._response_q.task_done()
                except queue.Empty:
                    if self._done is True:
                        return  
        except Exception as error:
            logger.error(f"_connector_tasks_iterator: {error}")

        logger.debug("Clearing response q")
        with self._response_q.mutex:
            self._response_q.queue.clear()
            self._response_q.all_tasks_done.notify_all()
            self._response_q.unfinished_tasks = 0
        logger.debug("Cleared response q")



    def _do_connector_tasks(self, task_registry: HubTaskRegistry, connector_id_queue: queue.Queue):
        try:
            sem = threading.Semaphore(self._num_of_concurrent_tasks)
            pool = ThreadPool(processes=self._num_of_concurrent_tasks)
            logger.info("Registering connector with Cegal Hub")
            hubChannel = HubChannel(self._connection_parameters, self._token_provider)
            connector_task_stub = ConnectorTaskServiceStub(hubChannel._channel)
            self._done = False
            self.do_connector_tasks_iterator = connector_task_stub.DoConnectorTasks(self._connector_tasks_iterator(task_registry))

            # This is a blocking call, can be cancelled by calling self.stop from another thread
            for connectorTask in self.do_connector_tasks_iterator:
                    if connectorTask.acknowledge_connector_joined:
                        self._reconnect_id = connectorTask.connector_id
                        connector_id_queue.put(connectorTask.connector_id)
                        logger.info("Successfully connected")
                        continue
                    
                    logger.debug(f"Task {connectorTask.payload_identifier} {connectorTask.request_id}")

                    if connectorTask.rpc_type == CONNECTOR_UNARY:
                        sem.acquire()
                        pool.apply_async(handle_unary_task, args=(task_registry, self._response_q, connectorTask, self._task_cancel_dict), callback=lambda x: sem.release())
                    elif connectorTask.rpc_type == CONNECTOR_STREAMING:
                        sem.acquire()
                        pool.apply_async(handle_server_streaming, args=(task_registry, connectorTask, self._response_q, self._task_cancel_dict), callback=lambda x: sem.release())
                    else:
                        logger.error(f"Unknown RpcType {connectorTask}")
                        task_result = self._create_failure_result(connectorTask.rpc_type, connectorTask.request_id, "Unknown rpc type")
                        self._response_q.put(task_result)
        except Exception as error:
            logger.error(f"_do_connector_tasks: {error}: {error.args}")
            logger.error(f"_do_connector_tasks: {traceback.format_exc()}")
            self._done = True
        finally:
            logger.debug("Clearing response q")
            with self._response_q.mutex:
                self._response_q.queue.clear()
                self._response_q.all_tasks_done.notify_all()
                self._response_q.unfinished_tasks = 0
            logger.debug("Cleared response q")
            logger.debug(f"Completed with {len(self._task_cancel_dict)} unfinished tasks.")
            hubChannel.close()
            pool.close()
            self._stop.set()

    def _subscribe_to_cancellations(self, connector_id_queue: queue.Queue):
        # We need the connector id, it is set at the first message from do_connector_tasks endpoint
        # lets wait until we get it. Cancel if stop is set.
        connector_id = None
        while connector_id is None:
            try:
                connector_id = connector_id_queue.get(block=True, timeout=2)
            except queue.Empty:
                if self._stop.is_set():
                    return

        try:
            logger.info("Attempting to connect to Cegal Hub")
            hubChannel = HubChannel(self._connection_parameters, self._token_provider)
            server_service_stub = ServerServiceStub(hubChannel._channel)

            cancellation_events_request = CancellationEventsRequest(connector_id=connector_id)
            self.cancellation_stream_iterator = server_service_stub.GetCancellationEvents(cancellation_events_request)

            # This is a blocking call, can be cancelled by calling self.stop from another thread
            for connectorTask in self.cancellation_stream_iterator:
                cancellation_token = self._task_cancel_dict.get(connectorTask.request_id)
                if isinstance(cancellation_token, CooperativeCancellationToken):
                    cancellation_token.cancel()
                    logger.info(f"\033[92m Cancellation request for {connectorTask.request_id} acknowledged \033[00m")
                elif isinstance(cancellation_token, NotCancellable):
                    logger.info(f"\033[91m Cancellation request for {connectorTask.request_id} not supported \033[00m")
                else:
                    logger.info(f"\033[93m Cancellation request for {connectorTask.request_id} not found \033[00m")
        except grpc._channel._MultiThreadedRendezvous as error:
            if error.cancelled():
                logger.info("_subscribe_to_cancellations: Cancelled")
            else:
                logger.error(f"_subscribe_to_cancellations: {error}: {error.args}")
                logger.error(f"_subscribe_to_cancellations: {traceback.format_exc()}")
        except Exception as error:
            logger.error(f"_subscribe_to_cancellations: {error}: {error.args}")
            logger.error(f"_subscribe_to_cancellations: {traceback.format_exc()}")
        finally:
            hubChannel.close()


class HubConnector():
    """A generic HubConnector which can be extended by concrete implementations. This API is considered experimental.

    Args:
        HubChannel ([HubChannel]): A HubChannel object which defines the connection to a Cegal Hub Server

    """

    def __init__(self, 
                 wellknown_identifier: str,
                 friendly_name: str,
                 description: str,
                 version: str,
                 build_version: str,
                 connection_parameters: ConnectionParameters = None,
                 token_provider=None,
                 join_token: str = "",
                 supports_public_requests: bool = False,
                 additional_labels: Dict[str, str] = None,
                 num_of_concurrent_tasks: int = 1):
        self._kw = { 
                        "wellknown_identifier":wellknown_identifier,
                        "friendly_name":friendly_name,
                        "description":description,
                        "version":version,
                        "build_version":build_version,
                        "connection_parameters":connection_parameters,
                        "token_provider":token_provider,
                        "join_token":join_token,
                        "supports_public_requests":supports_public_requests,
                        "additional_labels":additional_labels,
                        "num_of_concurrent_tasks":num_of_concurrent_tasks
                }


    def start(self, task_registry: HubTaskRegistry, auto_reconnect=True):
        while True:
            self._session = _HubConnectorSession(**self._kw)
            self._session.start(task_registry)
            if not auto_reconnect:
                break
            time.sleep(10)


    def stop(self):
        self._session.stop()
