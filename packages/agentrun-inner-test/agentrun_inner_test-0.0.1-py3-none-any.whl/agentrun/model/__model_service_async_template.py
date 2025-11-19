"""Model Service 高层 API"""

from typing import Any, Optional

from agentrun.model.api.data import ModelCompletionAPI
from agentrun.utils.config import Config
from agentrun.utils.model import Status
from agentrun.utils.resource import ResourceBase

from .model import (
    BackendType,
    ModelServiceCreateInput,
    ModelServiceImmutableProps,
    ModelServiceMutableProps,
    ModelServicesSystemProps,
    ModelServiceUpdateInput,
)


class ModelService(
    ModelServiceImmutableProps,
    ModelServiceMutableProps,
    ModelServicesSystemProps,
    ResourceBase,
):
    """模型服务"""

    @classmethod
    def __get_client(cls):
        from .client import ModelClient

        return ModelClient()

    @classmethod
    async def create_async(
        cls, input: ModelServiceCreateInput, config: Optional[Config] = None
    ):
        """创建模型服务（异步）

        Args:
            input: 模型服务输入参数
            config: 配置

        Returns:
            ModelService: 创建的模型服务对象
        """
        return await cls.__get_client().create_async(input, config=config)

    @classmethod
    async def delete_by_name_async(
        cls, model_service_name: str, config: Optional[Config] = None
    ):
        """根据名称删除模型服务（异步）

        Args:
            model_service_name: 模型服务名称
            config: 配置
        """
        return await cls.__get_client().delete_async(
            model_service_name, backend_type=BackendType.SERVICE, config=config
        )

    @classmethod
    async def update_by_name_async(
        cls,
        model_service_name: str,
        input: ModelServiceUpdateInput,
        config: Optional[Config] = None,
    ):
        """根据名称更新模型服务（异步）

        Args:
            model_service_name: 模型服务名称
            input: 模型服务更新输入参数
            config: 配置

        Returns:
            ModelService: 更新后的模型服务对象
        """
        return await cls.__get_client().update_async(
            model_service_name, input, config=config
        )

    @classmethod
    async def get_by_name_async(
        cls, model_service_name: str, config: Optional[Config] = None
    ):
        """根据名称获取模型服务（异步）

        Args:
            model_service_name: 模型服务名称
            config: 配置

        Returns:
            ModelService: 模型服务对象
        """
        return await cls.__get_client().get_async(
            model_service_name, backend_type=BackendType.SERVICE, config=config
        )

    def __update_self(self, other: Any):
        """更新自身属性"""
        self.__dict__.update(other.__dict__)

    async def update_async(
        self, input: ModelServiceUpdateInput, config: Optional[Config] = None
    ):
        """更新模型服务（异步）

        Args:
            input: 模型服务更新输入参数
            config: 配置

        Returns:
            ModelService: 更新后的模型服务对象
        """
        if self.model_service_name is None:
            raise ValueError(
                "model_service_name is required to update a ModelService"
            )

        result = await self.update_by_name_async(
            self.model_service_name, input, config=config
        )
        self.__update_self(result)

        return self

    async def delete_async(self, config: Optional[Config] = None):
        """删除模型服务（异步）

        Args:
            config: 配置
        """
        if self.model_service_name is None:
            raise ValueError(
                "model_service_name is required to delete a ModelService"
            )

        return await self.delete_by_name_async(
            self.model_service_name, config=config
        )

    async def refresh_async(self, config: Optional[Config] = None):
        """刷新模型服务信息（异步）

        Args:
            config: 配置

        Returns:
            ModelService: 刷新后的模型服务对象
        """
        if self.model_service_name is None:
            raise ValueError(
                "model_service_name is required to refresh a ModelService"
            )

        result = await self.get_by_name_async(
            self.model_service_name, config=config
        )
        self.__update_self(result)

        return self

    async def wait_until_ready_async(
        self,
        interval_seconds: int = 5,
        timeout_seconds: int = 300,
    ):
        """等待模型服务进入就绪状态（异步）

        Args:
            interval_seconds: 检查间隔（秒）
            timeout_seconds: 超时时间（秒）

        Returns:
            ModelService: 就绪后的模型服务对象

        Raises:
            TimeoutError: 等待超时
        """
        import asyncio
        import time

        start_time = time.time()
        while True:
            await self.refresh_async()

            if self.status == Status.READY:
                return self

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(
                    f"等待模型服务 {self.model_service_name} 就绪超时"
                )

            await asyncio.sleep(interval_seconds)

    def completions(
        self,
        messages: list,
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ):
        assert self.provider_settings is not None
        assert self.provider_settings.base_url is not None

        default_model = (
            self.provider_settings.model_names[0]
            if self.provider_settings.model_names is not None
            and len(self.provider_settings.model_names) > 0
            else model
        )
        assert default_model is not None

        m = ModelCompletionAPI(
            api_key=self.provider_settings.api_key or "",
            base_url=self.provider_settings.base_url,
            model=default_model,
        )

        return m.completions(**kwargs, messages=messages, stream=stream)

    def responses(
        self,
        messages: list,
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ):
        assert self.provider_settings is not None
        assert self.provider_settings.base_url is not None

        default_model = (
            self.provider_settings.model_names[0]
            if self.provider_settings.model_names is not None
            and len(self.provider_settings.model_names) > 0
            else model
        )
        assert default_model is not None

        m = ModelCompletionAPI(
            api_key=self.provider_settings.api_key or "",
            base_url=self.provider_settings.base_url,
            model=default_model,
        )

        return m.responses(**kwargs, messages=messages, stream=stream)
