from __future__ import annotations

import atexit
import threading
import time
from typing import Any, Dict, Optional

from agentrun.integration.utils.tool import CommonToolSet, tool
from agentrun.sandbox import Sandbox, TemplateType
from agentrun.utils.config import Config


class CodeInterpreterToolSet(CommonToolSet):
    """LangChain 代码沙箱工具适配器。"""

    def __init__(
        self,
        template_name: str,
        template_type: TemplateType,
        config: Optional[Config],
        sandbox_idle_timeout_seconds: int,
    ) -> None:
        self.template_name = template_name
        self.template_type = template_type
        self.config = config or Config()
        self.sandbox_idle_timeout_seconds = sandbox_idle_timeout_seconds

        self._sandbox = None
        self._lock = threading.Lock()
        atexit.register(self.close)
        super().__init__()

    def close(self) -> None:
        sandbox = self._sandbox
        if sandbox and sandbox.sandbox_id:
            try:
                sandbox.stop(sandbox_id=sandbox.sandbox_id)
            finally:
                self._sandbox = None

    def _ensure_sandbox(self):
        if self._sandbox is not None:
            return self._sandbox
        if self.template_type != TemplateType.CODE_INTERPRETER:
            raise NotImplementedError(
                "Only TemplateType.CODE_INTERPRETER is supported"
            )
        with self._lock:
            if self._sandbox is None:
                self._sandbox = Sandbox.create(
                    template_type=self.template_type,
                    template_name=self.template_name,
                    sandbox_idle_timeout_seconds=self.sandbox_idle_timeout_seconds,
                    config=self.config,
                )
                time.sleep(10)

        return self._sandbox

    @tool(
        name="sandbox_execute_code",
        description="在指定的 Code Interpreter 沙箱中执行代码",
    )
    def execute_code(
        self,
        code: str,
        language: str = "python",
        timeout: int = 60,
    ) -> Dict[str, Any]:

        with self._ensure_sandbox() as sandbox:
            with sandbox.context.create() as ctx:
                # time.sleep(5)
                try:
                    result = ctx.execute(code=code, timeout=timeout)
                finally:
                    try:
                        ctx.delete()
                    except Exception:
                        pass
                return {
                    "stdout": result.get("stdout"),
                    "stderr": result.get("stderr"),
                    "raw": result,
                }

    @tool(
        name="sandbox_list_directory",
        description="列出沙箱中的文件",
    )
    def list_directory(self, path: str = "/") -> Dict[str, Any]:
        sandbox = self._ensure_sandbox()
        return {
            "path": path,
            "entries": sandbox.file_system.list(path=path),
        }

    @tool(
        name="sandbox_read_file",
        description="读取沙箱文件内容",
    )
    def read_file(self, path: str) -> Dict[str, Any]:
        sandbox = self._ensure_sandbox()
        return {
            "path": path,
            "content": sandbox.file.read(path=path),
        }

    @tool(
        name="sandbox_write_file",
        description="向沙箱写入文本文件",
    )
    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        sandbox = self._ensure_sandbox()
        return {
            "path": path,
            "result": sandbox.file.write(path=path, content=content),
        }


def sandbox_toolset(
    template_name: str,
    *,
    template_type: TemplateType = TemplateType.CODE_INTERPRETER,
    config: Optional[Config] = None,
    sandbox_idle_timeout_seconds: int = 600,
    prefix: Optional[str] = None,
):
    """将沙箱模板封装为 LangChain ``StructuredTool`` 列表。"""

    if template_type != TemplateType.CODE_INTERPRETER:
        raise NotImplementedError(
            "sandbox_toolset currently supports only CODE_INTERPRETER templates"
        )

    toolset_adapter = CodeInterpreterToolSet(
        template_name=template_name,
        template_type=template_type,
        config=config,
        sandbox_idle_timeout_seconds=sandbox_idle_timeout_seconds,
    )

    return toolset_adapter
