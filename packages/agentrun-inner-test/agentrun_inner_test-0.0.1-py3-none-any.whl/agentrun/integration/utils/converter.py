"""框架转换器

提供统一的框架转换入口，使用适配器模式实现跨框架转换。
"""

from typing import Any, Dict, Optional

from agentrun.integration.utils.adapter import (
    MessageAdapter,
    ModelAdapter,
    ToolAdapter,
)
from agentrun.integration.utils.canonical import CanonicalMessage, CanonicalTool


class FrameworkConverter:
    """框架转换器（注册中心）

    管理所有框架适配器，提供统一的转换接口。
    使用中间格式作为桥梁，最大化代码复用。
    """

    def __init__(self):
        self._message_adapters: Dict[str, MessageAdapter] = {}
        self._tool_adapters: Dict[str, ToolAdapter] = {}
        self._model_adapters: Dict[str, ModelAdapter] = {}

    def register_message_adapter(
        self, framework: str, adapter: MessageAdapter
    ) -> None:
        """注册消息适配器"""
        self._message_adapters[framework] = adapter

    def register_tool_adapter(
        self, framework: str, adapter: ToolAdapter
    ) -> None:
        """注册工具适配器"""
        self._tool_adapters[framework] = adapter

    def register_model_adapter(
        self, framework: str, adapter: ModelAdapter
    ) -> None:
        """注册模型适配器"""
        self._model_adapters[framework] = adapter

    def convert_messages(
        self,
        messages: Any,
        from_framework: str,
        to_framework: str,
    ) -> Any:
        """跨框架消息转换

        转换流程：
        1. 框架A消息 → 中间格式（CanonicalMessage）
        2. 中间格式 → 框架B消息

        Args:
            messages: 源框架的消息格式
            from_framework: 源框架名称
            to_framework: 目标框架名称

        Returns:
            目标框架的消息格式

        Raises:
            ValueError: 如果适配器未注册
        """
        # 转换为中间格式
        from_adapter = self._message_adapters.get(from_framework)
        if not from_adapter:
            raise ValueError(
                f"No message adapter registered for framework: {from_framework}"
            )

        canonical_messages = from_adapter.to_canonical(messages)

        # 从中间格式转换
        to_adapter = self._message_adapters.get(to_framework)
        if not to_adapter:
            raise ValueError(
                f"No message adapter registered for framework: {to_framework}"
            )

        return to_adapter.from_canonical(canonical_messages)

    def convert_tools(
        self,
        tools: Any,
        from_framework: str,
        to_framework: str,
    ) -> Any:
        """跨框架工具转换

        Args:
            tools: 源框架的工具格式
            from_framework: 源框架名称
            to_framework: 目标框架名称

        Returns:
            目标框架的工具格式
        """
        from_adapter = self._tool_adapters.get(from_framework)
        if not from_adapter:
            raise ValueError(
                f"No tool adapter registered for framework: {from_framework}"
            )

        canonical_tools = from_adapter.to_canonical(tools)

        to_adapter = self._tool_adapters.get(to_framework)
        if not to_adapter:
            raise ValueError(
                f"No tool adapter registered for framework: {to_framework}"
            )

        return to_adapter.from_canonical(canonical_tools)

    def get_model_adapter(self, framework: str) -> Optional[ModelAdapter]:
        """获取模型适配器"""
        return self._model_adapters.get(framework)


# 全局转换器实例
_converter = FrameworkConverter()


def get_converter() -> FrameworkConverter:
    """获取全局转换器实例"""
    return _converter


def _auto_register_adapters() -> None:
    """自动注册所有可用的适配器

    延迟导入，避免循环依赖。
    """
    # LangChain 适配器
    try:
        from agentrun.integration.langchain.adapter import (
            LangChainMessageAdapter,
            LangChainModelAdapter,
            LangChainToolAdapter,
        )

        _converter.register_message_adapter(
            "langchain", LangChainMessageAdapter()
        )
        _converter.register_tool_adapter("langchain", LangChainToolAdapter())
        _converter.register_model_adapter("langchain", LangChainModelAdapter())
    except (ImportError, AttributeError):
        pass

    # Google ADK 适配器
    try:
        from agentrun.integration.google_adk.adapter import (
            GoogleADKMessageAdapter,
            GoogleADKModelAdapter,
            GoogleADKToolAdapter,
        )

        _converter.register_message_adapter(
            "google_adk", GoogleADKMessageAdapter()
        )
        _converter.register_tool_adapter("google_adk", GoogleADKToolAdapter())
        _converter.register_model_adapter("google_adk", GoogleADKModelAdapter())
    except (ImportError, AttributeError):
        pass

    # AgentScope 适配器（待实现）
    # try:
    #     from agentrun.integration.agentscope.adapter import (
    #         AgentScopeMessageAdapter,
    #         AgentScopeToolAdapter,
    #         AgentScopeModelAdapter,
    #     )
    #     _converter.register_message_adapter(
    #         "agentscope", AgentScopeMessageAdapter()
    #     )
    #     _converter.register_tool_adapter(
    #         "agentscope", AgentScopeToolAdapter()
    #     )
    #     _converter.register_model_adapter(
    #         "agentscope", AgentScopeModelAdapter()
    #     )
    # except (ImportError, AttributeError):
    #     pass


# 初始化时自动注册
_auto_register_adapters()
