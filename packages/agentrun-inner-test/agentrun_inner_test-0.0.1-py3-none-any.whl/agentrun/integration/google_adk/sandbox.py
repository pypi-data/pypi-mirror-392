"""Google ADK Sandbox 工具集成"""

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from agentrun.config import Config
    from agentrun.sandbox import Sandbox, SandboxConfig


class SandboxToolkit:
    """沙箱工具集

    为 Google ADK Agent 提供沙箱工具

    注意: 不需要预先安装 Google ADK,工具可以独立使用
    """

    def __init__(
        self,
        sandbox_type: str,
        config: Optional["Config"] = None,
        auto_create: bool = True,
    ):
        """初始化工具集

        Args:
            sandbox_type: 沙箱类型
            config: 全局配置
            auto_create: 是否自动创建沙箱
        """
        # 延迟导入,避免循环依赖
        from agentrun.config import Config

        self.sandbox_type = sandbox_type
        self.config = config or Config()
        self.sandbox = None
        self.auto_create = auto_create

        if auto_create:
            self._ensure_sandbox()

    def _ensure_sandbox(self) -> None:
        """确保沙箱已创建"""
        if self.sandbox is None:
            # 延迟导入
            from agentrun.sandbox import Sandbox, SandboxConfig

            self.sandbox = Sandbox.create(
                config=self.config,
                type=self.sandbox_type,
                sandbox_config=SandboxConfig(name=f"adk-{self.sandbox_type}"),
            )

    def tools(self) -> List[Callable]:
        """获取工具列表

        Returns:
            List[Callable]: Google ADK 兼容的工具函数列表
        """
        # 延迟导入
        from agentrun.sandbox import Sandbox

        if self.sandbox_type == Sandbox.BROWSER:
            return self._browser_tools()
        elif self.sandbox_type == Sandbox.CODE_INTERPRETER:
            return self._code_interpreter_tools()
        else:
            raise ValueError(f"Unsupported sandbox type: {self.sandbox_type}")

    def _browser_tools(self) -> List[Callable]:
        """浏览器工具"""

        def goto(url: str) -> Dict[str, Any]:
            """导航到指定 URL

            Args:
                url: 目标 URL

            Returns:
                操作结果
            """
            self._ensure_sandbox()
            self.sandbox.goto(url)
            return {"status": "success", "url": url}

        def screenshot() -> Dict[str, Any]:
            """截取当前页面截图

            Returns:
                包含截图数据的字典
            """
            self._ensure_sandbox()
            data = self.sandbox.screenshot()
            return {"status": "success", "screenshot": data}

        def get_content() -> Dict[str, Any]:
            """获取页面内容

            Returns:
                页面内容
            """
            self._ensure_sandbox()
            content = self.sandbox.html_content()
            return {"status": "success", "content": content}

        def click(selector: str) -> Dict[str, Any]:
            """点击元素

            Args:
                selector: CSS 选择器

            Returns:
                操作结果
            """
            self._ensure_sandbox()
            self.sandbox.click(selector)
            return {"status": "success", "selector": selector}

        return [goto, screenshot, get_content, click]

    def _code_interpreter_tools(self) -> List[Callable]:
        """代码解释器工具"""

        def execute_code(code: str, language: str = "python") -> Dict[str, Any]:
            """执行代码

            Args:
                code: 要执行的代码
                language: 编程语言

            Returns:
                执行结果
            """
            self._ensure_sandbox()
            result = self.sandbox.execute_code(code)
            return {
                "status": result.status,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_value": result.return_value,
            }

        def read_file(path: str) -> Dict[str, Any]:
            """读取文件

            Args:
                path: 文件路径

            Returns:
                文件内容
            """
            self._ensure_sandbox()
            content = self.sandbox.download_file(path)
            return {"status": "success", "content": content.decode("utf-8")}

        def write_file(path: str, content: str) -> Dict[str, Any]:
            """写入文件

            Args:
                path: 文件路径
                content: 文件内容

            Returns:
                操作结果
            """
            self._ensure_sandbox()
            self.sandbox.write(path, content)
            return {"status": "success", "path": path}

        return [execute_code, read_file, write_file]

    def cleanup(self) -> None:
        """清理资源"""
        if self.sandbox:
            try:
                self.sandbox.stop()
            except Exception:
                pass


def create_sandbox_tool(
    sandbox_type: str,
    config: Optional["Config"] = None,
    template_name: Optional[str] = None,
) -> SandboxToolkit:
    """创建沙箱工具集

    Args:
        sandbox_type: 沙箱类型
        config: 全局配置
        template_name: 模板名称

    Returns:
        SandboxToolkit: 工具集对象

    Examples:
        >>> from google.adk.agents.llm_agent import Agent
        >>> from agentrun.integration.google_adk import create_sandbox_tool
        >>>
        >>> toolkit = create_sandbox_tool(Sandbox.BROWSER)
        >>> agent = Agent(
        ...     model='gemini-2.5-flash',
        ...     tools=toolkit.tools()
        ... )
    """
    return SandboxToolkit(
        sandbox_type=sandbox_type, config=config, auto_create=True
    )


# 预定义的工具集
chrome_browser_sandbox = None  # 延迟初始化
python_code_interpreter_sandbox = None  # 延迟初始化


def _get_chrome_browser_sandbox() -> SandboxToolkit:
    """获取 Chrome 浏览器沙箱工具集"""
    # 延迟导入
    from agentrun.sandbox import Sandbox

    global chrome_browser_sandbox
    if chrome_browser_sandbox is None:
        chrome_browser_sandbox = SandboxToolkit(
            sandbox_type=Sandbox.BROWSER, auto_create=False
        )  # 不自动创建
    return chrome_browser_sandbox


def _get_python_code_interpreter_sandbox() -> SandboxToolkit:
    """获取 Python 代码解释器沙箱工具集"""
    # 延迟导入
    from agentrun.sandbox import Sandbox

    global python_code_interpreter_sandbox
    if python_code_interpreter_sandbox is None:
        python_code_interpreter_sandbox = SandboxToolkit(
            sandbox_type=Sandbox.CODE_INTERPRETER,
            auto_create=False,  # 不自动创建
        )
    return python_code_interpreter_sandbox


# 延迟初始化,只在实际使用时创建
# 用户可以直接导入这些对象,它们会在首次访问时初始化
def __getattr__(name: str) -> Any:
    """延迟初始化全局工具集对象"""
    if name == "chrome_browser_sandbox":
        return _get_chrome_browser_sandbox()
    elif name == "python_code_interpreter_sandbox":
        return _get_python_code_interpreter_sandbox()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
