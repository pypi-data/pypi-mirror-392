import os
from typing import Dict, Optional

from dotenv import load_dotenv

load_dotenv()


def get_env_with_default(default: str, *key: str) -> str:
    for k in key:
        v = os.getenv(k)
        if v is not None:
            return v
    return default


class Config:
    """AgentRun SDK 全局配置类

    用于管理账号凭证和客户端配置

    Examples:
        >>> config = Config(
        ...     account_id="your-account-id",
        ...     access_key_id="your-key-id",
        ...     access_key_secret="your-secret"
        ... )
        >>> # 或从环境变量读取
        >>> config = Config()
    """

    __slots__ = (
        "_access_key_id",
        "_access_key_secret",
        "_security_token",
        "_account_id",
        "_token",
        "_region_id",
        "_timeout",
        "_read_timeout",
        "_control_endpoint",
        "_data_endpoint",
        "_devs_endpoint",
        "_headers",
        "__weakref__",
    )

    def __init__(
        self,
        access_key_id: Optional[str] = None,
        access_key_secret: Optional[str] = None,
        security_token: Optional[str] = None,
        account_id: Optional[str] = None,
        token: Optional[str] = None,
        region_id: Optional[str] = None,
        timeout: Optional[int] = 600,
        read_timeout: Optional[int] = 100000,
        control_endpoint: Optional[str] = None,
        data_endpoint: Optional[str] = None,
        devs_endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """初始化配置

        Args:
            access_key_id: Access Key ID,未提供时从 AGENTRUN_ACCESS_KEY_ID 或 ALIBABA_CLOUD_ACCESS_KEY_ID 环境变量读取
            access_key_secret: Access Key Secret,未提供时从 AGENTRUN_ACCESS_KEY_SECRET 或 ALIBABA_CLOUD_ACCESS_KEY_SECRET 环境变量读取
            security_token: 安全令牌,未提供时从 AGENTRUN_SECURITY_TOKEN 或 ALIBABA_CLOUD_SECURITY_TOKEN 环境变量读取
            account_id: 账号 ID,未提供时从 AGENTRUN_ACCOUNT_ID 或 ALIBABA_CLOUD_ACCOUNT_ID 环境变量读取
            token: 自定义令牌,用于数据链路调用
            region_id: 区域 ID,默认为 cn-hangzhou
            timeout: 请求超时时间,单位秒
            control_endpoint: 自定义控制链路端点,可选
            data_endpoint: 自定义数据链路端点,可选
            headers: 自定义请求头,可选
        """

        if access_key_id is None:
            access_key_id = get_env_with_default(
                "", "AGENTRUN_ACCESS_KEY_ID", "ALIBABA_CLOUD_ACCESS_KEY_ID"
            )
        if access_key_secret is None:
            access_key_secret = get_env_with_default(
                "",
                "AGENTRUN_ACCESS_KEY_SECRET",
                "ALIBABA_CLOUD_ACCESS_KEY_SECRET",
            )
        if security_token is None:
            security_token = get_env_with_default(
                "", "AGENTRUN_SECURITY_TOKEN", "ALIBABA_CLOUD_SECURITY_TOKEN"
            )
        if account_id is None:
            account_id = get_env_with_default(
                "", "AGENTRUN_ACCOUNT_ID", "FC_ACCOUNT_ID"
            )
        if region_id is None:
            region_id = get_env_with_default("", "AGENTRUN_REGION", "FC_REGION")
        if control_endpoint is None:
            control_endpoint = get_env_with_default(
                "", "AGENTRUN_CONTROL_ENDPOINT"
            )
        if data_endpoint is None:
            data_endpoint = get_env_with_default("", "AGENTRUN_DATA_ENDPOINT")
        if devs_endpoint is None:
            devs_endpoint = get_env_with_default("", "DEVS_ENDPOINT")

        self._access_key_id = access_key_id
        self._access_key_secret = access_key_secret
        self._security_token = security_token
        self._account_id = account_id
        self._token = token
        self._region_id = region_id
        self._timeout = timeout
        self._read_timeout = read_timeout
        self._control_endpoint = control_endpoint
        self._data_endpoint = data_endpoint
        self._devs_endpoint = devs_endpoint
        self._headers = headers or {}

    @classmethod
    def with_configs(cls, *configs: Optional["Config"]) -> "Config":
        return cls().update(*configs)

    def update(self, *configs: Optional["Config"]) -> "Config":
        """
        使用给定的配置对象,返回新的实例,优先使用靠后的值

        Args:
            configs: 要合并的配置对象

        Returns:
            合并后的新配置对象
        """

        for config in configs:
            if config is None:
                continue

            for attr in filter(
                lambda x: x != "__weakref__",
                self.__slots__,
            ):
                value = getattr(config, attr)
                if value is not None:
                    if type(value) is dict:
                        getattr(self, attr).update(getattr(config, attr) or {})
                    else:
                        setattr(self, attr, value)

        return self

    def __repr__(self) -> str:

        return "Config{%s}" % (
            ", ".join([
                f'"{key}": "{getattr(self, key)}"'
                for key in self.__slots__
                if key != "__weakref__"
            ])
        )

    def get_access_key_id(self) -> str:
        """获取 Access Key ID"""
        return self._access_key_id

    def get_access_key_secret(self) -> str:
        """获取 Access Key Secret"""
        return self._access_key_secret

    def get_security_token(self) -> str:
        """获取安全令牌"""
        return self._security_token

    def get_account_id(self) -> str:
        """获取账号 ID"""
        if not self._account_id:
            raise ValueError(
                "account id is not set, please add AGENTRUN_ACCOUNT_ID env"
                " variable or set it in code."
            )

        return self._account_id

    def get_token(self) -> Optional[str]:
        """获取自定义令牌"""
        return self._token

    def get_region_id(self) -> str:
        """获取区域 ID"""
        if self._region_id:
            return self._region_id

        return "cn-hangzhou"

    def get_timeout(self) -> Optional[int]:
        """获取请求超时时间"""
        return self._timeout or 600

    def get_read_timeout(self) -> Optional[int]:
        """获取请求超时时间"""
        return self._read_timeout or 100000

    def get_control_endpoint(self) -> str:
        """获取控制链路端点"""
        if self._control_endpoint:
            return self._control_endpoint

        return f"https://agentrun.{self.get_region_id()}.aliyuncs.com"

    def get_data_endpoint(self) -> str:
        """获取数据链路端点"""
        if self._data_endpoint:
            return self._data_endpoint

        return f"https://{self.get_account_id()}.agentrun-data.{self.get_region_id()}.aliyuncs.com"

    def get_devs_endpoint(self) -> str:
        """获取 Devs 端点"""
        if self._devs_endpoint:
            return self._devs_endpoint

        return f"https://devs.{self.get_region_id()}.aliyuncs.com"

    def get_headers(self) -> Dict[str, str]:
        """获取自定义请求头"""
        return self._headers or {}
