"""LangChain 适配器实现

提供 LangChain 框架的消息、工具和模型适配器。
"""

import json
from typing import Any, List, Optional

from agentrun.integration.utils.adapter import (
    MessageAdapter,
    ModelAdapter,
    ToolAdapter,
)
from agentrun.integration.utils.canonical import (
    CanonicalMessage,
    CanonicalTool,
    CanonicalToolCall,
    MessageRole,
)


class LangChainMessageAdapter(MessageAdapter):
    """LangChain 消息适配器

    实现 LangChain BaseMessage ↔ CanonicalMessage 的转换。
    """

    def to_canonical(self, messages: Any) -> List[CanonicalMessage]:
        """将 LangChain BaseMessage 转换为中间格式"""
        try:
            from langchain_core.messages import (
                AIMessage,
                BaseMessage,
                HumanMessage,
                SystemMessage,
                ToolMessage,
            )
        except ImportError as e:
            raise ImportError(
                "LangChain is not installed. "
                "Install it with: pip install langchain-core"
            ) from e

        canonical = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                canonical.append(
                    CanonicalMessage(
                        role=MessageRole.SYSTEM,
                        content=msg.content
                        if hasattr(msg, "content")
                        else None,
                    )
                )
            elif isinstance(msg, HumanMessage):
                canonical.append(
                    CanonicalMessage(
                        role=MessageRole.USER,
                        content=msg.content
                        if hasattr(msg, "content")
                        else None,
                    )
                )
            elif isinstance(msg, AIMessage):
                tool_calls = None
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    tool_calls = []
                    for call in msg.tool_calls:
                        # LangChain tool_calls 格式: {"id": ..., "name": ..., "args": ...}
                        call_id = (
                            call.get("id")
                            if isinstance(call, dict)
                            else getattr(call, "id", "")
                        )
                        call_name = (
                            call.get("name")
                            if isinstance(call, dict)
                            else getattr(call, "name", "")
                        )
                        call_args = (
                            call.get("args")
                            if isinstance(call, dict)
                            else getattr(call, "args", {})
                        )

                        # 如果 args 是字符串，尝试解析
                        if isinstance(call_args, str):
                            try:
                                call_args = json.loads(call_args)
                            except json.JSONDecodeError:
                                call_args = {}

                        tool_calls.append(
                            CanonicalToolCall(
                                id=str(call_id),
                                name=str(call_name),
                                arguments=(
                                    call_args
                                    if isinstance(call_args, dict)
                                    else {}
                                ),
                            )
                        )

                canonical.append(
                    CanonicalMessage(
                        role=MessageRole.ASSISTANT,
                        content=msg.content
                        if hasattr(msg, "content")
                        else None,
                        tool_calls=tool_calls,
                    )
                )
            elif isinstance(msg, ToolMessage):
                content = msg.content
                if type(content) is not str:
                    content = str(content)

                canonical.append(
                    CanonicalMessage(
                        role=MessageRole.TOOL,
                        content=content,
                        tool_call_id=(
                            msg.tool_call_id
                            if hasattr(msg, "tool_call_id")
                            else None
                        ),
                    )
                )
            else:
                # 未知消息类型，尝试提取基本信息
                role_str = getattr(msg, "type", "user").lower()
                if "system" in role_str:
                    role = MessageRole.SYSTEM
                elif "assistant" in role_str or "ai" in role_str:
                    role = MessageRole.ASSISTANT
                elif "tool" in role_str:
                    role = MessageRole.TOOL
                else:
                    role = MessageRole.USER

                content = getattr(msg, "content", None)
                canonical.append(CanonicalMessage(role=role, content=content))

        return canonical

    def from_canonical(self, messages: List[CanonicalMessage]) -> Any:
        """将中间格式转换为 LangChain BaseMessage"""
        try:
            from langchain_core.messages import (
                AIMessage,
                HumanMessage,
                SystemMessage,
                ToolMessage,
            )
        except ImportError as e:
            raise ImportError(
                "LangChain is not installed. "
                "Install it with: pip install langchain-core"
            ) from e

        result = []
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                result.append(SystemMessage(content=msg.content or ""))
            elif msg.role == MessageRole.USER:
                result.append(HumanMessage(content=msg.content or ""))
            elif msg.role == MessageRole.ASSISTANT:
                tool_calls = None
                if msg.tool_calls:
                    tool_calls = [
                        {
                            "id": call.id,
                            "name": call.name,
                            "args": call.arguments,
                        }
                        for call in msg.tool_calls
                    ]
                result.append(
                    AIMessage(
                        content=msg.content or "",
                        tool_calls=tool_calls,
                    )
                )
            elif msg.role == MessageRole.TOOL:
                result.append(
                    ToolMessage(
                        content=msg.content or "",
                        tool_call_id=msg.tool_call_id or "",
                    )
                )

        return result


class LangChainToolAdapter(ToolAdapter):
    """LangChain 工具适配器

    实现 LangChain StructuredTool ↔ CanonicalTool 的转换。
    """

    def to_canonical(self, tools: Any) -> List[CanonicalTool]:
        """将 LangChain StructuredTool 转换为中间格式"""
        from agentrun.integration.utils.tool import _json_schema_to_pydantic

        canonical = []
        for tool in tools:
            # 提取工具信息
            name = getattr(tool, "name", "")
            description = getattr(tool, "description", "")

            # 提取参数 schema
            parameters = {}
            if hasattr(tool, "args_schema") and tool.args_schema:
                try:
                    parameters = tool.args_schema.model_json_schema()
                except Exception:
                    # 如果无法获取 schema，使用空字典
                    parameters = {"type": "object", "properties": {}}
            else:
                parameters = {"type": "object", "properties": {}}

            # 提取函数
            func = getattr(tool, "func", None)
            if func is None and hasattr(tool, "_func"):
                func = tool._func

            canonical.append(
                CanonicalTool(
                    name=name,
                    description=description,
                    parameters=parameters,
                    func=func,
                )
            )

        return canonical

    def from_canonical(self, tools: List[CanonicalTool]) -> Any:
        """将中间格式转换为 LangChain StructuredTool"""
        try:
            from langchain_core.tools import StructuredTool
        except ImportError as e:
            raise ImportError(
                "LangChain is not installed. "
                "Install it with: pip install langchain-core"
            ) from e

        from agentrun.integration.utils.tool import _json_schema_to_pydantic

        result = []
        for tool in tools:
            # 从 JSON Schema 创建 Pydantic 模型
            args_schema = _json_schema_to_pydantic(
                f"{tool.name}_Args", tool.parameters
            )

            if args_schema is None:
                # 如果无法创建 schema，使用空模型
                from pydantic import create_model

                args_schema = create_model(f"{tool.name}_Args")

            result.append(
                StructuredTool.from_function(
                    func=tool.func,
                    name=tool.name,
                    description=tool.description,
                    args_schema=args_schema,
                )
            )

        return result


class LangChainModelAdapter(ModelAdapter):
    """LangChain 模型适配器

    将 CommonModel 包装为 LangChain BaseChatModel。
    """

    def wrap_model(self, common_model: Any) -> Any:
        """包装 CommonModel 为 LangChain BaseChatModel"""
        try:
            from langchain_core.callbacks.manager import (
                CallbackManagerForLLMRun,
            )
            from langchain_core.language_models.chat_models import BaseChatModel
            from langchain_core.messages import AIMessage, BaseMessage
            from langchain_core.outputs import ChatGeneration, ChatResult
        except ImportError as e:
            raise ImportError(
                "LangChain is not installed. "
                "Install it with: pip install langchain-core"
            ) from e

        from agentrun.integration.utils.converter import get_converter

        converter = get_converter()
        message_adapter = converter._message_adapters.get("langchain")

        if message_adapter is None:
            # 如果适配器未注册，使用旧的实现方式
            return common_model.to_langchain()

        class AgentRunLangChainChatModel(BaseChatModel):
            """LangChain ChatModel 封装 AgentRun CommonModel"""

            model_name: str = common_model.name

            def __init__(
                self,
                model_name: str = None,
                _common_model: Any = None,
                _message_adapter: Any = None,
                **kwargs,
            ):
                super().__init__(**kwargs)
                if _common_model is not None:
                    # 从现有实例复制
                    self._common_model = _common_model
                    self._message_adapter = _message_adapter
                    if model_name:
                        self.model_name = model_name
                else:
                    # 新实例
                    self._common_model = common_model
                    self._message_adapter = message_adapter
                self._bound_tools = getattr(self, "_bound_tools", None)
                self._tool_choice = getattr(self, "_tool_choice", None)

            @property
            def _llm_type(self) -> str:
                return "agentrun-common-model"

            def bind_tools(
                self,
                tools: Any,
                *,
                tool_choice: Any = None,
                **kwargs: Any,
            ) -> Any:
                """绑定工具到模型

                Args:
                    tools: 工具列表，可以是 StructuredTool、函数、字典等
                    tool_choice: 工具选择策略
                    **kwargs: 其他参数

                Returns:
                    绑定了工具的新模型实例
                """
                from typing import Sequence

                from langchain_core.tools import BaseTool, StructuredTool

                # 转换工具为 OpenAI 格式
                openai_tools = []
                for tool in tools:
                    if isinstance(tool, dict):
                        # 已经是字典格式
                        openai_tools.append(tool)
                    elif isinstance(tool, (BaseTool, StructuredTool)):
                        # LangChain 工具，转换为 OpenAI 格式
                        tool_schema = {}
                        if hasattr(tool, "args_schema") and tool.args_schema:
                            try:
                                tool_schema = (
                                    tool.args_schema.model_json_schema()
                                )
                            except Exception:
                                tool_schema = {
                                    "type": "object",
                                    "properties": {},
                                }

                        openai_tools.append({
                            "type": "function",
                            "function": {
                                "name": getattr(tool, "name", ""),
                                "description": getattr(tool, "description", ""),
                                "parameters": tool_schema,
                            },
                        })
                    elif callable(tool):
                        # 函数，尝试提取信息
                        import inspect

                        sig = inspect.signature(tool)
                        params = {}
                        for param_name, param in sig.parameters.items():
                            if param_name == "self":
                                continue
                            param_type = "string"
                            if param.annotation != inspect.Parameter.empty:
                                ann_str = str(param.annotation)
                                if "int" in ann_str:
                                    param_type = "integer"
                                elif "float" in ann_str or "number" in ann_str:
                                    param_type = "number"
                                elif "bool" in ann_str:
                                    param_type = "boolean"
                                elif "list" in ann_str or "List" in ann_str:
                                    param_type = "array"
                                elif "dict" in ann_str or "Dict" in ann_str:
                                    param_type = "object"

                            param_info = {"type": param_type}
                            if param.default != inspect.Parameter.empty:
                                param_info["default"] = param.default
                            params[param_name] = param_info

                        openai_tools.append({
                            "type": "function",
                            "function": {
                                "name": getattr(tool, "__name__", "unknown"),
                                "description": getattr(tool, "__doc__", ""),
                                "parameters": {
                                    "type": "object",
                                    "properties": params,
                                    "required": [
                                        name
                                        for name, param in sig.parameters.items()
                                        if param.default
                                        == inspect.Parameter.empty
                                        and name != "self"
                                    ],
                                },
                            },
                        })
                    else:
                        # 其他类型，尝试转换为字典
                        try:
                            if hasattr(tool, "to_openai_function"):
                                openai_tools.append(tool.to_openai_function())
                            elif hasattr(tool, "dict"):
                                openai_tools.append(tool.dict())
                            elif hasattr(tool, "model_dump"):
                                openai_tools.append(tool.model_dump())
                        except Exception:
                            # 如果无法转换，跳过
                            continue

                # 创建新的模型实例，保存工具信息
                bound_model = AgentRunLangChainChatModel(
                    model_name=self.model_name,
                    _common_model=self._common_model,
                    _message_adapter=self._message_adapter,
                )
                bound_model._bound_tools = openai_tools
                bound_model._tool_choice = tool_choice

                return bound_model

            def _generate(  # type: ignore[override]
                self,
                messages: List[BaseMessage],
                stop: Optional[List[str]] = None,
                run_manager: Optional[CallbackManagerForLLMRun] = None,
                **kwargs: Any,
            ) -> ChatResult:
                # 使用适配器转换消息
                canonical_messages = self._message_adapter.to_canonical(
                    messages
                )

                # 转换为 OpenAI 格式（CommonModel 使用的格式）
                openai_messages = []
                for msg in canonical_messages:
                    msg_dict = msg.to_dict()
                    openai_messages.append(msg_dict)

                # 调用底层模型
                payload: dict = {"messages": openai_messages}
                if stop:
                    kwargs = {**kwargs, "stop": stop}

                # 如果有绑定的工具，添加到请求中
                if hasattr(self, "_bound_tools") and self._bound_tools:
                    kwargs["tools"] = self._bound_tools

                response = self._common_model.completions(**payload, **kwargs)

                # 转换响应
                ai_message = self._convert_response(response)
                generation = ChatGeneration(message=ai_message)
                llm_output = {"usage": getattr(response, "usage", None)}
                return ChatResult(
                    generations=[generation], llm_output=llm_output
                )

            @staticmethod
            def _convert_response(response: Any) -> AIMessage:
                """转换模型响应为 AIMessage"""
                # 尝试提取响应信息
                response_dict = {}
                if hasattr(response, "model_dump"):
                    response_dict = response.model_dump()
                elif hasattr(response, "dict"):
                    response_dict = response.dict()
                elif isinstance(response, dict):
                    response_dict = response
                elif hasattr(response, "__dict__"):
                    response_dict = {
                        k: v
                        for k, v in response.__dict__.items()
                        if not k.startswith("_")
                    }

                choices = response_dict.get("choices") or []
                if choices:
                    first_choice = (
                        choices[0]
                        if isinstance(choices[0], dict)
                        else choices[0].__dict__
                    )
                    message_dict = first_choice.get("message", {})
                    if not isinstance(message_dict, dict):
                        message_dict = (
                            message_dict.__dict__
                            if hasattr(message_dict, "__dict__")
                            else {}
                        )

                    content = message_dict.get("content", "")
                    tool_calls_raw = message_dict.get("tool_calls") or []

                    tool_calls = []
                    for call in tool_calls_raw:
                        if isinstance(call, dict):
                            call_dict = call
                        else:
                            call_dict = (
                                call.__dict__
                                if hasattr(call, "__dict__")
                                else {}
                            )

                        function_dict = call_dict.get("function", {})
                        if not isinstance(function_dict, dict):
                            function_dict = (
                                function_dict.__dict__
                                if hasattr(function_dict, "__dict__")
                                else {}
                            )

                        args_str = function_dict.get("arguments", "{}")
                        if isinstance(args_str, str):
                            try:
                                args = json.loads(args_str)
                            except json.JSONDecodeError:
                                args = {}
                        else:
                            args = args_str

                        tool_calls.append({
                            "id": call_dict.get("id", ""),
                            "name": function_dict.get("name", ""),
                            "args": args,
                        })

                    # 构建 AIMessage，tool_calls 不能为 None
                    message_kwargs = {
                        "content": content or "",
                        "response_metadata": {
                            "usage": response_dict.get("usage")
                        },
                    }
                    if tool_calls:
                        message_kwargs["tool_calls"] = tool_calls

                    return AIMessage(**message_kwargs)

                return AIMessage(content=str(response))

        return AgentRunLangChainChatModel()
