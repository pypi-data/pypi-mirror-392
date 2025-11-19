from typing import List, Optional

from alibabacloud_agentrun20250910.models import (
    CreateAgentRuntimeEndpointInput,
    ListAgentRuntimeEndpointsRequest,
    ListAgentRuntimeVersionsRequest,
    UpdateAgentRuntimeEndpointInput,
)

from agentrun.agent_runtime.model import (
    AgentRuntimeArtifact,
    AgentRuntimeCreateInput,
    AgentRuntimeEndpointCreateInput,
    AgentRuntimeEndpointListInput,
    AgentRuntimeEndpointUpdateInput,
    AgentRuntimeListInput,
    AgentRuntimeUpdateInput,
    AgentRuntimeVersion,
    NetworkConfig,
)
from agentrun.agent_runtime.runtime import AgentRuntime
from agentrun.utils.config import Config
from agentrun.utils.exception import HTTPError

from .api.control import (
    AgentRuntimeControlAPI,
    CreateAgentRuntimeInput,
    GetAgentRuntimeRequest,
    ListAgentRuntimesRequest,
    UpdateAgentRuntimeInput,
)
from .endpoint import AgentRuntimeEndpoint


class AgentRuntimeClient:

    def __init__(self, config: Optional[Config] = None):
        self.__control_api = AgentRuntimeControlAPI(config)

    async def create_async(
        self, input: AgentRuntimeCreateInput, config: Optional[Config] = None
    ) -> AgentRuntime:
        if input.network_configuration is None:
            input.network_configuration = NetworkConfig()

        if input.artifact_type is None:
            if input.code_configuration is not None:
                input.artifact_type = AgentRuntimeArtifact.CODE
            elif input.container_configuration is not None:
                input.artifact_type = AgentRuntimeArtifact.CONTAINER
            else:
                raise ValueError(
                    "Either code_configuration or image_configuration must be"
                    " provided."
                )

        try:
            result = await self.__control_api.create_agent_runtime_async(
                CreateAgentRuntimeInput().from_map(input.model_dump()),
                config=config,
            )
        except HTTPError as e:
            raise e.to_resource_error(
                "AgentRuntime", input.agent_runtime_name
            ) from e
        return AgentRuntime.from_inner_object(result)

    async def delete_async(
        self, id: str, config: Optional[Config] = None
    ) -> AgentRuntime:
        try:
            result = await self.__control_api.delete_agent_runtime_async(
                id, config=config
            )
            return AgentRuntime.from_inner_object(result)
        except HTTPError as e:
            raise e.to_resource_error("AgentRuntime", id) from e

    async def update_async(
        self,
        id: str,
        input: AgentRuntimeUpdateInput,
        config: Optional[Config] = None,
    ) -> AgentRuntime:
        try:
            result = await self.__control_api.update_agent_runtime_async(
                id,
                UpdateAgentRuntimeInput().from_map(input.model_dump()),
                config=config,
            )
            return AgentRuntime.from_inner_object(result)
        except HTTPError as e:
            raise e.to_resource_error("AgentRuntime", id) from e

    async def get_async(
        self,
        id: str,
        config: Optional[Config] = None,
    ) -> AgentRuntime:
        try:
            result = await self.__control_api.get_agent_runtime_async(
                id, GetAgentRuntimeRequest(), config=config
            )
            return AgentRuntime.from_inner_object(result)
        except HTTPError as e:
            raise e.to_resource_error("AgentRuntime", id) from e

    async def list_async(
        self,
        input: Optional[AgentRuntimeListInput] = None,
        config: Optional[Config] = None,
    ) -> List[AgentRuntime]:
        if input is None:
            input = AgentRuntimeListInput()

        results = await self.__control_api.list_agent_runtimes_async(
            ListAgentRuntimesRequest().from_map(input.model_dump()),
            config=config,
        )
        return [AgentRuntime.from_inner_object(item) for item in results.items]

    async def create_endpoint_async(
        self,
        agent_runtime_id: str,
        endpoint: AgentRuntimeEndpointCreateInput,
        config: Optional[Config] = None,
    ) -> AgentRuntimeEndpoint:
        try:
            result = (
                await self.__control_api.create_agent_runtime_endpoint_async(
                    agent_runtime_id,
                    CreateAgentRuntimeEndpointInput().from_map(
                        endpoint.model_dump()
                    ),
                    config=config,
                )
            )
        except HTTPError as e:
            raise e.to_resource_error(
                "AgentRuntimeEndpoint",
                "/".join([
                    agent_runtime_id,
                    endpoint.agent_runtime_endpoint_name or "",
                ]),
            ) from e

        return AgentRuntimeEndpoint.from_inner_object(result)

    async def delete_endpoint_async(
        self,
        agent_runtime_id: str,
        endpoint_id: str,
        config: Optional[Config] = None,
    ) -> AgentRuntimeEndpoint:
        try:
            result = (
                await self.__control_api.delete_agent_runtime_endpoint_async(
                    agent_runtime_id,
                    endpoint_id,
                    config=config,
                )
            )
        except HTTPError as e:
            raise e.to_resource_error(
                "AgentRuntimeEndpoint",
                "/".join([
                    agent_runtime_id,
                    endpoint_id,
                ]),
            ) from e

        return AgentRuntimeEndpoint.from_inner_object(result)

    async def update_endpoint_async(
        self,
        agent_runtime_id: str,
        endpoint_id: str,
        endpoint: AgentRuntimeEndpointUpdateInput,
        config: Optional[Config] = None,
    ) -> AgentRuntimeEndpoint:
        try:
            result = (
                await self.__control_api.update_agent_runtime_endpoint_async(
                    agent_runtime_id,
                    endpoint_id,
                    UpdateAgentRuntimeEndpointInput().from_map(
                        endpoint.model_dump()
                    ),
                    config=config,
                )
            )
        except HTTPError as e:
            raise e.to_resource_error(
                "AgentRuntimeEndpoint",
                "/".join([
                    agent_runtime_id,
                    endpoint_id,
                ]),
            ) from e

        return AgentRuntimeEndpoint.from_inner_object(result)

    async def get_endpoint_async(
        self,
        agent_runtime_id: str,
        endpoint_id: str,
        config: Optional[Config] = None,
    ) -> AgentRuntimeEndpoint:
        try:
            result = await self.__control_api.get_agent_runtime_endpoint_async(
                agent_runtime_id,
                endpoint_id,
                config=config,
            )
        except HTTPError as e:
            raise e.to_resource_error(
                "AgentRuntimeEndpoint",
                "/".join([
                    agent_runtime_id,
                    endpoint_id,
                ]),
            ) from e

        return AgentRuntimeEndpoint.from_inner_object(result)

    async def list_endpoints_async(
        self,
        agent_runtime_id: str,
        input: Optional[AgentRuntimeEndpointListInput] = None,
        config: Optional[Config] = None,
    ) -> List[AgentRuntimeEndpoint]:
        if input is None:
            input = AgentRuntimeEndpointListInput()

        results = await self.__control_api.list_agent_runtime_endpoints_async(
            agent_runtime_id,
            ListAgentRuntimeEndpointsRequest().from_map(input.model_dump()),
            config=config,
        )
        return [
            AgentRuntimeEndpoint.from_inner_object(item)
            for item in results.items
        ]

    async def list_versions_async(
        self,
        agent_runtime_id: str,
        input: Optional[AgentRuntimeListInput] = None,
        config: Optional[Config] = None,
    ) -> List[AgentRuntimeVersion]:
        if input is None:
            input = AgentRuntimeListInput()

        results = await self.__control_api.list_agent_runtime_versions_async(
            agent_runtime_id,
            ListAgentRuntimeVersionsRequest().from_map(input.model_dump()),
            config=config,
        )
        return [
            AgentRuntimeVersion.from_inner_object(item)
            for item in results.items
        ]
