"""Model Proxy 高层 API"""

from typing import Any, Optional

from agentrun.model.api.data import ModelDataAPI
from agentrun.utils.config import Config
from agentrun.utils.resource import ResourceBase

from .model import (
    BackendType,
    ModelProxyCreateInput,
    ModelProxyImmutableProps,
    ModelProxyMutableProps,
    ModelProxySystemProps,
    ModelProxyUpdateInput,
)


class ModelProxy(
    ModelProxyImmutableProps,
    ModelProxyMutableProps,
    ModelProxySystemProps,
    ResourceBase,
):
    """模型服务"""

    _data_client: Optional[ModelDataAPI] = None

    @classmethod
    def __get_client(cls):
        from .client import ModelClient

        return ModelClient()

    @classmethod
    async def create_async(
        cls, input: ModelProxyCreateInput, config: Optional[Config] = None
    ):
        """创建模型服务（异步）

        Args:
            input: 模型服务输入参数
            config: 配置

        Returns:
            ModelProxy: 创建的模型服务对象
        """
        return await cls.__get_client().create_async(input, config=config)

    @classmethod
    async def delete_by_name_async(
        cls, model_Proxy_name: str, config: Optional[Config] = None
    ):
        """根据名称删除模型服务（异步）

        Args:
            model_Proxy_name: 模型服务名称
            config: 配置
        """
        return await cls.__get_client().delete_async(
            model_Proxy_name, backend_type=BackendType.PROXY, config=config
        )

    @classmethod
    async def update_by_name_async(
        cls,
        model_proxy_name: str,
        input: ModelProxyUpdateInput,
        config: Optional[Config] = None,
    ):
        """根据名称更新模型服务（异步）

        Args:
            model_Proxy_name: 模型服务名称
            input: 模型服务更新输入参数
            config: 配置

        Returns:
            ModelProxy: 更新后的模型服务对象
        """
        return await cls.__get_client().update_async(
            model_proxy_name, input, config=config
        )

    @classmethod
    async def get_by_name_async(
        cls, model_proxy_name: str, config: Optional[Config] = None
    ):
        """根据名称获取模型服务（异步）

        Args:
            model_Proxy_name: 模型服务名称
            config: 配置

        Returns:
            ModelProxy: 模型服务对象
        """
        return await cls.__get_client().get_async(
            model_proxy_name, backend_type=BackendType.PROXY, config=config
        )

    def __update_self(self, other: Any):
        """更新自身属性"""
        self.__dict__.update(other.__dict__)

    async def update_async(
        self, input: ModelProxyUpdateInput, config: Optional[Config] = None
    ):
        """更新模型服务（异步）

        Args:
            input: 模型服务更新输入参数
            config: 配置

        Returns:
            ModelProxy: 更新后的模型服务对象
        """
        if self.model_proxy_name is None:
            raise ValueError(
                "model_Proxy_name is required to update a ModelProxy"
            )

        result = await self.update_by_name_async(
            self.model_proxy_name, input, config=config
        )
        self.__update_self(result)

        return self

    async def delete_async(self, config: Optional[Config] = None):
        """删除模型服务（异步）

        Args:
            config: 配置
        """
        if self.model_proxy_name is None:
            raise ValueError(
                "model_Proxy_name is required to delete a ModelProxy"
            )

        return await self.delete_by_name_async(
            self.model_proxy_name, config=config
        )

    async def refresh_async(self, config: Optional[Config] = None):
        """刷新模型服务信息（异步）

        Args:
            config: 配置

        Returns:
            ModelProxy: 刷新后的模型服务对象
        """
        if self.model_proxy_name is None:
            raise ValueError(
                "model_Proxy_name is required to refresh a ModelProxy"
            )

        result = await self.get_by_name_async(
            self.model_proxy_name, config=config
        )
        self.__update_self(result)

        return self

    def completions(
        self,
        messages: list,
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ):
        if self._data_client is None:
            self._data_client = ModelDataAPI(
                self.model_proxy_name or "", config=self._config
            )

        if self._data_client.model_name != self.model_proxy_name:
            self._data_client.update_model_name(
                model_name=self.model_proxy_name or "", config=self._config
            )

        return self._data_client.completions(
            **kwargs, messages=messages, model=model, stream=stream
        )

    def responses(
        self,
        messages: list,
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ):
        if self._data_client is None:
            self._data_client = ModelDataAPI(
                self.model_proxy_name or "", config=self._config
            )

        if self._data_client.model_name != self.model_proxy_name:
            self._data_client.update_model_name(
                model_name=self.model_proxy_name or "", config=self._config
            )

        return self._data_client.responses(
            **kwargs, messages=messages, model=model, stream=stream
        )
