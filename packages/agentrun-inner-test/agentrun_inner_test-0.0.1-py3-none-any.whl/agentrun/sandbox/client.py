import time
from typing import List, Optional, TYPE_CHECKING

from alibabacloud_agentrun20250910.models import (
    CreateSandboxInput,
    CreateTemplateInput,
    ListSandboxesRequest,
    ListTemplatesRequest,
    UpdateTemplateInput,
)

from agentrun.sandbox.api.sandbox_control import SandboxControlAPI
from agentrun.sandbox.api.template_control import TemplateControlAPI
from agentrun.sandbox.model import PageableInput, SandboxInput, TemplateInput
from agentrun.sandbox.sandbox import Sandbox
from agentrun.utils.config import Config
from agentrun.utils.exception import ClientError, ResourceNotExistError

if TYPE_CHECKING:
    from agentrun.sandbox.template import Template


class SandboxClient:
    """Sandbox 客户端，用于管理 Sandbox 和 Template"""

    def __init__(self, config: Optional[Config] = None):
        """初始化 Sandbox 客户端

        Args:
            config: 配置对象
        """
        self.__sandbox_control_api = SandboxControlAPI(config)
        self.__template_control_api = TemplateControlAPI(config)

    # ==================== Sandbox 相关方法 ====================

    async def create_sandbox_async(
        self, input: SandboxInput, config: Optional[Config] = None
    ) -> Sandbox:
        """创建 Sandbox（异步）

        Args:
            input: Sandbox 配置
            config: 配置对象

        Returns:
            Sandbox: 创建的 Sandbox 对象

        Raises:
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        # 转换为 SDK 需要的格式
        sdk_input = CreateSandboxInput().from_map(
            input.model_dump(by_alias=True)
        )
        result = await self.__sandbox_control_api.create_async(
            sdk_input, config=config
        )
        return Sandbox.from_inner_object(result)

    def create_sandbox(
        self, input: SandboxInput, config: Optional[Config] = None
    ) -> Sandbox:
        """创建 Sandbox（同步）

        Args:
            input: Sandbox 配置
            config: 配置对象

        Returns:
            Sandbox: 创建的 Sandbox 对象

        Raises:
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        # 转换为 SDK 需要的格式
        sdk_input = CreateSandboxInput().from_map(
            input.model_dump(by_alias=True)
        )
        result = self.__sandbox_control_api.create(sdk_input, config=config)
        return Sandbox.from_inner_object(result)

    async def get_sandbox_async(
        self, sandbox_id: str, config: Optional[Config] = None
    ) -> Sandbox:
        """获取 Sandbox（异步）

        Args:
            sandbox_id: Sandbox ID
            config: 配置对象

        Returns:
            Sandbox: Sandbox 对象

        Raises:
            ResourceNotExistError: Sandbox 不存在
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        try:
            result = await self.__sandbox_control_api.get_async(
                sandbox_id, config=config
            )
            return Sandbox.from_inner_object(result)
        except ClientError as e:
            if e.status_code == 404:
                raise ResourceNotExistError("Sandbox", sandbox_id) from e
            raise e

    def get_sandbox(
        self, sandbox_id: str, config: Optional[Config] = None
    ) -> Sandbox:
        """获取 Sandbox（同步）

        Args:
            sandbox_id: Sandbox ID
            config: 配置对象

        Returns:
            Sandbox: Sandbox 对象

        Raises:
            ResourceNotExistError: Sandbox 不存在
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        try:
            result = self.__sandbox_control_api.get(sandbox_id, config=config)
            return Sandbox.from_inner_object(result)
        except ClientError as e:
            if e.status_code == 404:
                raise ResourceNotExistError("Sandbox", sandbox_id) from e
            raise e

    async def list_sandboxes_async(
        self,
        input: Optional[PageableInput] = None,
        config: Optional[Config] = None,
    ) -> List[Sandbox]:
        """枚举 Sandboxes（异步）

        Args:
            input: 分页配置
            config: 配置对象

        Returns:
            List[Sandbox]: Sandbox 列表

        Raises:
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        if input is None:
            input = PageableInput()

        # 转换为 SDK 需要的格式
        sdk_input = ListSandboxesRequest().from_map(
            input.model_dump(by_alias=True)
        )
        results = await self.__sandbox_control_api.list_async(
            sdk_input, config=config
        )
        return [Sandbox.from_inner_object(item) for item in results.items]

    def list_sandboxes(
        self,
        input: Optional[PageableInput] = None,
        config: Optional[Config] = None,
    ) -> List[Sandbox]:
        """枚举 Sandboxes（同步）

        Args:
            input: 分页配置
            config: 配置对象

        Returns:
            List[Sandbox]: Sandbox 列表

        Raises:
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        if input is None:
            input = PageableInput()

        # 转换为 SDK 需要的格式
        sdk_input = ListSandboxesRequest().from_map(
            input.model_dump(by_alias=True)
        )
        results = self.__sandbox_control_api.list(sdk_input, config=config)
        return [Sandbox.from_inner_object(item) for item in results.items]

    async def stop_sandbox_async(
        self, sandbox_id: str, config: Optional[Config] = None
    ) -> Sandbox:
        """停止 Sandbox（异步）

        Args:
            sandbox_id: Sandbox ID
            config: 配置对象

        Returns:
            Sandbox: 停止后的 Sandbox 对象

        Raises:
            ResourceNotExistError: Sandbox 不存在
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        try:
            result = await self.__sandbox_control_api.stop_async(
                sandbox_id, config=config
            )
            return Sandbox.from_inner_object(result)
        except ClientError as e:
            if e.status_code == 404:
                raise ResourceNotExistError("Sandbox", sandbox_id) from e
            raise e

    def stop_sandbox(
        self, sandbox_id: str, config: Optional[Config] = None
    ) -> Sandbox:
        """停止 Sandbox（同步）

        Args:
            sandbox_id: Sandbox ID
            config: 配置对象

        Returns:
            Sandbox: 停止后的 Sandbox 对象

        Raises:
            ResourceNotExistError: Sandbox 不存在
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        try:
            result = self.__sandbox_control_api.stop(sandbox_id, config=config)
            return Sandbox.from_inner_object(result)
        except ClientError as e:
            if e.status_code == 404:
                raise ResourceNotExistError("Sandbox", sandbox_id) from e
            raise e

    # ==================== Template 相关方法 ====================

    def _wait_template_ready(
        self,
        template_name: str,
        config: Optional[Config] = None,
        interval_seconds: int = 5,
        timeout_seconds: int = 300,
    ) -> "Template":
        """Wait for Template to be ready (sync)

        Args:
            template_name: Template name
            config: Config object
            interval_seconds: Polling interval in seconds
            timeout_seconds: Timeout in seconds

        Returns:
            Template: Ready Template object

        Raises:
            TimeoutError: Timeout error
            ClientError: Client error
        """
        start_time = time.time()
        while True:
            template = self.get_template(template_name, config=config)

            # Check if ready
            if template.status == "READY":
                return template

            # Check if failed
            if (
                template.status == "CREATE_FAILED"
                or template.status == "UPDATE_FAILED"
            ):
                raise ClientError(
                    f"Template {template_name} creation failed, status:"
                    f" {template.status}"
                )

            # Check timeout
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(
                    f"Timeout waiting for Template {template_name} to be ready,"
                    f" current status: {template.status}"
                )

            time.sleep(interval_seconds)

    async def _wait_template_ready_async(
        self,
        template_name: str,
        config: Optional[Config] = None,
        interval_seconds: int = 5,
        timeout_seconds: int = 300,
    ) -> "Template":
        """Wait for Template to be ready (async)

        Args:
            template_name: Template name
            config: Config object
            interval_seconds: Polling interval in seconds
            timeout_seconds: Timeout in seconds

        Returns:
            Template: Ready Template object

        Raises:
            TimeoutError: Timeout error
            ClientError: Client error
        """
        import asyncio

        start_time = time.time()
        while True:
            template = await self.get_template_async(
                template_name, config=config
            )

            # Check if ready
            if template.status == "READY":
                return template

            # Check if failed
            if (
                template.status == "CREATE_FAILED"
                or template.status == "UPDATE_FAILED"
            ):
                raise ClientError(
                    f"Template {template_name} creation failed, status:"
                    f" {template.status}"
                )

            # Check timeout
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(
                    f"Timeout waiting for Template {template_name} to be ready,"
                    f" current status: {template.status}"
                )

            await asyncio.sleep(interval_seconds)

    async def create_template_async(
        self, input: TemplateInput, config: Optional[Config] = None
    ) -> "Template":
        """创建 Template（异步）

        Args:
            input: Template 配置
            config: 配置对象

        Returns:
            Template: 创建的 Template 对象

        Raises:
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        from agentrun.sandbox.template import Template

        # 转换为 SDK 需要的格式
        sdk_input = CreateTemplateInput().from_map(
            input.model_dump(by_alias=True)
        )
        result = await self.__template_control_api.create_async(
            sdk_input, config=config
        )
        template = Template.from_inner_object(result)

        # Poll and wait for Template to be ready
        template = await self._wait_template_ready_async(
            template.template_name, config=config
        )

        return template

    def create_template(
        self, input: TemplateInput, config: Optional[Config] = None
    ) -> "Template":
        """创建 Template（同步）

        Args:
            input: Template 配置
            config: 配置对象

        Returns:
            Template: 创建的 Template 对象

        Raises:
            ClientError: 客户端错误
            ServerError: 服务器错误
            TimeoutError: Timeout waiting for Template to be ready
        """
        from agentrun.sandbox.template import Template

        # 转换为 SDK 需要的格式
        sdk_input = CreateTemplateInput().from_map(
            input.model_dump(by_alias=True)
        )
        result = self.__template_control_api.create(sdk_input, config=config)
        template = Template.from_inner_object(result)

        # Poll and wait for Template to be ready
        template = self._wait_template_ready(
            template.template_name, config=config
        )

        return template

    async def delete_template_async(
        self, template_name: str, config: Optional[Config] = None
    ) -> "Template":
        """删除 Template（异步）

        Args:
            template_name: Template 名称
            config: 配置对象

        Returns:
            Template: 删除的 Template 对象

        Raises:
            ResourceNotExistError: Template 不存在
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        from agentrun.sandbox.template import Template

        try:
            result = await self.__template_control_api.delete_async(
                template_name, config=config
            )
            return Template.from_inner_object(result)
        except ClientError as e:
            if e.status_code == 404:
                raise ResourceNotExistError("Template", template_name) from e
            raise e

    def delete_template(
        self, template_name: str, config: Optional[Config] = None
    ) -> "Template":
        """删除 Template（同步）

        Args:
            template_name: Template 名称
            config: 配置对象

        Returns:
            Template: 删除的 Template 对象

        Raises:
            ResourceNotExistError: Template 不存在
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        from agentrun.sandbox.template import Template

        try:
            result = self.__template_control_api.delete(
                template_name, config=config
            )
            return Template.from_inner_object(result)
        except ClientError as e:
            if e.status_code == 404:
                raise ResourceNotExistError("Template", template_name) from e
            raise e

    async def update_template_async(
        self,
        template_name: str,
        input: TemplateInput,
        config: Optional[Config] = None,
    ) -> "Template":
        """更新 Template（异步）

        Args:
            template_name: Template 名称
            input: Template 更新配置
            config: 配置对象

        Returns:
            Template: 更新后的 Template 对象

        Raises:
            ResourceNotExistError: Template 不存在
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        from agentrun.sandbox.template import Template

        try:
            # 转换为 SDK 需要的格式
            sdk_input = UpdateTemplateInput().from_map(
                input.model_dump(by_alias=True, exclude_none=True)
            )
            result = await self.__template_control_api.update_async(
                template_name, sdk_input, config=config
            )
            return Template.from_inner_object(result)
        except ClientError as e:
            if e.status_code == 404:
                raise ResourceNotExistError("Template", template_name) from e
            raise e

    def update_template(
        self,
        template_name: str,
        input: TemplateInput,
        config: Optional[Config] = None,
    ) -> "Template":
        """更新 Template（同步）

        Args:
            template_name: Template 名称
            input: Template 更新配置
            config: 配置对象

        Returns:
            Template: 更新后的 Template 对象

        Raises:
            ResourceNotExistError: Template 不存在
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        from agentrun.sandbox.template import Template

        try:
            # 转换为 SDK 需要的格式
            sdk_input = UpdateTemplateInput().from_map(
                input.model_dump(by_alias=True, exclude_none=True)
            )
            result = self.__template_control_api.update(
                template_name, sdk_input, config=config
            )
            return Template.from_inner_object(result)
        except ClientError as e:
            if e.status_code == 404:
                raise ResourceNotExistError("Template", template_name) from e
            raise e

    async def get_template_async(
        self, template_name: str, config: Optional[Config] = None
    ) -> "Template":
        """获取 Template（异步）

        Args:
            template_name: Template 名称
            config: 配置对象

        Returns:
            Template: Template 对象

        Raises:
            ResourceNotExistError: Template 不存在
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        from agentrun.sandbox.template import Template

        try:
            result = await self.__template_control_api.get_async(
                template_name, config=config
            )
            return Template.from_inner_object(result)
        except ClientError as e:
            if e.status_code == 404:
                raise ResourceNotExistError("Template", template_name) from e
            raise e

    def get_template(
        self, template_name: str, config: Optional[Config] = None
    ) -> "Template":
        """获取 Template（同步）

        Args:
            template_name: Template 名称
            config: 配置对象

        Returns:
            Template: Template 对象

        Raises:
            ResourceNotExistError: Template 不存在
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        from agentrun.sandbox.template import Template

        try:
            result = self.__template_control_api.get(
                template_name, config=config
            )
            return Template.from_inner_object(result)
        except ClientError as e:
            if e.status_code == 404:
                raise ResourceNotExistError("Template", template_name) from e
            raise e

    async def list_templates_async(
        self,
        input: Optional[PageableInput] = None,
        config: Optional[Config] = None,
    ) -> List["Template"]:
        """枚举 Templates（异步）

        Args:
            input: 分页配置
            config: 配置对象

        Returns:
            List[Template]: Template 列表

        Raises:
            ClientError: 客户端错误
            ServerError: 服务器错误
            TimeoutError: Timeout waiting for Template to be ready
        """
        from agentrun.sandbox.template import Template

        if input is None:
            input = PageableInput()

        # 转换为 SDK 需要的格式
        sdk_input = ListTemplatesRequest().from_map(
            input.model_dump(by_alias=True)
        )
        results = await self.__template_control_api.list_async(
            sdk_input, config=config
        )
        return (
            [Template.from_inner_object(item) for item in results.items]
            if results.items
            else []
        )

    def list_templates(
        self,
        input: Optional[PageableInput] = None,
        config: Optional[Config] = None,
    ) -> List["Template"]:
        """枚举 Templates（同步）

        Args:
            input: 分页配置
            config: 配置对象

        Returns:
            List[Template]: Template 列表

        Raises:
            ClientError: 客户端错误
            ServerError: 服务器错误
        """
        from agentrun.sandbox.template import Template

        if input is None:
            input = PageableInput()

        # 转换为 SDK 需要的格式
        sdk_input = ListTemplatesRequest().from_map(
            input.model_dump(by_alias=True)
        )
        results = self.__template_control_api.list(sdk_input, config=config)
        return (
            [Template.from_inner_object(item) for item in results.items]
            if results.items
            else []
        )
