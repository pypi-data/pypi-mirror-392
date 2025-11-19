"""LangChain 集成模块,提供 AgentRun 模型与沙箱的 LangChain 适配。"""

from __future__ import annotations

from typing import Any, List, Optional

from agentrun.integration.builtin.sandbox import (
    sandbox_toolset as _sandbox_toolset,
)
from agentrun.integration.utils.model import model as _common_model
from agentrun.sandbox import TemplateType
from agentrun.utils.config import Config

__all__ = [
    "model",
    "sandbox_toolset",
]


def model(
    name: str,
    backend_type: Optional[str] = None,
    config: Optional[Config] = None,
):
    """获取 AgentRun 模型并转换为 LangChain ``BaseChatModel``。"""

    common_model = _common_model(
        name=name,
        backend_type=backend_type,
        config=config,
    )
    return common_model.to_langchain()


def sandbox_toolset(
    template_name: str,
    *,
    template_type: TemplateType = TemplateType.CODE_INTERPRETER,
    config: Optional[Config] = None,
    sandbox_idle_timeout_seconds: int = 600,
    prefix: Optional[str] = None,
) -> List[Any]:
    """将沙箱模板封装为 LangChain ``StructuredTool`` 列表。"""

    return _sandbox_toolset(
        template_name=template_name,
        template_type=template_type,
        config=config,
        sandbox_idle_timeout_seconds=sandbox_idle_timeout_seconds,
        prefix=prefix,
    ).to_langchain(prefix=prefix)
