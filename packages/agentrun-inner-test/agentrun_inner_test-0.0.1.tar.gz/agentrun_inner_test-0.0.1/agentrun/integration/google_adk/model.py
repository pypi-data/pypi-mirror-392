"""Google ADK Model 集成"""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from agentrun.config import Config
    from agentrun.model import Model


def model(model_name: str, config: Optional["Config"] = None) -> Any:
    """获取 AgentRun 模型并转换为 Google ADK 兼容格式

    动态导入依赖,不需要预先安装 Google ADK

    Args:
        model_name: 模型名称或 ID
        config: 全局配置,未提供时从环境变量读取

    Returns:
        适配 Google ADK 的模型对象

    Raises:
        ModelError: 模型不存在或不支持时抛出
        ImportError: Google ADK 未安装时抛出

    Examples:
        >>> # 需要先安装: pip install google-generativeai
        >>> from google.adk.agents.llm_agent import Agent
        >>> from agentrun.integration.google_adk import model
        >>>
        >>> agent = Agent(
        ...     model=model('my-model'),
        ...     name='assistant',
        ...     instruction='You are a helpful assistant.'
        ... )
    """
    # 动态导入,避免强制依赖
    try:
        import google.genai  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "Google ADK not installed. Please install it first:\n  pip install"
            " google-generativeai\n\nOr install agentrun with google_adk"
            " support:\n  pip install agentrun[google_adk]"
        ) from e

    # 延迟导入 agentrun 模块
    from agentrun.config import Config
    from agentrun.model import Model
    from agentrun.utils.exception import ModelError

    if config is None:
        config = Config()

    # 获取 AgentRun 模型
    agentrun_model = Model.get(config, model_name)

    if not agentrun_model.is_proxy:
        raise ModelError("Only proxy models support Google ADK integration")

    if not agentrun_model.endpoint:
        raise ModelError("Model endpoint not available")

    # 创建 Google ADK 兼容的模型配置
    # 注意: 这里需要根据实际 Google ADK API 进行适配
    class AgentRunModelAdapter:
        """AgentRun 模型适配器

        适配 AgentRun 模型到 Google ADK 接口
        """

        def __init__(self, model_obj: "Model") -> None:
            self.model = model_obj
            self.client = model_obj.chat

        def generate_content(self, prompt: str, **kwargs: Any) -> Any:
            """生成内容"""
            messages = [{"role": "user", "content": prompt}]
            response = self.client.completions.create(
                messages=messages, **kwargs
            )
            return response

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            """调用模型"""
            if args:
                return self.generate_content(args[0], **kwargs)
            return self.generate_content(**kwargs)

    return AgentRunModelAdapter(agentrun_model)
