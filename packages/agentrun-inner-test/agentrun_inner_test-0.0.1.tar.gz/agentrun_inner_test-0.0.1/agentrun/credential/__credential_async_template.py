"""Credential 高层 API"""

from typing import Any, Optional

from agentrun.utils.config import Config
from agentrun.utils.resource import ResourceBase

from .model import (
    CredentialCreateInput,
    CredentialImmutableProps,
    CredentialMutableProps,
    CredentialSystemProps,
    CredentialUpdateInput,
)


class Credential(
    CredentialMutableProps,
    CredentialImmutableProps,
    CredentialSystemProps,
    ResourceBase,
):
    """凭证"""

    @classmethod
    def __get_client(cls):
        from .client import CredentialClient

        return CredentialClient()

    @classmethod
    async def create_async(
        cls, input: CredentialCreateInput, config: Optional[Config] = None
    ):
        """创建凭证（异步）

        Args:
            input: 凭证输入参数
            config: 配置

        Returns:
            Credential: 创建的凭证对象
        """
        return await cls.__get_client().create_async(input, config=config)

    @classmethod
    async def delete_by_name_async(
        cls, credential_name: str, config: Optional[Config] = None
    ):
        """根据名称删除凭证（异步）

        Args:
            credential_name: 凭证名称
            config: 配置
        """
        return await cls.__get_client().delete_async(
            credential_name, config=config
        )

    @classmethod
    async def update_by_name_async(
        cls,
        credential_name: str,
        input: CredentialUpdateInput,
        config: Optional[Config] = None,
    ):
        """根据名称更新凭证（异步）

        Args:
            credential_name: 凭证名称
            input: 凭证更新输入参数
            config: 配置

        Returns:
            Credential: 更新后的凭证对象
        """
        return await cls.__get_client().update_async(
            credential_name, input, config=config
        )

    @classmethod
    async def get_by_name_async(
        cls, credential_name: str, config: Optional[Config] = None
    ):
        """根据名称获取凭证（异步）

        Args:
            credential_name: 凭证名称
            config: 配置

        Returns:
            Credential: 凭证对象
        """
        return await cls.__get_client().get_async(
            credential_name, config=config
        )

    def __update_self(self, other: Any):
        """更新自身属性"""
        self.__dict__.update(other.__dict__)

    async def update_async(
        self, input: CredentialUpdateInput, config: Optional[Config] = None
    ):
        """更新凭证（异步）

        Args:
            input: 凭证更新输入参数
            config: 配置

        Returns:
            Credential: 更新后的凭证对象
        """
        if self.credential_name is None:
            raise ValueError(
                "credential_name is required to update a Credential"
            )

        result = await self.update_by_name_async(
            self.credential_name, input, config=config
        )
        self.__update_self(result)

        return self

    async def delete_async(self, config: Optional[Config] = None):
        """删除凭证（异步）

        Args:
            config: 配置
        """
        if self.credential_name is None:
            raise ValueError(
                "credential_name is required to delete a Credential"
            )

        return await self.delete_by_name_async(
            self.credential_name, config=config
        )

    async def refresh_async(self, config: Optional[Config] = None):
        """刷新凭证信息（异步）

        Args:
            config: 配置

        Returns:
            Credential: 刷新后的凭证对象
        """
        if self.credential_name is None:
            raise ValueError(
                "credential_name is required to refresh a Credential"
            )

        result = await self.get_by_name_async(
            self.credential_name, config=config
        )
        self.__update_self(result)

        return self
