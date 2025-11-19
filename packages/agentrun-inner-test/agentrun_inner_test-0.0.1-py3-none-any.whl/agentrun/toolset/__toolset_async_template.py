from typing import Any, Dict, Optional, Tuple

import pydash

from agentrun.utils.config import Config
from agentrun.utils.log import logger
from agentrun.utils.model import BaseModel

from .api.openapi import OpenAPI
from .model import MCPServerConfig, SchemaType, ToolSetSpec, ToolSetStatus


class ToolSet(BaseModel):
    created_time: Optional[str] = None
    description: Optional[str] = None
    generation: Optional[int] = None
    kind: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    name: Optional[str] = None
    spec: Optional[ToolSetSpec] = None
    status: Optional[ToolSetStatus] = None
    uid: Optional[str] = None

    @classmethod
    def __get_client(cls, config: Optional[Config] = None):
        from .client import ToolSetClient

        return ToolSetClient(config)

    @classmethod
    async def get_by_name_async(
        cls, name: str, config: Optional[Config] = None
    ):
        cli = cls.__get_client(config)
        return await cli.get_async(name=name)

    def type(self):
        return SchemaType(pydash.get(self, "spec.tool_schema.type", ""))

    def _get_openapi_auth_defaults(
        self,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        headers: Dict[str, Any] = {}
        query: Dict[str, Any] = {}

        auth_config = pydash.get(self, "spec.auth_config", None)
        auth_type = getattr(auth_config, "type", None) if auth_config else None

        if auth_type == "APIKey":
            api_key_param = pydash.get(
                auth_config,
                "parameters.api_key_parameter",
                None,
            )
            if api_key_param:
                key = getattr(api_key_param, "key", None)
                value = getattr(api_key_param, "value", None)
                location = getattr(api_key_param, "in_", None)
                if key and value is not None:
                    if location == "header":
                        headers[key] = value
                    elif location == "query":
                        query[key] = value

        return headers, query

    def _get_openapi_base_url(self) -> Optional[str]:
        return pydash.get(
            self,
            "status.outputs.urls.intranet_url",
            None,
        ) or pydash.get(self, "status.outputs.urls.internet_url", None)

    def _create_openapi_client(
        self,
        config: Optional[Config] = None,
    ) -> OpenAPI:
        schema_detail = pydash.get(self, "spec.tool_schema.detail", None)
        if not schema_detail:
            raise ValueError("OpenAPI schema detail is missing.")

        headers, query = self._get_openapi_auth_defaults()

        return OpenAPI(
            schema=schema_detail,
            base_url=self._get_openapi_base_url(),
            headers=headers,
            query_params=query,
            config=config,
        )

    def _resolve_openapi_operation_name(
        self,
        client: OpenAPI,
        name: str,
    ) -> str:
        if client.has_tool(name):
            return name

        openapi_tools = (
            pydash.get(
                self,
                "status.outputs.open_api_tools",
                [],
            )
            or []
        )

        for tool_meta in openapi_tools:
            if tool_meta is None:
                continue

            if hasattr(tool_meta, "model_dump"):
                meta = tool_meta.model_dump(exclude_none=True)
            elif isinstance(tool_meta, dict):
                meta = tool_meta
            else:
                meta = {
                    key: getattr(tool_meta, key)
                    for key in dir(tool_meta)
                    if not key.startswith("_")
                    and not callable(getattr(tool_meta, key))
                }

            candidates = [
                meta.get("tool_id"),
                meta.get("tool_name"),
                meta.get("operationId"),
            ]
            if name in candidates:
                for candidate in candidates:
                    if candidate and client.has_tool(candidate):
                        return candidate

                method = meta.get("method")
                path = meta.get("path")
                if method and path:
                    for item in client.list_tools():
                        if (
                            item.get("method") == method
                            and item.get("path") == path
                        ):
                            operation_id = item.get("operationId")
                            if operation_id:
                                return operation_id

        return name

    async def get_async(self, config: Optional[Config] = None):
        if self.name is None:
            raise ValueError("ToolSet name is required to get the ToolSet.")

        result = await self.get_by_name_async(name=self.name, config=config)
        return self.update_self(result)

    async def list_tools_async(self, config: Optional[Config] = None):
        if self.type() == SchemaType.MCP:
            return pydash.get(self, "status.outputs.tools", [])
        elif self.type() == SchemaType.OpenAPI:
            client = self._create_openapi_client(config=config)
            return client.list_tools()
        return []

    async def call_tool_async(
        self,
        name: str,
        arguments: Optional[Dict[str, str]] = None,
        config: Optional[Config] = None,
    ):
        if self.type() == SchemaType.MCP:
            from .api.mcp import MCPToolSet

            mcp_server_config: MCPServerConfig = pydash.get(
                self, "status.outputs.mcp_server_config", None
            )
            assert (
                mcp_server_config.url is not None
            ), "MCP server URL is missing."

            cfg = Config.with_configs(
                config, Config(headers=mcp_server_config.headers)
            )

            toolset_client = MCPToolSet(
                url=mcp_server_config.url,
                config=cfg,
            )

            logger.debug(
                "invoke mcp tool %s with arguments %s", name, arguments
            )
            result = await toolset_client.call_tool_async(
                name=name,
                arguments=arguments,
            )
            logger.debug("invoke mcp tool %s got result %s", name, result)

            return result
        elif self.type() == SchemaType.OpenAPI:
            client = self._create_openapi_client(config=config)
            operation_name = self._resolve_openapi_operation_name(
                client,
                name,
            )

            logger.debug(
                "invoke openapi tool %s with arguments %s",
                operation_name,
                arguments,
            )
            result = await client.invoke_tool_async(
                name=operation_name,
                arguments=arguments,
                config=config,
            )
            logger.debug("invoke openapi tool %s got result %s", name, result)
            return result
        return []
