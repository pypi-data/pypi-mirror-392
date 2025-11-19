"""Sandbox 高层 API"""

from typing import List, Literal, Optional, overload, TYPE_CHECKING, Union

from alibabacloud_agentrun20250910.models import Sandbox as SandboxModel

from agentrun.sandbox.api.code_interpreter_data import CodeInterpreterDataAPI
from agentrun.sandbox.model import SandboxInput, TemplateType
from agentrun.utils.config import Config, get_env_with_default
from agentrun.utils.model import BaseModel

if TYPE_CHECKING:
    from agentrun.sandbox.browser_sandbox import BrowserSandbox
    from agentrun.sandbox.code_interpreter_sandbox import CodeInterpreterSandbox
    from agentrun.sandbox.model import PageableInput, TemplateInput
    from agentrun.sandbox.template import Template


class Sandbox(BaseModel):
    """Sandbox 实例

    封装了 Sandbox 的基本信息和操作方法
    """

    created_at: Optional[str] = None
    """沙箱创建时间"""
    last_updated_at: Optional[str] = None
    """最后更新时间"""
    sandbox_arn: Optional[str] = None
    """沙箱全局唯一资源名称"""
    sandbox_id: Optional[str] = None
    """沙箱 ID"""
    sandbox_idle_timeout_seconds: Optional[int] = None
    """沙箱空闲超时时间（秒）"""
    status: Optional[str] = None
    """沙箱状态"""
    template_id: Optional[str] = None
    """模板 ID"""
    template_name: Optional[str] = None
    """模板名称"""
    account_id: Optional[str] = None
    """账号 ID"""
    _config: Optional[Config] = None
    """配置对象，用于子类的 data_api 初始化"""

    @classmethod
    def __get_client(cls):
        """获取 Sandbox 客户端"""
        from .client import SandboxClient

        return SandboxClient()

    @classmethod
    def __get_account_id(cls, config: Optional[Config] = None) -> str:
        """获取 account_id，复用 Config 的逻辑

        Args:
            config: 配置对象

        Returns:
            str: account_id
        """
        # 如果 config 提供了 account_id，优先使用
        if config is not None:
            account_id = config.get_account_id()
            if account_id:
                return account_id

        # 否则从环境变量读取
        return get_env_with_default("", "AGENTRUN_ACCOUNT_ID", "FC_ACCOUNT_ID")

    @classmethod
    @overload
    async def create_async(
        cls,
        template_type: Literal[TemplateType.CODE_INTERPRETER],
        template_name: Optional[str] = None,
        sandbox_idle_timeout_seconds: Optional[int] = 600,
        config: Optional[Config] = None,
    ) -> "CodeInterpreterSandbox":
        ...

    @classmethod
    @overload
    async def create_async(
        cls,
        template_type: Literal[TemplateType.BROWSER],
        template_name: Optional[str] = None,
        sandbox_idle_timeout_seconds: Optional[int] = 600,
        config: Optional[Config] = None,
    ) -> "BrowserSandbox":
        ...

    @classmethod
    async def create_async(
        cls,
        template_type: TemplateType,
        template_name: Optional[str] = None,
        sandbox_idle_timeout_seconds: Optional[int] = 600,
        config: Optional[Config] = None,
    ) -> Union["CodeInterpreterSandbox", "BrowserSandbox"]:

        if template_name is None:
            # todo 可以考虑为用户创建一个模板？
            raise ValueError("template_name is required")

        # 先根据传入的template_name，获取template的类型
        template = await cls.get_template_async(template_name, config=config)

        # 根据 template 类型创建相应的 Sandbox 子类
        from agentrun.sandbox.browser_sandbox import BrowserSandbox
        from agentrun.sandbox.code_interpreter_sandbox import (
            CodeInterpreterSandbox,
        )

        if template_type != template.template_type:
            raise ValueError(
                f"template_type of {template_name} is {template.template_type},"
                f" not {template_type}"
            )

        # 创建 Sandbox（返回基类实例）
        base_sandbox = await cls.__get_client().create_sandbox_async(
            SandboxInput(
                template_name=template_name,
                sandbox_idle_timeout_seconds=sandbox_idle_timeout_seconds,
            ),
            config=config,
        )

        # 根据 template 类型转换为对应的子类实例
        sandbox = None
        if template.template_type == TemplateType.CODE_INTERPRETER:
            sandbox = CodeInterpreterSandbox.model_validate(
                base_sandbox.model_dump(by_alias=False)
            )
        elif template.template_type == TemplateType.BROWSER:
            sandbox = BrowserSandbox.model_validate(
                base_sandbox.model_dump(by_alias=False)
            )
        else:
            raise ValueError(
                f"template_type {template.template_type} is not supported"
            )

        # 设置 account_id 和 config
        sandbox.account_id = cls.__get_account_id(config)
        sandbox._config = config
        return sandbox

    @classmethod
    @overload
    def create(
        cls,
        template_type: Literal[TemplateType.CODE_INTERPRETER],
        template_name: Optional[str] = None,
        sandbox_idle_timeout_seconds: Optional[int] = 600,
        config: Optional[Config] = None,
    ) -> "CodeInterpreterSandbox":
        ...

    @classmethod
    @overload
    def create(
        cls,
        template_type: Literal[TemplateType.BROWSER],
        template_name: Optional[str] = None,
        sandbox_idle_timeout_seconds: Optional[int] = 600,
        config: Optional[Config] = None,
    ) -> "BrowserSandbox":
        ...

    @classmethod
    def create(
        cls,
        template_type: TemplateType,
        template_name: Optional[str] = None,
        sandbox_idle_timeout_seconds: Optional[int] = 600,
        config: Optional[Config] = None,
    ) -> Union["CodeInterpreterSandbox", "BrowserSandbox"]:

        if template_name is None:
            # todo 可以考虑为用户创建一个模板？
            raise ValueError("template_name is required")

        # 先根据传入的template_name，获取template的类型
        template = cls.get_template(template_name, config=config)

        # 根据 template 类型创建相应的 Sandbox 子类
        from agentrun.sandbox.browser_sandbox import BrowserSandbox
        from agentrun.sandbox.code_interpreter_sandbox import (
            CodeInterpreterSandbox,
        )

        if template_type != template.template_type:
            raise ValueError(
                f"template_type of {template_name} is {template.template_type},"
                f" not {template_type}"
            )

        # 创建 Sandbox（返回基类实例）
        base_sandbox = cls.__get_client().create_sandbox(
            SandboxInput(
                template_name=template_name,
                sandbox_idle_timeout_seconds=sandbox_idle_timeout_seconds,
            ),
            config=config,
        )

        # 根据 template 类型转换为对应的子类实例
        sandbox = None
        if template.template_type == TemplateType.CODE_INTERPRETER:
            sandbox = CodeInterpreterSandbox.model_validate(
                base_sandbox.model_dump(by_alias=False)
            )
        elif template.template_type == TemplateType.BROWSER:
            sandbox = BrowserSandbox.model_validate(
                base_sandbox.model_dump(by_alias=False)
            )
        else:
            raise ValueError(
                f"template_type {template.template_type} is not supported"
            )

        # 设置 account_id 和 config
        sandbox.account_id = cls.__get_account_id(config)
        sandbox._config = config
        return sandbox

    @classmethod
    async def get_async(
        cls, sandbox_id: str, config: Optional[Config] = None
    ) -> "Sandbox":
        """通过 ID 获取 Sandbox（异步）

        Args:
            sandbox_id: Sandbox ID
            config: 配置对象

        Returns:
            Sandbox: Sandbox 对象
        """
        if sandbox_id is None:
            raise ValueError("sandbox_id is required")
        return await cls.__get_client().get_sandbox_async(
            sandbox_id, config=config
        )

    @classmethod
    def get(cls, sandbox_id: str, config: Optional[Config] = None) -> "Sandbox":
        """通过 ID 获取 Sandbox（同步）

        Args:
            sandbox_id: Sandbox ID
            config: 配置对象

        Returns:
            Sandbox: Sandbox 对象
        """
        if sandbox_id is None:
            raise ValueError("sandbox_id is required")
        return cls.__get_client().get_sandbox(sandbox_id, config=config)

    @classmethod
    def stop(
        cls, sandbox_id: str, config: Optional[Config] = None
    ) -> "Sandbox":
        """通过 ID 删除 Sandbox（同步）

        Args:
            sandbox_id: Sandbox ID
            config: 配置对象

        Returns:
            Sandbox: Sandbox 对象
        """
        if sandbox_id is None:
            raise ValueError("sandbox_id is required")
        return cls.__get_client().stop_sandbox(sandbox_id, config=config)

    @classmethod
    async def stop_async(
        cls, sandbox_id: str, config: Optional[Config] = None
    ) -> "Sandbox":
        """通过 ID 删除 Sandbox（异步）

        Args:
            sandbox_id: Sandbox ID
            config: 配置对象

        Returns:
            Sandbox: Sandbox 对象
        """
        if sandbox_id is None:
            raise ValueError("sandbox_id is required")
        return await cls.__get_client().stop_sandbox_async(
            sandbox_id, config=config
        )

    @classmethod
    @overload
    def connect(
        cls,
        sandbox_id: str,
        template_type: Literal[TemplateType.CODE_INTERPRETER],
        config: Optional[Config] = None,
    ) -> "CodeInterpreterSandbox":
        ...

    @classmethod
    @overload
    def connect(
        cls,
        sandbox_id: str,
        template_type: Literal[TemplateType.BROWSER],
        config: Optional[Config] = None,
    ) -> "BrowserSandbox":
        ...

    @classmethod
    @overload
    def connect(
        cls,
        sandbox_id: str,
        template_type: None = None,
        config: Optional[Config] = None,
    ) -> Union["CodeInterpreterSandbox", "BrowserSandbox"]:
        ...

    @classmethod
    def connect(
        cls,
        sandbox_id: str,
        template_type: Optional[TemplateType] = None,
        config: Optional[Config] = None,
    ) -> Union["CodeInterpreterSandbox", "BrowserSandbox"]:
        """连接一个SandBox（同步）

        Args:
            sandbox_id: Sandbox ID
            type: 可选的类型参数，用于类型提示和运行时验证
            config: 配置对象

        Returns:
            Sandbox: 根据模板类型返回对应的 Sandbox 子类对象

        Raises:
            ValueError: 如果模板类型不支持或与预期类型不匹配
        """
        if sandbox_id is None:
            raise ValueError("sandbox_id is required")

        # 先获取 sandbox 信息
        sandbox = cls.__get_client().get_sandbox(sandbox_id, config=config)

        # 根据 template_name 获取 template 类型
        if sandbox.template_name is None:
            raise ValueError(f"Sandbox {sandbox_id} has no template_name")

        template = cls.get_template(sandbox.template_name, config=config)

        # 如果提供了 type 参数，验证类型是否匹配
        if (
            template_type is not None
            and template.template_type != template_type
        ):
            raise ValueError(
                f"Sandbox {sandbox_id} has template type"
                f" {template.template_type}, but expected {template_type}"
            )

        # 根据 template 类型创建相应的 Sandbox 子类
        from agentrun.sandbox.browser_sandbox import BrowserSandbox
        from agentrun.sandbox.code_interpreter_sandbox import (
            CodeInterpreterSandbox,
        )

        result = None
        if template.template_type == TemplateType.CODE_INTERPRETER:
            result = CodeInterpreterSandbox.model_validate(
                sandbox.model_dump(by_alias=False)
            )
        elif template.template_type == TemplateType.BROWSER:
            result = BrowserSandbox.model_validate(
                sandbox.model_dump(by_alias=False)
            )
        else:
            raise ValueError(
                f"Unsupported template type: {template.template_type}. "
                "Expected 'code-interpreter' or 'browser'"
            )

        # 设置 account_id 和 config
        result.account_id = cls.__get_account_id(config)
        result._config = config
        return result

    @classmethod
    @overload
    async def connect_async(
        cls,
        sandbox_id: str,
        template_type: Literal[TemplateType.CODE_INTERPRETER],
        config: Optional[Config] = None,
    ) -> "CodeInterpreterSandbox":
        ...

    @classmethod
    @overload
    async def connect_async(
        cls,
        sandbox_id: str,
        template_type: Literal[TemplateType.BROWSER],
        config: Optional[Config] = None,
    ) -> "BrowserSandbox":
        ...

    @classmethod
    @overload
    async def connect_async(
        cls,
        sandbox_id: str,
        template_type: None = None,
        config: Optional[Config] = None,
    ) -> Union["CodeInterpreterSandbox", "BrowserSandbox"]:
        ...

    @classmethod
    async def connect_async(
        cls,
        sandbox_id: str,
        template_type: Optional[TemplateType] = None,
        config: Optional[Config] = None,
    ) -> Union["CodeInterpreterSandbox", "BrowserSandbox"]:
        """连接一个SandBox（异步）

        Args:
            sandbox_id: Sandbox ID
            type: 可选的类型参数，用于类型提示和运行时验证
            config: 配置对象

        Returns:
            Sandbox: 根据模板类型返回对应的 Sandbox 子类对象

        Raises:
            ValueError: 如果模板类型不支持或与预期类型不匹配
        """
        if sandbox_id is None:
            raise ValueError("sandbox_id is required")

        # 先获取 sandbox 信息
        sandbox = await cls.__get_client().get_sandbox_async(
            sandbox_id, config=config
        )

        # 根据 template_name 获取 template 类型
        if sandbox.template_name is None:
            raise ValueError(f"Sandbox {sandbox_id} has no template_name")

        template = await cls.get_template_async(
            sandbox.template_name, config=config
        )

        # 如果提供了 type 参数，验证类型是否匹配
        if (
            template_type is not None
            and template.template_type != template_type
        ):
            raise ValueError(
                f"Sandbox {sandbox_id} has template type"
                f" {template.template_type}, but expected {template_type}"
            )

        # 根据 template 类型创建相应的 Sandbox 子类
        from agentrun.sandbox.browser_sandbox import BrowserSandbox
        from agentrun.sandbox.code_interpreter_sandbox import (
            CodeInterpreterSandbox,
        )

        result = None
        if template.template_type == TemplateType.CODE_INTERPRETER:
            result = CodeInterpreterSandbox.model_validate(
                sandbox.model_dump(by_alias=False)
            )
        elif template.template_type == TemplateType.BROWSER:
            result = BrowserSandbox.model_validate(
                sandbox.model_dump(by_alias=False)
            )
        else:
            raise ValueError(
                f"Unsupported template type: {template.template_type}. "
                "Expected 'code-interpreter' or 'browser'"
            )

        # 设置 account_id 和 config
        result.account_id = cls.__get_account_id(config)
        result._config = config
        return result

    # ==================== Template 相关类方法 ====================

    @classmethod
    async def create_template_async(
        cls, input: "TemplateInput", config: Optional[Config] = None
    ) -> "Template":
        """创建 Template（异步）

        Args:
            input: Template 配置
            config: 配置对象

        Returns:
            Template: 创建的 Template 对象
        """
        if input.template_type is None:
            raise ValueError("template_type is required")
        return await cls.__get_client().create_template_async(
            input, config=config
        )

    @classmethod
    def create_template(
        cls, input: "TemplateInput", config: Optional[Config] = None
    ) -> "Template":
        """创建 Template（同步）

        Args:
            input: Template 配置
            config: 配置对象

        Returns:
            Template: 创建的 Template 对象
        """
        if input.template_type is None:
            raise ValueError("template_type is required")
        return cls.__get_client().create_template(input, config=config)

    @classmethod
    async def get_template_async(
        cls, template_name: str, config: Optional[Config] = None
    ) -> "Template":
        """获取 Template（异步）

        Args:
            template_name: Template 名称
            config: 配置对象

        Returns:
            Template: Template 对象
        """
        if template_name is None:
            raise ValueError("template_name is required")
        return await cls.__get_client().get_template_async(
            template_name, config=config
        )

    @classmethod
    def get_template(
        cls, template_name: str, config: Optional[Config] = None
    ) -> "Template":
        """获取 Template（同步）

        Args:
            template_name: Template 名称
            config: 配置对象

        Returns:
            Template: Template 对象
        """
        if template_name is None:
            raise ValueError("template_name is required")
        return cls.__get_client().get_template(template_name, config=config)

    @classmethod
    async def update_template_async(
        cls,
        template_name: str,
        input: "TemplateInput",
        config: Optional[Config] = None,
    ) -> "Template":
        """更新 Template（异步）

        Args:
            template_name: Template 名称
            input: Template 更新配置
            config: 配置对象

        Returns:
            Template: 更新后的 Template 对象
        """
        if template_name is None:
            raise ValueError("template_name is required")
        return await cls.__get_client().update_template_async(
            template_name, input, config=config
        )

    @classmethod
    def update_template(
        cls,
        template_name: str,
        input: "TemplateInput",
        config: Optional[Config] = None,
    ) -> "Template":
        """更新 Template（同步）

        Args:
            template_name: Template 名称
            input: Template 更新配置
            config: 配置对象

        Returns:
            Template: 更新后的 Template 对象
        """
        if template_name is None:
            raise ValueError("template_name is required")
        return cls.__get_client().update_template(
            template_name, input, config=config
        )

    @classmethod
    async def delete_template_async(
        cls, template_name: str, config: Optional[Config] = None
    ) -> "Template":
        """删除 Template（异步）

        Args:
            template_name: Template 名称
            config: 配置对象

        Returns:
            Template: 删除的 Template 对象
        """
        if template_name is None:
            raise ValueError("template_name is required")
        return await cls.__get_client().delete_template_async(
            template_name, config=config
        )

    @classmethod
    def delete_template(
        cls, template_name: str, config: Optional[Config] = None
    ) -> "Template":
        """删除 Template（同步）

        Args:
            template_name: Template 名称
            config: 配置对象

        Returns:
            Template: 删除的 Template 对象
        """
        if template_name is None:
            raise ValueError("template_name is required")
        return cls.__get_client().delete_template(template_name, config=config)

    @classmethod
    async def list_templates_async(
        cls,
        input: Optional["PageableInput"] = None,
        config: Optional[Config] = None,
    ) -> List["Template"]:
        """列出 Templates（异步）

        Args:
            input: 分页配置
            config: 配置对象

        Returns:
            List[Template]: Template 列表
        """
        return await cls.__get_client().list_templates_async(
            input, config=config
        )

    @classmethod
    def list_templates(
        cls,
        input: Optional["PageableInput"] = None,
        config: Optional[Config] = None,
    ) -> List["Template"]:
        """列出 Templates（同步）

        Args:
            input: 分页配置
            config: 配置对象

        Returns:
            List[Template]: Template 列表
        """
        return cls.__get_client().list_templates(input, config=config)
