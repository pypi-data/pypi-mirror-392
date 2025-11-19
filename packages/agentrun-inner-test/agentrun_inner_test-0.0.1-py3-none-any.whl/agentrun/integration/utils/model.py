"""通用模型定义和转换模块

提供跨框架的通用模型定义和转换功能。
"""

import json
from typing import Any, Dict, List, Optional

from agentrun.utils.config import Config


class CommonModel:
    """通用模型定义

    封装 AgentRun 模型，提供跨框架转换能力。
    """

    def __init__(
        self,
        name: str,
        model_obj: Any,
        backend_type: Optional[str] = None,
        config: Optional[Config] = None,
    ):
        self.name = name
        self.model_obj = model_obj
        self.backend_type = backend_type
        self.config = config or Config()

    def completions(self, *args, **kwargs):
        """调用底层模型的 completions 方法"""
        return self.model_obj.completions(*args, **kwargs)

    def responses(self, *args, **kwargs):
        """调用底层模型的 responses 方法"""
        return self.model_obj.responses(*args, **kwargs)

    def to_google_adk(self) -> Any:
        """转换为 Google ADK BaseLlm

        优先使用适配器模式，如果适配器未注册则回退到旧实现。
        """
        # 尝试使用适配器模式
        try:
            from agentrun.integration.utils.converter import get_converter

            converter = get_converter()
            adapter = converter.get_model_adapter("google_adk")
            if adapter is not None:
                return adapter.wrap_model(self)
        except (ImportError, AttributeError, KeyError):
            pass

        # 回退到旧实现（保持向后兼容）
        try:
            from google.adk.models.base_llm import BaseLlm
            from google.adk.models.llm_request import LlmRequest
            from google.adk.models.llm_response import LlmResponse
        except ImportError as e:
            raise ImportError(
                "Google ADK not installed. "
                "Install it with: pip install google-generativeai"
            ) from e

        model_instance = self

        class AgentRunLlm(BaseLlm):
            """AgentRun 模型适配为 Google ADK BaseLlm"""

            async def generate_content_async(
                self, llm_request: LlmRequest, stream: bool = False
            ):
                """实现 BaseLlm 的抽象方法"""
                # 转换 LlmRequest 为 OpenAI 格式的 messages
                messages = []

                # 处理 system_instruction (在 config 中)
                if hasattr(llm_request, "config") and llm_request.config:
                    if (
                        hasattr(llm_request.config, "system_instruction")
                        and llm_request.config.system_instruction
                    ):
                        messages.append({
                            "role": "system",
                            "content": llm_request.config.system_instruction,
                        })

                # 处理 contents
                if llm_request.contents:
                    for content in llm_request.contents:
                        # 映射 Google ADK 角色到 OpenAI 角色
                        role = "user"
                        if hasattr(content, "role"):
                            role_str = str(content.role).lower()
                            if "model" in role_str or "assistant" in role_str:
                                role = "assistant"
                            elif "system" in role_str:
                                role = "system"
                            elif "tool" in role_str:
                                role = "tool"
                            elif "function" in role_str:
                                role = "function"
                            else:
                                role = "user"

                        # Content 对象有 parts 属性
                        if hasattr(content, "parts"):
                            text_parts = []
                            tool_calls = []

                            for part in content.parts:
                                # 处理文本
                                if hasattr(part, "text") and part.text:
                                    text_parts.append(part.text)

                                # 处理 function_call
                                elif (
                                    hasattr(part, "function_call")
                                    and part.function_call
                                ):
                                    import json

                                    func_call = part.function_call
                                    tool_calls.append({
                                        "id": f"call_{len(tool_calls)}",
                                        "type": "function",
                                        "function": {
                                            "name": func_call.name,
                                            "arguments": (
                                                json.dumps(func_call.args)
                                                if hasattr(func_call, "args")
                                                else "{}"
                                            ),
                                        },
                                    })

                                # 处理 function_response
                                elif (
                                    hasattr(part, "function_response")
                                    and part.function_response
                                ):
                                    # 这是工具的返回结果
                                    import json

                                    func_resp = part.function_response
                                    messages.append({
                                        "role": "tool",
                                        "tool_call_id": (
                                            f"call_0"
                                        ),  # 需要匹配之前的 tool_call_id
                                        "content": (
                                            json.dumps(func_resp.response)
                                            if hasattr(func_resp, "response")
                                            else str(func_resp)
                                        ),
                                    })
                                    continue

                            # 构建消息
                            if text_parts or tool_calls:
                                msg = {"role": role}

                                if text_parts:
                                    msg["content"] = " ".join(text_parts)

                                if tool_calls and role == "assistant":
                                    msg["tool_calls"] = tool_calls
                                    if not text_parts:
                                        msg["content"] = None

                                messages.append(msg)
                        else:
                            messages.append(
                                {"role": role, "content": str(content)}
                            )

                # 处理工具（转换为 OpenAI tools 格式）
                tools = None
                if (
                    hasattr(llm_request, "tools_dict")
                    and llm_request.tools_dict
                ):
                    tools = []
                    for tool_name, tool_obj in llm_request.tools_dict.items():
                        # 从 Google ADK BaseTool 提取信息
                        tool_def = {
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "description": getattr(
                                    tool_obj, "description", ""
                                ),
                            },
                        }

                        # 尝试获取参数定义
                        if hasattr(tool_obj, "input_schema"):
                            tool_def["function"][
                                "parameters"
                            ] = tool_obj.input_schema

                        tools.append(tool_def)

                # 调用底层模型
                kwargs = {"messages": messages, "stream": stream}
                if tools:
                    kwargs["tools"] = tools

                response = model_instance.completions(**kwargs)

                # 转换响应为 LlmResponse
                from google.genai import types as genai_types

                if hasattr(response, "choices") and response.choices:
                    choice = response.choices[0]
                    message = choice.message

                    # 构造 Content 对象
                    parts = []

                    # 处理文本内容
                    if hasattr(message, "content") and message.content:
                        parts.append(genai_types.Part(text=message.content))

                    # 处理 tool calls
                    if hasattr(message, "tool_calls") and message.tool_calls:
                        for tool_call in message.tool_calls:
                            import json

                            # 构造 function call part
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

        # BaseLlm 需要一个 model 字段（模型名称）
        return AgentRunLlm(model=self.name)

    def to_langchain(self) -> Any:
        """转换为 LangChain ChatModel

        优先使用适配器模式，如果适配器未注册则回退到旧实现。
        """
        # 尝试使用适配器模式
        try:
            from agentrun.integration.utils.converter import get_converter

            converter = get_converter()
            adapter = converter.get_model_adapter("langchain")
            if adapter is not None:
                return adapter.wrap_model(self)
        except (ImportError, AttributeError, KeyError):
            pass

        # 回退到旧实现（保持向后兼容）
        try:
            from langchain_core.callbacks.manager import (
                CallbackManagerForLLMRun,
            )
            from langchain_core.language_models.chat_models import BaseChatModel
            from langchain_core.messages import (
                AIMessage,
                BaseMessage,
                HumanMessage,
                SystemMessage,
                ToolMessage,
            )
            from langchain_core.outputs import ChatGeneration, ChatResult
        except ImportError as exc:
            raise ImportError(
                "LangChain is not installed. Install it with: pip install"
                " langchain-core"
            ) from exc

        common_model = self

        class AgentRunLangChainChatModel(BaseChatModel):
            """LangChain ChatModel 封装 AgentRun CommonModel"""

            model_name: str = common_model.name

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._common_model = common_model

            @property
            def _llm_type(self) -> str:
                return "agentrun-common-model"

            @staticmethod
            def _maybe_parse_arguments(args: Any) -> Any:
                if args is None:
                    return {}
                if isinstance(args, (dict, list)):
                    return args
                if isinstance(args, str):
                    try:
                        return json.loads(args)
                    except json.JSONDecodeError:
                        return args
                return args

            @staticmethod
            def _to_plain_dict(value: Any) -> Dict[str, Any]:
                if isinstance(value, dict):
                    return value
                for attr in ("model_dump", "dict"):
                    if hasattr(value, attr):
                        try:
                            return getattr(value, attr)()
                        except Exception:  # pragma: no cover - best effort
                            continue
                if hasattr(value, "__dict__"):
                    return {
                        key: val
                        for key, val in value.__dict__.items()
                        if not key.startswith("_")
                    }
                return {}

            @classmethod
            def _convert_messages(
                cls, messages: List[BaseMessage]
            ) -> List[Dict[str, Any]]:
                converted: List[Dict[str, Any]] = []
                for message in messages:
                    if isinstance(message, SystemMessage):
                        converted.append(
                            {"role": "system", "content": message.content}
                        )
                    elif isinstance(message, HumanMessage):
                        converted.append(
                            {"role": "user", "content": message.content}
                        )
                    elif isinstance(message, AIMessage):
                        entry: Dict[str, Any] = {
                            "role": "assistant",
                            "content": message.content,
                        }
                        tool_calls = []
                        for call in message.tool_calls or []:
                            tool_calls.append({
                                "id": call.get("id"),
                                "type": "function",
                                "function": {
                                    "name": call.get("name"),
                                    "arguments": json.dumps(
                                        call.get("args", {})
                                    ),
                                },
                            })
                        if tool_calls:
                            entry["tool_calls"] = tool_calls
                        converted.append(entry)
                    elif isinstance(message, ToolMessage):
                        converted.append({
                            "role": "tool",
                            "content": message.content,
                            "tool_call_id": message.tool_call_id,
                        })
                    else:
                        entry: Dict[str, Any] = {
                            "role": getattr(message, "role", message.type),
                            "content": getattr(message, "content", ""),
                        }
                        converted.append(entry)
                return converted

            @classmethod
            def _convert_response(cls, response: Any) -> AIMessage:
                response_dict = cls._to_plain_dict(response)
                choices = response_dict.get("choices") or []
                if choices:
                    first_choice = cls._to_plain_dict(choices[0])
                    message_dict = cls._to_plain_dict(
                        first_choice.get("message", {})
                    )
                    tool_calls_raw = message_dict.get("tool_calls") or []
                    tool_calls = []
                    for call in tool_calls_raw:
                        call_dict = cls._to_plain_dict(call)
                        function_dict = cls._to_plain_dict(
                            call_dict.get("function", {})
                        )
                        tool_calls.append({
                            "id": call_dict.get("id"),
                            "name": function_dict.get("name"),
                            "args": cls._maybe_parse_arguments(
                                function_dict.get("arguments")
                            ),
                        })
                    additional_kwargs = {
                        key: value
                        for key, value in message_dict.items()
                        if key not in {"role", "content", "tool_calls"}
                    }
                    return AIMessage(
                        content=message_dict.get("content", ""),
                        tool_calls=tool_calls or None,
                        additional_kwargs=additional_kwargs,
                        response_metadata={"usage": response_dict.get("usage")},
                    )

                return AIMessage(content=str(response))

            def _generate(  # type: ignore[override]
                self,
                messages: List[BaseMessage],
                stop: Optional[List[str]] = None,
                run_manager: Optional[CallbackManagerForLLMRun] = None,
                **kwargs: Any,
            ) -> ChatResult:
                payload: Dict[str, Any] = {
                    "messages": self._convert_messages(messages)
                }
                if stop:
                    kwargs = {**kwargs, "stop": stop}
                response = self._common_model.completions(**payload, **kwargs)
                ai_message = self._convert_response(response)
                generation = ChatGeneration(message=ai_message)
                llm_output = {"usage": getattr(response, "usage", None)}
                return ChatResult(
                    generations=[generation], llm_output=llm_output
                )

        return AgentRunLangChainChatModel()

    def __call__(self, messages: list, **kwargs) -> Any:
        """直接调用模型"""
        return self.completions(messages=messages, **kwargs)

    def langchain(self) -> Any:
        """to_langchain 的别名"""
        return self.to_langchain()


def model(
    name: str,
    backend_type: Optional[str] = None,
    config: Optional[Config] = None,
) -> CommonModel:
    """获取 AgentRun 模型并封装为通用 Model 对象

    等价于 ModelClient.get()，但返回通用 Model 对象。

    Args:
        name: 模型名称
        backend_type: 后端类型 ("proxy" 或 "service")
        config: 配置对象

    Returns:
        Model 实例
    """
    from agentrun.model.client import ModelClient
    from agentrun.model.model import BackendType

    if config is None:
        config = Config()

    client = ModelClient(config=config)

    # 转换 backend_type
    backend_type_enum = None
    if backend_type is not None:
        if backend_type.lower() == "proxy":
            backend_type_enum = BackendType.PROXY
        elif backend_type.lower() == "service":
            backend_type_enum = BackendType.SERVICE
        else:
            raise ValueError(
                f"Invalid backend_type: {backend_type}. "
                "Must be 'proxy' or 'service'"
            )

    # 获取模型对象
    model_obj = client.get(
        name=name, backend_type=backend_type_enum, config=config
    )

    # 确定实际的 backend_type
    actual_backend_type = None
    if hasattr(model_obj, "model_proxy_name"):
        actual_backend_type = "proxy"
    elif hasattr(model_obj, "model_service_name"):
        actual_backend_type = "service"

    return CommonModel(
        name=name,
        model_obj=model_obj,
        backend_type=actual_backend_type,
        config=config,
    )


def from_agentrun_model(
    model_obj: Any,
    config: Optional[Config] = None,
) -> CommonModel:
    """从 AgentRun 模型对象创建通用 Model

    Args:
        model_obj: ModelProxy 或 ModelService 实例
        config: 配置对象

    Returns:
        Model 实例
    """
    # 确定模型名称和类型
    name = None
    backend_type = None

    if hasattr(model_obj, "model_proxy_name"):
        name = model_obj.model_proxy_name
        backend_type = "proxy"
    elif hasattr(model_obj, "model_service_name"):
        name = model_obj.model_service_name
        backend_type = "service"
    else:
        raise ValueError(
            f"Unsupported model type: {type(model_obj)}. "
            "Expected ModelProxy or ModelService"
        )

    if not name:
        raise ValueError("Model name is not available")

    return CommonModel(
        name=name,
        model_obj=model_obj,
        backend_type=backend_type,
        config=config or Config(),
    )
