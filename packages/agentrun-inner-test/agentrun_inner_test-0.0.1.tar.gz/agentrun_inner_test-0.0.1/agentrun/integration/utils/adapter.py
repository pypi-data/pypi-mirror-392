"""适配器接口定义

定义统一的适配器接口，所有框架适配器都实现这些接口。
这样可以确保一致的转换行为，并最大化代码复用。
"""

from abc import ABC, abstractmethod
from typing import Any, List

from agentrun.integration.utils.canonical import CanonicalMessage, CanonicalTool


class MessageAdapter(ABC):
    """消息格式适配器接口

    所有框架的消息适配器都实现这个接口。
    只需要实现框架格式 ↔ 中间格式的转换，不需要实现框架A ↔ 框架B。

    转换流程：
    - 框架A消息 → to_canonical() → CanonicalMessage
    - CanonicalMessage → from_canonical() → 框架B消息
    """

    @abstractmethod
    def to_canonical(self, messages: Any) -> List[CanonicalMessage]:
        """将框架消息转换为中间格式

        Args:
            messages: 框架特定的消息格式

        Returns:
            中间格式消息列表
        """
        pass

    @abstractmethod
    def from_canonical(self, messages: List[CanonicalMessage]) -> Any:
        """将中间格式转换为框架消息

        Args:
            messages: 中间格式消息列表

        Returns:
            框架特定的消息格式
        """
        pass


class ToolAdapter(ABC):
    """工具格式适配器接口

    所有框架的工具适配器都实现这个接口。
    """

    @abstractmethod
    def to_canonical(self, tools: Any) -> List[CanonicalTool]:
        """将框架工具转换为中间格式

        Args:
            tools: 框架特定的工具格式

        Returns:
            中间格式工具列表
        """
        pass

    @abstractmethod
    def from_canonical(self, tools: List[CanonicalTool]) -> Any:
        """将中间格式转换为框架工具

        Args:
            tools: 中间格式工具列表

        Returns:
            框架特定的工具格式
        """
        pass


class ModelAdapter(ABC):
    """模型适配器接口

    用于包装框架模型，使其能够与 CommonModel 协同工作。
    """

    @abstractmethod
    def wrap_model(self, common_model: Any) -> Any:
        """包装 CommonModel 为框架特定的模型格式

        Args:
            common_model: CommonModel 实例

        Returns:
            框架特定的模型对象
        """
        pass
