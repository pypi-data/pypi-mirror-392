"""Template 高层 API"""

from typing import Dict, List, Optional

from alibabacloud_agentrun20250910.models import Template as TemplateModel

from agentrun.sandbox.model import (
    TemplateArmsConfiguration,
    TemplateContainerConfiguration,
    TemplateCredentialConfiguration,
    TemplateInput,
    TemplateLogConfiguration,
    TemplateMcpOptions,
    TemplateMcpState,
    TemplateNetworkConfiguration,
    TemplateOssConfiguration,
    TemplateType,
)
from agentrun.utils.config import Config
from agentrun.utils.model import BaseModel


class Template(BaseModel):
    """Template 实例

    封装了 Template 的基本信息和操作方法
    """

    template_id: Optional[str] = None
    """模板 ID"""
    template_name: Optional[str] = None
    """模板名称"""
    template_version: Optional[str] = None
    """模板版本"""
    template_arn: Optional[str] = None
    """模板 ARN"""
    resource_name: Optional[str] = None
    """资源名称"""
    template_type: Optional[TemplateType] = None
    """模板类型"""
    cpu: Optional[float] = None
    """CPU 核数"""
    memory: Optional[int] = None
    """内存大小（MB）"""
    disk_size: Optional[int] = None
    """磁盘大小（GB）"""
    execution_role_arn: Optional[str] = None
    """执行角色 ARN"""
    sandbox_idle_timeout_in_seconds: Optional[int] = None
    """沙箱空闲超时时间（秒）"""
    sandbox_ttlin_seconds: Optional[int] = None
    """沙箱存活时间（秒）"""
    share_concurrency_limit_per_sandbox: Optional[int] = None
    """每个沙箱的最大并发会话数"""
    template_configuration: Optional[Dict] = None
    """模板配置"""
    environment_variables: Optional[Dict] = None
    """环境变量"""
    network_configuration: Optional[TemplateNetworkConfiguration] = None
    """网络配置"""
    oss_configuration: Optional[List[TemplateOssConfiguration]] = None
    """OSS 配置列表"""
    log_configuration: Optional[TemplateLogConfiguration] = None
    """日志配置"""
    credential_configuration: Optional[TemplateCredentialConfiguration] = None
    """凭证配置"""
    container_configuration: Optional[TemplateContainerConfiguration] = None
    """容器配置"""
    mcp_options: Optional[TemplateMcpOptions] = None
    """MCP 选项"""
    mcp_state: Optional[TemplateMcpState] = None
    """MCP 状态"""
    created_at: Optional[str] = None
    """创建时间"""
    last_updated_at: Optional[str] = None
    """最后更新时间"""
    status: Optional[str] = None
    """状态"""
    status_reason: Optional[str] = None
    """状态原因"""

    @classmethod
    def from_inner_object(cls, obj: TemplateModel) -> "Template":
        """从 SDK Template 模型创建 Template 对象

        Args:
            obj: SDK Template 模型对象

        Returns:
            Template: Template 对象
        """
        return cls.model_validate(obj.to_map(), by_alias=True)
