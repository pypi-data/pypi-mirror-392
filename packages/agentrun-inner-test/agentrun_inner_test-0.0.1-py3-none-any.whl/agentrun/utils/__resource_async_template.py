from abc import abstractmethod
import asyncio
import time
from typing import Awaitable, Callable, Optional

from typing_extensions import Self

from agentrun.utils.config import Config
from agentrun.utils.exception import DeleteResourceError, ResourceNotExistError
from agentrun.utils.log import logger

from .model import BaseModel, Status


class ResourceBase(BaseModel):
    status: Optional[Status] = None
    _config: Optional[Config] = None

    @abstractmethod
    async def refresh_async(self, config: Optional[Config] = None) -> Self:
        ...

    @abstractmethod
    async def delete_async(self, config: Optional[Config] = None) -> Self:
        ...

    async def __wait_until_async(
        self,
        check_finished_callback_async: Callable[[Self], Awaitable[bool]],
        interval_seconds: int = 5,
        timeout_seconds: int = 300,
    ) -> Self:
        """等待智能体运行时进入就绪状态"""

        start_time = time.time()
        while True:
            if await check_finished_callback_async(self):
                return self

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("等待就绪超时")

            await asyncio.sleep(interval_seconds)

    async def wait_until_ready_or_failed_async(
        self,
        callback: Optional[Callable[[Self], None]] = None,
        interval_seconds: int = 5,
        timeout_seconds: int = 300,
    ):
        """等待智能体运行时进入就绪状态"""

        async def check_ready_callback(resource: Self) -> bool:
            await resource.refresh_async()
            if callback:
                callback(resource)
            logger.debug("当前状态：%s", resource.status)

            return Status.is_final_status(resource.status)

        await self.__wait_until_async(
            check_ready_callback,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
        )

    async def delete_and_wait_until_finished_async(
        self,
        callback: Optional[Callable[[Self], None]] = None,
        interval_seconds: int = 5,
        timeout_seconds: int = 300,
    ):
        """等待智能体运行时被删除"""

        await self.delete_async()

        async def check_deleted_callback(resource: Self) -> bool:
            try:
                await resource.refresh_async()
                if callback:
                    callback(resource)
            except ResourceNotExistError:
                return True

            if resource.status == Status.DELETING:
                return False

            raise DeleteResourceError(f"Resource status is {resource.status}")

        await self.__wait_until_async(
            check_deleted_callback,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
        )

    def set_config(self, config: Config) -> Self:
        """设置配置

        Args:
            config: 配置

        Returns:
            Self: 当前对象
        """
        self._config = config
        return self
