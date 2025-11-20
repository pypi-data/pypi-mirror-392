from __future__ import annotations

from typing import Optional

import grpc

from ameide_sdk.generated.ameide_core_proto.agents.v1 import agents_pb2_grpc as agents_grpc
from ameide_sdk.generated.ameide_core_proto.agents_runtime.v1 import agents_runtime_service_pb2_grpc as agents_runtime_grpc
from ameide_sdk.generated.ameide_core_proto.governance.v1 import governance_service_pb2_grpc as governance_grpc
from ameide_sdk.generated.ameide_core_proto.graph.v1 import graph_service_pb2_grpc as graph_grpc
from ameide_sdk.generated.ameide_core_proto.inference.v1 import inference_service_pb2_grpc as inference_grpc
from ameide_sdk.generated.ameide_core_proto.platform.v1 import invitations_pb2_grpc as invitations_grpc
from ameide_sdk.generated.ameide_core_proto.platform.v1 import organizations_pb2_grpc as organizations_grpc
from ameide_sdk.generated.ameide_core_proto.platform.v1 import roles_pb2_grpc as roles_grpc
from ameide_sdk.generated.ameide_core_proto.platform.v1 import teams_pb2_grpc as teams_grpc
from ameide_sdk.generated.ameide_core_proto.platform.v1 import tenants_pb2_grpc as tenants_grpc
from ameide_sdk.generated.ameide_core_proto.platform.v1 import users_pb2_grpc as users_grpc
from ameide_sdk.generated.ameide_core_proto.threads.v1 import threads_service_pb2_grpc as threads_grpc
from ameide_sdk.generated.ameide_core_proto.transformation.v1 import transformation_service_pb2_grpc as transformation_grpc
from ameide_sdk.generated.ameide_core_proto.workflows_runtime.v1 import workflows_service_pb2_grpc as workflows_grpc

from .config import SDKOptions
from .interceptors import auth_interceptor, metadata_interceptor, timeout_interceptor
from .retry import wrap_stub_with_retry


class AmeideClient:
    """High level client exposing strongly typed stubs for platform services."""

    def __init__(self, options: Optional[SDKOptions] = None) -> None:
        self._options = options or SDKOptions()
        self._channel = self._create_channel()
        self.agents = self._wrap_stub(agents_grpc.AgentsServiceStub)
        self.organizations = self._wrap_stub(organizations_grpc.OrganizationServiceStub)
        self.organization_roles = self._wrap_stub(roles_grpc.OrganizationRoleServiceStub)
        self.teams = self._wrap_stub(teams_grpc.TeamServiceStub)
        self.users = self._wrap_stub(users_grpc.UserServiceStub)
        self.invitations = self._wrap_stub(invitations_grpc.InvitationServiceStub)
        self.tenants = self._wrap_stub(tenants_grpc.TenantServiceStub)
        self.graph = self._wrap_stub(graph_grpc.GraphServiceStub)
        self.transformation = self._wrap_stub(transformation_grpc.TransformationServiceStub)
        self.inference = self._wrap_stub(inference_grpc.InferenceServiceStub)
        self.agents_runtime = self._wrap_stub(agents_runtime_grpc.AgentsRuntimeServiceStub)
        self.governance = self._wrap_stub(governance_grpc.GovernanceServiceStub)
        self.threads = self._wrap_stub(threads_grpc.ThreadsServiceStub)
        self.workflows = self._wrap_stub(workflows_grpc.WorkflowServiceStub)

    def close(self) -> None:
        self._channel.close()

    def _create_channel(self) -> grpc.Channel:
        opts = self._options
        target = opts.endpoint
        channel_opts = [
            ("grpc.max_send_message_length", 16 * 1024 * 1024),
            ("grpc.max_receive_message_length", 16 * 1024 * 1024),
        ]

        if opts.secure:
            base_channel: grpc.Channel = grpc.secure_channel(target, grpc.ssl_channel_credentials(), options=channel_opts)
        else:
            base_channel = grpc.insecure_channel(target, options=channel_opts)

        built_in = [
            metadata_interceptor(opts),
            auth_interceptor(opts.auth),
            timeout_interceptor(opts.timeout),
        ]
        interceptors = [interceptor for interceptor in built_in if interceptor]
        if opts.interceptors:
            interceptors.extend(opts.interceptors)

        if interceptors:
            return grpc.intercept_channel(base_channel, *interceptors)
        return base_channel

    def _wrap_stub(self, factory):
        stub = factory(self._channel)
        return wrap_stub_with_retry(stub, self._options.retry)
