"""Google ADK 适配器实现

提供 Google ADK 框架的消息、工具和模型适配器。
"""

import json
from typing import Any, List

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


class GoogleADKMessageAdapter(MessageAdapter):
    """Google ADK 消息适配器

    实现 Google ADK LlmRequest/LlmResponse ↔ CanonicalMessage 的转换。
    """

    def to_canonical(self, messages: Any) -> List[CanonicalMessage]:
        """将 Google ADK LlmRequest 转换为中间格式"""
        canonical = []

        # Google ADK 使用 LlmRequest，包含 contents 列表
        if hasattr(messages, "contents"):
            contents = messages.contents
        elif isinstance(messages, list):
            contents = messages
        else:
            contents = [messages]

        # 处理 system_instruction (在 config 中)
        if hasattr(messages, "config") and messages.config:
            if (
                hasattr(messages.config, "system_instruction")
                and messages.config.system_instruction
            ):
                canonical.append(
                    CanonicalMessage(
                        role=MessageRole.SYSTEM,
                        content=messages.config.system_instruction,
                    )
                )

        # 处理 contents
        for content in contents:
            # 确定角色
            role = MessageRole.USER
            if hasattr(content, "role"):
                role_str = str(content.role).lower()
                if "model" in role_str or "assistant" in role_str:
                    role = MessageRole.ASSISTANT
                elif "system" in role_str:
                    role = MessageRole.SYSTEM
                elif "tool" in role_str:
                    role = MessageRole.TOOL
                elif "function" in role_str:
                    role = MessageRole.TOOL
                else:
                    role = MessageRole.USER

            # 处理 parts
            if hasattr(content, "parts"):
                text_parts = []
                tool_calls = []
                tool_call_id = None

                for part in content.parts:
                    # 处理文本
                    if hasattr(part, "text") and part.text:
                        text_parts.append(part.text)

                    # 处理 function_call
                    elif hasattr(part, "function_call") and part.function_call:
                        func_call = part.function_call
                        args = {}
                        if hasattr(func_call, "args"):
                            if isinstance(func_call.args, dict):
                                args = func_call.args
                            else:
                                try:
                                    args = json.loads(str(func_call.args))
                                except (json.JSONDecodeError, TypeError):
                                    args = {}

                        tool_calls.append(
                            CanonicalToolCall(
                                id=getattr(
                                    func_call, "id", f"call_{len(tool_calls)}"
                                ),
                                name=getattr(func_call, "name", ""),
                                arguments=args,
                            )
                        )

                    # 处理 function_response
                    elif (
                        hasattr(part, "function_response")
                        and part.function_response
                    ):
                        func_resp = part.function_response
                        response_content = ""
                        if hasattr(func_resp, "response"):
                            if isinstance(func_resp.response, dict):
                                response_content = json.dumps(
                                    func_resp.response
                                )
                            else:
                                response_content = str(func_resp.response)
                        else:
                            response_content = str(func_resp)

                        # function_response 表示工具返回结果
                        canonical.append(
                            CanonicalMessage(
                                role=MessageRole.TOOL,
                                content=response_content,
                                tool_call_id=getattr(func_resp, "id", "call_0"),
                            )
                        )
                        continue

                # 构建消息
                if text_parts or tool_calls:
                    content_text = " ".join(text_parts) if text_parts else None
                    canonical.append(
                        CanonicalMessage(
                            role=role,
                            content=content_text,
                            tool_calls=tool_calls if tool_calls else None,
                        )
                    )
            else:
                # 没有 parts，直接使用字符串内容
                content_text = str(content) if content else None
                canonical.append(
                    CanonicalMessage(role=role, content=content_text)
                )

        return canonical

    def from_canonical(self, messages: List[CanonicalMessage]) -> Any:
        """将中间格式转换为 Google ADK LlmRequest"""
        try:
            from google.adk.models.llm_request import LlmRequest
            from google.genai import types as genai_types
        except ImportError as e:
            raise ImportError(
                "Google ADK not installed. "
                "Install it with: pip install google-generativeai"
            ) from e

        contents = []
        system_instruction = None

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                # System message 作为 system_instruction
                system_instruction = msg.content
                continue

            parts = []

            # 处理文本内容
            if msg.content:
                parts.append(genai_types.Part(text=msg.content))

            # 处理工具调用
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    func_call = genai_types.FunctionCall(
                        name=tool_call.name,
                        args=tool_call.arguments,
                    )
                    parts.append(genai_types.Part(function_call=func_call))

            # 处理工具返回结果
            if msg.role == MessageRole.TOOL and msg.tool_call_id:
                func_response = genai_types.FunctionResponse(
                    name="",  # 需要从上下文获取
                    response=json.loads(msg.content) if msg.content else {},
                )
                parts.append(genai_types.Part(function_response=func_response))
                continue

            # 如果没有 parts，添加空文本
            if not parts:
                parts.append(genai_types.Part(text=""))

            # 确定角色
            role_str = "user"
            if msg.role == MessageRole.ASSISTANT:
                role_str = "model"
            elif msg.role == MessageRole.TOOL:
                role_str = "function"

            content = genai_types.Content(parts=parts, role=role_str)
            contents.append(content)

        # 创建 LlmRequest
        llm_request = LlmRequest(contents=contents)
        if system_instruction:
            # 设置 system_instruction
            try:
                from google.adk.models.llm_request_config import (
                    LlmRequestConfig,
                )

                config = LlmRequestConfig(system_instruction=system_instruction)
                llm_request.config = config
            except ImportError:
                # 如果无法导入，尝试直接设置
                if hasattr(llm_request, "config"):
                    llm_request.config = type(
                        "Config", (), {"system_instruction": system_instruction}
                    )()

        return llm_request


class GoogleADKToolAdapter(ToolAdapter):
    """Google ADK 工具适配器

    实现 Google ADK BaseTool ↔ CanonicalTool 的转换。
    Google ADK 直接使用 Python 函数作为工具，所以转换相对简单。
    """

    def to_canonical(self, tools: Any) -> List[CanonicalTool]:
        """将 Google ADK 工具转换为中间格式"""
        canonical = []

        # Google ADK 工具可以是函数列表或字典
        if not isinstance(tools, list):
            tools = [tools]

        for tool in tools:
            # Google ADK 工具通常是函数
            if callable(tool):
                name = getattr(tool, "__name__", "")
                description = getattr(tool, "__doc__", "") or ""

                # 尝试从函数签名提取参数 schema
                import inspect

                sig = inspect.signature(tool)
                parameters = {
                    "type": "object",
                    "properties": {},
                    "required": [],
                }

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

                    parameters["properties"][param_name] = {
                        "type": param_type,
                        "description": "",
                    }

                    if param.default == inspect.Parameter.empty:
                        parameters["required"].append(param_name)

                canonical.append(
                    CanonicalTool(
                        name=name,
                        description=description,
                        parameters=parameters,
                        func=tool,
                    )
                )
            else:
                # 如果不是函数，尝试提取信息
                name = getattr(tool, "name", str(tool))
                description = getattr(tool, "description", "")
                parameters = getattr(
                    tool, "input_schema", {"type": "object", "properties": {}}
                )
                func = getattr(tool, "func", None)

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
        """将中间格式转换为 Google ADK 工具

        Google ADK 直接使用 Python 函数，所以直接返回函数。
        """
        result = []
        for tool in tools:
            if tool.func is None:
                # 如果没有函数，创建一个包装函数
                def make_wrapper(tool_name: str, tool_params: dict):
                    def wrapper(**kwargs):
                        # 这里应该调用实际的工具实现
                        # 但 Google ADK 需要实际的函数
                        raise NotImplementedError(
                            f"Tool {tool_name} has no function implementation"
                        )

                    wrapper.__name__ = tool_name
                    wrapper.__doc__ = tool.description
                    return wrapper

                result.append(make_wrapper(tool.name, tool.parameters))
            else:
                # 直接返回函数
                result.append(tool.func)

        return result


class GoogleADKModelAdapter(ModelAdapter):
    """Google ADK 模型适配器

    将 CommonModel 包装为 Google ADK BaseLlm。
    """

    def wrap_model(self, common_model: Any) -> Any:
        """包装 CommonModel 为 Google ADK BaseLlm"""
        try:
            from google.adk.models.base_llm import BaseLlm
            from google.adk.models.llm_request import LlmRequest
            from google.adk.models.llm_response import LlmResponse
            from google.genai import types as genai_types
        except ImportError as e:
            raise ImportError(
                "Google ADK not installed. "
                "Install it with: pip install google-generativeai"
            ) from e

        from agentrun.integration.utils.converter import get_converter

        converter = get_converter()
        message_adapter = converter._message_adapters.get("google_adk")

        if message_adapter is None:
            # 如果适配器未注册，使用旧的实现方式
            return common_model.to_google_adk()

        model_instance = common_model

        class AgentRunLlm(BaseLlm):
            """AgentRun 模型适配为 Google ADK BaseLlm"""

            def __init__(self, **kwargs):
                super().__init__(model=model_instance.name, **kwargs)
                self._common_model = model_instance
                self._message_adapter = message_adapter

            async def generate_content_async(
                self, llm_request: LlmRequest, stream: bool = False
            ):
                """实现 BaseLlm 的抽象方法"""
                # 使用适配器转换消息
                canonical_messages = self._message_adapter.to_canonical(
                    llm_request
                )

                # 转换为 OpenAI 格式（CommonModel 使用的格式）
                openai_messages = []
                for msg in canonical_messages:
                    msg_dict = msg.to_dict()
                    openai_messages.append(msg_dict)

                # 处理工具
                tools = None
                if (
                    hasattr(llm_request, "tools_dict")
                    and llm_request.tools_dict
                ):
                    tools = []
                    for tool_name, tool_obj in llm_request.tools_dict.items():
                        tool_def = {
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "description": getattr(
                                    tool_obj, "description", ""
                                ),
                            },
                        }
                        if hasattr(tool_obj, "input_schema"):
                            tool_def["function"][
                                "parameters"
                            ] = tool_obj.input_schema
                        tools.append(tool_def)

                # 调用底层模型
                kwargs = {"messages": openai_messages, "stream": stream}
                if tools:
                    kwargs["tools"] = tools

                response = model_instance.completions(**kwargs)

                # 转换响应为 LlmResponse
                if hasattr(response, "choices") and response.choices:
                    choice = response.choices[0]
                    message = choice.message

                    parts = []

                    # 处理文本内容
                    if hasattr(message, "content") and message.content:
                        parts.append(genai_types.Part(text=message.content))

                    # 处理工具调用
                    if hasattr(message, "tool_calls") and message.tool_calls:
                        for tool_call in message.tool_calls:
                            func_call = genai_types.FunctionCall(
                                name=tool_call.function.name,
                                args=(
                                    json.loads(tool_call.function.arguments)
                                    if isinstance(
                                        tool_call.function.arguments, str
                                    )
                                    else tool_call.function.arguments
                                ),
                            )
                            parts.append(
                                genai_types.Part(function_call=func_call)
                            )

                    # 如果没有任何内容，添加空文本
                    if not parts:
                        parts.append(genai_types.Part(text=""))

                    content = genai_types.Content(parts=parts, role="model")
                else:
                    # 非标准响应
                    content = genai_types.Content(
                        parts=[genai_types.Part(text=str(response))],
                        role="model",
                    )

                llm_response = LlmResponse(content=content)
                yield llm_response

        return AgentRunLlm()
