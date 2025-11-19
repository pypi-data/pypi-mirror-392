# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import collections
import grpc

from .client_config import ClientConfig
from .generic_client_interceptor import create


class _ClientCallDetails(
        collections.namedtuple(
            '_ClientCallDetails',
            ('method', 'timeout', 'metadata', 'credentials')),
        grpc.ClientCallDetails):
    pass


def impersonation_header_interceptor():

    def intercept_call(client_call_details, request_iterator, request_streaming,
                       response_streaming):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        if ClientConfig.get_user_impersonation_token() is not None:
            metadata.append((
                "impersonationid",
                ClientConfig.get_user_impersonation_token(),
            ))
        client_call_details = _ClientCallDetails(
            client_call_details.method, client_call_details.timeout, metadata,
            client_call_details.credentials)
        return client_call_details, request_iterator, None

    return create(intercept_call)
