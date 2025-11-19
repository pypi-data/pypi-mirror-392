from enum import Enum
from typing import Any, Dict, List, Optional

from agentrun.utils.model import BaseModel, Field, PageableInput


class SchemaType(str, Enum):
    MCP = "MCP"
    OpenAPI = "OpenAPI"


class ToolSetStatusOutputsUrls(BaseModel):
    internet_url: Optional[str] = None
    intranet_url: Optional[str] = None


class MCPServerConfig(BaseModel):
    headers: Optional[Dict[str, str]] = None
    transport_type: Optional[str] = None
    url: Optional[str] = None


class ToolMeta(BaseModel):
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    name: Optional[str] = None


class OpenAPIToolMeta(BaseModel):
    method: Optional[str] = None
    path: Optional[str] = None
    tool_id: Optional[str] = None
    tool_name: Optional[str] = None


class ToolSetStatusOutputs(BaseModel):
    function_arn: Optional[str] = None
    mcp_server_config: Optional[MCPServerConfig] = None
    open_api_tools: Optional[List[OpenAPIToolMeta]] = None
    tools: Optional[List[ToolMeta]] = None
    urls: Optional[ToolSetStatusOutputsUrls] = None


class APIKeyAuthParameter(BaseModel):
    encrypted: Optional[bool] = None
    in_: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None


class AuthorizationParameters(BaseModel):
    api_key_parameter: Optional[APIKeyAuthParameter] = None


class Authorization(BaseModel):
    parameters: Optional[AuthorizationParameters] = None
    type: Optional[str] = None


class ToolSetSchema(BaseModel):
    detail: Optional[str] = None
    type: Optional[SchemaType] = None


class ToolSetSpec(BaseModel):
    auth_config: Optional[Authorization] = None
    tool_schema: Optional[ToolSetSchema] = Field(alias="schema", default=None)


class ToolSetStatus(BaseModel):
    observed_generation: Optional[int] = None
    observed_time: Optional[str] = None
    outputs: Optional[ToolSetStatusOutputs] = None
    phase: Optional[str] = None


class ToolSetListInput(PageableInput):
    keyword: Optional[str] = None
    label_selector: Optional[List[str]] = None
