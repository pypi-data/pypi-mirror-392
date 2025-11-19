"""Model Service 客户端"""

from typing import Optional

from alibabacloud_devs20230714.models import ListToolsetsRequest

from agentrun.toolset.api.control import ToolControlAPI
from agentrun.toolset.model import ToolSetListInput
from agentrun.utils.config import Config
from agentrun.utils.exception import HTTPError

from .toolset import ToolSet


class ToolSetClient:
    """Model Service 客户端"""

    def __init__(self, config: Optional[Config] = None):
        """初始化客户端

        Args:
            config: 配置
        """
        self.__control_api = ToolControlAPI(config)

    async def get_async(
        self,
        name: str,
        config: Optional[Config] = None,
    ):
        try:
            result = await self.__control_api.get_toolset_async(
                name=name,
                config=config,
            )
        except HTTPError as e:
            raise e.to_resource_error("Model", name) from e

        return ToolSet.from_inner_object(result)

    async def list_async(
        self,
        input: Optional[ToolSetListInput] = None,
        config: Optional[Config] = None,
    ):
        if input is None:
            input = ToolSetListInput()

        result = await self.__control_api.list_toolsets_async(
            input=ListToolsetsRequest().from_map(input.model_dump()),
            config=config,
        )

        return [ToolSet.from_inner_object(item) for item in result.data]
