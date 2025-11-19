from enum import Enum
from typing import Dict, List, Optional
import uuid

from pydantic import model_validator

from agentrun.utils.model import BaseModel, Field


class TemplateType(str, Enum):
    """沙箱模板类型"""

    CODE_INTERPRETER = "CodeInterpreter"
    """代码解释器"""
    BROWSER = "Browser"
    """浏览器"""


class TemplateNetworkMode(str, Enum):
    """Agent Runtime 网络访问模式"""

    PUBLIC = "PUBLIC"
    """公网模式"""
    PRIVATE = "PRIVATE"
    """私网模式"""
    PUBLIC_AND_PRIVATE = "PUBLIC_AND_PRIVATE"
    """公私网模式"""


class CodeLanguage(str, Enum):
    """Code Interpreter 代码语言"""

    PYTHON = "python"


class TemplateNetworkConfiguration(BaseModel):
    """沙箱模板网络配置"""

    network_mode: TemplateNetworkMode = TemplateNetworkMode.PUBLIC
    """网络访问模式"""
    security_group_id: Optional[str] = None
    """安全组 ID"""
    vpc_id: Optional[str] = None
    """私有网络 ID"""
    vswitch_ids: Optional[List[str]] = None
    """私有网络交换机 ID 列表"""


class TemplateOssConfiguration(BaseModel):
    """沙箱模板 OSS 配置"""

    bucket_name: Optional[str] = None
    """OSS 存储桶名称"""
    object_name: Optional[str] = None
    """OSS 对象名称"""


class TemplateLogConfiguration(BaseModel):
    """沙箱模板日志配置"""

    log_project: Optional[str] = None
    """SLS 日志项目"""
    log_store: Optional[str] = None
    """SLS 日志库"""


class TemplateCredentialConfiguration(BaseModel):
    """沙箱模板凭证配置"""

    credential_id: Optional[str] = None
    """凭证 ID"""


class TemplateArmsConfiguration(BaseModel):
    """沙箱模板 ARMS 监控配置"""

    arms_instance_id: Optional[str] = None

    """ARMS 实例 ID"""


class TemplateContainerConfiguration(BaseModel):
    """沙箱模板容器配置"""

    image: Optional[str] = None
    """容器镜像地址"""
    command: Optional[List[str]] = None
    """容器启动命令"""


class TemplateMcpOptions(BaseModel):
    """沙箱模板 MCP 选项配置"""

    enabled_tools: Optional[List[str]] = None

    """启用的工具列表"""
    transport: Optional[str] = None
    """传输协议"""


class TemplateMcpState(BaseModel):
    """沙箱模板 MCP 状态"""

    access_endpoint: Optional[str] = None
    """访问端点"""
    status: Optional[str] = None
    """状态"""
    status_reason: Optional[str] = None
    """状态原因"""


class TemplateInput(BaseModel):
    """沙箱模板配置"""

    template_name: Optional[str] = f"sandbox_template_{uuid.uuid4()}"
    """模板名称"""
    template_type: TemplateType
    """模板类型"""
    cpu: Optional[float] = 2.0
    """CPU 核数"""
    memory: Optional[int] = 4096
    """内存大小（MB）"""
    execution_role_arn: Optional[str] = None
    """执行角色 ARN"""
    sandbox_idle_timeout_in_seconds: Optional[int] = 3600
    """沙箱空闲超时时间（秒）"""
    sandbox_ttlin_seconds: Optional[int] = 600
    """沙箱存活时间（秒）"""
    share_concurrency_limit_per_sandbox: Optional[int] = 1
    """每个沙箱的最大并发会话数"""
    template_configuration: Optional[Dict] = None
    """模板配置"""
    description: Optional[str] = None
    """描述"""
    environment_variables: Optional[Dict] = None
    """环境变量"""
    network_configuration: Optional[TemplateNetworkConfiguration] = (
        TemplateNetworkConfiguration(network_mode=TemplateNetworkMode.PUBLIC)
    )
    """网络配置"""
    oss_configuration: Optional[List[TemplateOssConfiguration]] = None
    """OSS 配置列表"""
    log_configuration: Optional[TemplateLogConfiguration] = None
    """日志配置"""
    credential_configuration: Optional[TemplateCredentialConfiguration] = None
    """凭证配置"""
    arms_configuration: Optional[TemplateArmsConfiguration] = None
    """ARMS 监控配置"""
    container_configuration: Optional[TemplateContainerConfiguration] = None
    """容器配置"""
    disk_size: Optional[int] = None
    """磁盘大小（GB）"""

    @model_validator(mode="before")
    @classmethod
    def set_disk_size_default(cls, values):
        """根据 template_type 设置 disk_size 的默认值"""
        # 如果 disk_size 已经被显式设置，则不修改
        if (
            values.get("disk_size") is not None
            or values.get("diskSize") is not None
        ):
            return values

        # 获取 template_type（支持两种命名格式）
        template_type = values.get("template_type") or values.get(
            "templateType"
        )

        # 根据 template_type 设置默认值
        if (
            template_type == TemplateType.CODE_INTERPRETER
            or template_type == "CodeInterpreter"
        ):
            values["disk_size"] = 512
        elif (
            template_type == TemplateType.BROWSER or template_type == "Browser"
        ):
            values["disk_size"] = 10240
        else:
            # 如果 template_type 未设置或为其他值，使用 512 作为默认值
            values["disk_size"] = 512

        return values


class SandboxInput(BaseModel):
    """Sandbox 创建配置"""

    template_name: str
    """模板名称"""
    sandbox_idle_timeout_seconds: Optional[int] = 600
    """沙箱空闲超时时间（秒）"""


class PageableInput(BaseModel):
    """分页查询参数"""

    page_number: Optional[int] = 1
    """页码"""
    page_size: Optional[int] = 10
    """每页大小"""
