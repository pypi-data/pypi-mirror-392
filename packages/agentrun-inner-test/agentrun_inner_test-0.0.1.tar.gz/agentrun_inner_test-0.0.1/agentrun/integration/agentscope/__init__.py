"""AgentScope 集成模块

提供与 AgentScope 的快速集成

此模块使用动态导入,不需要预先安装 AgentScope。
只有在实际使用时才会尝试导入 AgentScope,版本跟随用户本地安装的版本。

安装方式:
    pip install agentscope

或者:
    pip install agentrun[agentscope]

示例:
    >>> # 需要先安装 AgentScope
    >>> from agentrun.integration.agentscope import AgentRunModelWrapper
    >>>
    >>> model = AgentRunModelWrapper(model_name="my-model")
    >>> agent = DialogAgent(model=model)
"""

# TODO: 实现 AgentScope 集成
# 计划实现:
# - AgentRunModelWrapper: AgentScope 模型适配器
# - AgentRunSandboxService: 沙箱服务集成

__all__ = []  # 待实现后添加
