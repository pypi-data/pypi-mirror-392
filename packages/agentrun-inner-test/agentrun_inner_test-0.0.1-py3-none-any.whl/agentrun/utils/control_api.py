from typing import Optional

from alibabacloud_agentrun20250910.client import Client as AgentRunClient
from alibabacloud_devs20230714.client import Client as DevsClient
from alibabacloud_tea_openapi import utils_models as open_api_util_models

from agentrun.utils.config import Config


class ControlAPI:
    """
    控制链路客户端
    """

    def __init__(self, config: Optional[Config] = None):
        """
        初始化 Control API 客户端

        Args:
            config: 全局配置对象
        """
        self.config = config

    def _get_client(self, config: Optional[Config] = None) -> "AgentRunClient":
        """
        获取 Control API 客户端实例

        Returns:
            AgentRunClient: Control API 客户端实例
        """

        cfg = Config.with_configs(self.config, config)
        endpoint = cfg.get_control_endpoint()
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            endpoint = endpoint.split("://", 1)[1]
        return AgentRunClient(
            open_api_util_models.Config(
                access_key_id=cfg.get_access_key_id(),
                access_key_secret=cfg.get_access_key_secret(),
                security_token=cfg.get_security_token(),
                region_id=cfg.get_region_id(),
                endpoint=endpoint,
                connect_timeout=cfg.get_timeout(),  # type: ignore
            )
        )

    def _get_devs_client(self, config: Optional[Config] = None) -> "DevsClient":
        """
        获取 Devs API 客户端实例

        Returns:
            DevsClient: Devs API 客户端实例
        """

        cfg = Config.with_configs(self.config, config)
        endpoint = cfg.get_devs_endpoint()
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            endpoint = endpoint.split("://", 1)[1]
        return DevsClient(
            open_api_util_models.Config(
                access_key_id=cfg.get_access_key_id(),
                access_key_secret=cfg.get_access_key_secret(),
                security_token=cfg.get_security_token(),
                region_id=cfg.get_region_id(),
                endpoint=endpoint,
                connect_timeout=cfg.get_timeout(),  # type: ignore
                read_timeout=cfg.get_read_timeout(),  # type: ignore
            )
        )
