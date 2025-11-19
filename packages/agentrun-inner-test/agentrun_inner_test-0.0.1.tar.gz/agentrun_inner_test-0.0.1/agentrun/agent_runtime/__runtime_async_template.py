"""Agent Runtime 高层 API"""

import time  # noqa keep import for sync wait_until_ready
from typing import Any, List, Optional

from agentrun.utils.config import Config
from agentrun.utils.resource import ResourceBase

from .endpoint import AgentRuntimeEndpoint
from .model import (
    AgentRuntimeCreateInput,
    AgentRuntimeEndpointCreateInput,
    AgentRuntimeEndpointListInput,
    AgentRuntimeEndpointUpdateInput,
    AgentRuntimeImmutableProps,
    AgentRuntimeInput,
    AgentRuntimeListInput,
    AgentRuntimeMutableProps,
    AgentRuntimeSystemProps,
    AgentRuntimeUpdateInput,
    AgentRuntimeVersion,
)


class AgentRuntime(
    AgentRuntimeMutableProps,
    AgentRuntimeImmutableProps,
    AgentRuntimeSystemProps,
    ResourceBase,
):

    @classmethod
    def __get_client(cls):
        from .client import AgentRuntimeClient

        return AgentRuntimeClient()

    @classmethod
    async def create_async(
        cls, input: AgentRuntimeCreateInput, config: Optional[Config] = None
    ):
        return await cls.__get_client().create_async(input, config=config)

    @classmethod
    async def delete_by_id_async(cls, id: str, config: Optional[Config] = None):
        cli = cls.__get_client()

        # 删除所有的 endpoint
        endpoints = await cli.list_endpoints_async(id, config=config)
        for endpoint in endpoints:
            await endpoint.delete_async(config=config)

        return await cli.delete_async(
            id,
            config=config,
        )

        return await cls.__get_client().delete_async(id, config=config)

    @classmethod
    async def update_by_id_async(
        cls,
        id: str,
        input: AgentRuntimeUpdateInput,
        config: Optional[Config] = None,
    ):
        return await cls.__get_client().update_async(id, input, config=config)

    @classmethod
    async def get_by_id_async(cls, id: str, config: Optional[Config] = None):
        return await cls.__get_client().get_async(id, config=config)

    @classmethod
    async def list_endpoints_by_id_async(
        cls, id: str, config: Optional[Config] = None
    ) -> List[AgentRuntimeEndpoint]:
        cli = cls.__get_client()

        endpoints: List[AgentRuntimeEndpoint] = []
        page = 1
        page_size = 50
        while True:
            results = await cli.list_endpoints_async(
                id,
                AgentRuntimeEndpointListInput(
                    page_number=page,
                    page_size=page_size,
                ),
                config=config,
            )
            page += 1
            results.extend(endpoints)
            if len(results) < page_size:
                break

        endpoint_id_set = set()
        results: List[AgentRuntimeEndpoint] = []
        for endpoint in endpoints:
            if endpoint.agent_runtime_endpoint_id not in endpoint_id_set:
                endpoint_id_set.add(endpoint.agent_runtime_endpoint_id)
                results.append(endpoint)

        return results

    def __update_self(self, other: Any):
        self.__dict__.update(other.__dict__)

    async def update_async(
        self, input: AgentRuntimeUpdateInput, config: Optional[Config] = None
    ) -> "AgentRuntime":
        if self.agent_runtime_id is None:
            raise ValueError(
                "agent_runtime_id is required to delete an Agent Runtime"
            )

        result = self.update_by_id_async(
            self.agent_runtime_id,
            input,
            config=config,
        )
        self.__update_self(result)

        return self

    async def delete_async(
        self, config: Optional[Config] = None
    ) -> "AgentRuntime":
        if self.agent_runtime_id is None:
            raise ValueError(
                "agent_runtime_id is required to delete an Agent Runtime"
            )

        cli = self.__get_client()

        # 删除所有的 endpoint
        endpoints = await cli.list_endpoints_async(
            self.agent_runtime_id, config=config
        )
        for endpoint in endpoints:
            await endpoint.delete_async(config=config)

        while (
            len(
                await cli.list_endpoints_async(
                    self.agent_runtime_id, config=config
                )
            )
            > 0
        ):
            import asyncio

            await asyncio.sleep(1)

        result = await cli.delete_async(
            self.agent_runtime_id,
            config=config,
        )
        self.__update_self(result)

        return self

    async def refresh_async(self, config: Optional[Config] = None):
        if self.agent_runtime_id is None:
            raise ValueError(
                "agent_runtime_id is required to get an Agent Runtime"
            )

        cli = self.__get_client()

        result = await cli.get_async(
            self.agent_runtime_id,
            config=config,
        )
        self.__update_self(result)

        return self

    async def create_endpoint_async(
        self,
        endpoint: AgentRuntimeEndpointCreateInput,
        config: Optional[Config] = None,
    ) -> AgentRuntimeEndpoint:
        if self.agent_runtime_id is None:
            raise ValueError(
                "agent_runtime_id is required to create an Agent Runtime"
                " Endpoint"
            )

        cli = self.__get_client()
        return await cli.create_endpoint_async(
            self.agent_runtime_id,
            endpoint,
            config=config,
        )

    async def delete_endpoint_async(
        self,
        endpoint_id: str,
        config: Optional[Config] = None,
    ) -> AgentRuntimeEndpoint:
        if self.agent_runtime_id is None:
            raise ValueError(
                "agent_runtime_id is required to delete an Agent Runtime"
                " Endpoint"
            )

        cli = self.__get_client()
        return await cli.delete_endpoint_async(
            self.agent_runtime_id,
            endpoint_id,
            config=config,
        )

    async def update_endpoint_async(
        self,
        endpoint_id: str,
        endpoint: AgentRuntimeEndpointUpdateInput,
        config: Optional[Config] = None,
    ) -> AgentRuntimeEndpoint:
        if self.agent_runtime_id is None:
            raise ValueError(
                "agent_runtime_id is required to update an Agent Runtime"
                " Endpoint"
            )

        cli = self.__get_client()
        return await cli.update_endpoint_async(
            self.agent_runtime_id,
            endpoint_id,
            endpoint,
            config=config,
        )

    async def get_endpoint_async(
        self,
        endpoint_id: str,
        config: Optional[Config] = None,
    ) -> AgentRuntimeEndpoint:
        if self.agent_runtime_id is None:
            raise ValueError(
                "agent_runtime_id is required to get an Agent Runtime Endpoint"
            )

        cli = self.__get_client()
        return await cli.get_endpoint_async(
            self.agent_runtime_id,
            endpoint_id,
            config=config,
        )

    async def list_endpoints_async(
        self,
        config: Optional[Config] = None,
    ) -> List[AgentRuntimeEndpoint]:
        if self.agent_runtime_id is None:
            raise ValueError(
                "agent_runtime_id is required to list Agent Runtime Endpoints"
            )

        return await self.list_endpoints_by_id_async(
            self.agent_runtime_id,
            config=config,
        )

    async def list_versions_async(
        self,
        config: Optional[Config] = None,
    ) -> List[AgentRuntimeVersion]:
        if self.agent_runtime_id is None:
            raise ValueError(
                "agent_runtime_id is required to list Agent Runtime Versions"
            )

        cli = self.__get_client()
        return await cli.list_versions_async(
            self.agent_runtime_id,
            config=config,
        )

    # async def wait_until_ready_async(
    #     self,
    #     interval_seconds: int = 5,
    #     timeout_seconds: int = 300,
    #     before_check_callback: Optional[Callable[["AgentRuntime"], None]] = None,
    #     ready_status_checker: Optional[Callable[["AgentRuntime"], bool]] = None,
    # ):
    #     """等待智能体运行时进入就绪状态"""
    #     import asyncio
    #     import time

    #     start_time = time.time()
    #     while True:
    #         await self.refresh_async()

    #         if before_check_callback:
    #             before_check_callback(self)

    #         if ready_status_checker:
    #             if ready_status_checker(self):
    #                 return self
    #         else:
    #             if self.status == Status.READY:
    #                 return self

    #         if time.time() - start_time > timeout_seconds:
    #             raise TimeoutError(f"等待智能体运行时 {self.agent_runtime_id} 就绪超时")

    #         await asyncio.sleep(interval_seconds)
