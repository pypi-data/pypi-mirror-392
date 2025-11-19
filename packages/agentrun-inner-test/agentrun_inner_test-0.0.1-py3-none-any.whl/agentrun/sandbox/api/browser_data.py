from typing import Optional
from urllib.parse import parse_qs, urlencode, urlparse

from agentrun.utils.config import Config
from agentrun.utils.data_api import DataAPI, ResourceType


class BrowserDataAPI(DataAPI):

    def __init__(
        self,
        sandbox_id: str,
        config: Optional[Config] = None,
    ):
        self.sandbox_id = sandbox_id
        namespace = f"sandboxes/{sandbox_id}"

        super().__init__(
            sandbox_id, ResourceType.Template, namespace=namespace, config=config
        )

    async def check_health_async(self):
        """
        Asynchronously check the health status of the browser instance.

        Returns:
            Response object containing the health status of the browser.

        Raises:
            Exception: If the health check request fails.
        """
        return await self.get_async("/health")

    def check_health(self):
        """
        Synchronously check the health status of the browser instance.

        Returns:
            Response object containing the health status of the browser.

        Raises:
            Exception: If the health check request fails.
        """
        return self.get("/health")

    def get_cdp_url(self):
        """
        Generate the WebSocket URL for Chrome DevTools Protocol (CDP) connection.

        This method constructs a WebSocket URL by:
        1. Converting the HTTP endpoint to WebSocket protocol (ws://)
        2. Parsing the existing URL and query parameters
        3. Adding the session ID to the query parameters
        4. Reconstructing the complete WebSocket URL

        Returns:
            str: The complete WebSocket URL for CDP automation connection,
                 including the session ID in the query parameters.

        Example:
            >>> api = BrowserDataAPI("browser123", "session456")
            >>> api.get_cdp_url()
            'ws://example.com/ws/automation?sessionId=session456'
        """
        cdp_url = self.with_path("/ws/automation").replace("http", "ws")
        u = urlparse(cdp_url)
        query_dict = parse_qs(u.query)
        query_dict["tenantId"] = [self.config.get_account_id()]
        new_query = urlencode(query_dict, doseq=True)
        new_u = u._replace(query=new_query)
        return new_u.geturl()

    def get_vnc_url(self):
        """
        Generate the WebSocket URL for VNC (Virtual Network Computing) live view connection.

        This method constructs a WebSocket URL for real-time browser viewing by:
        1. Converting the HTTP endpoint to WebSocket protocol (ws://)
        2. Parsing the existing URL and query parameters
        3. Adding the session ID to the query parameters
        4. Reconstructing the complete WebSocket URL

        Returns:
            str: The complete WebSocket URL for VNC live view connection,
                 including the session ID in the query parameters.

        Example:
            >>> api = BrowserDataAPI("browser123", "session456")
            >>> api.get_vnc_url()
            'ws://example.com/ws/liveview?sessionId=session456'
        """
        vnc_url = self.with_path("/ws/liveview").replace("http", "ws")
        u = urlparse(vnc_url)
        query_dict = parse_qs(u.query)
        query_dict["tenantId"] = [self.config.get_account_id()]
        new_query = urlencode(query_dict, doseq=True)
        new_u = u._replace(query=new_query)
        return new_u.geturl()

    def sync_playwright(
        self, browser_type: str = "chrome", config: Optional[Config] = None
    ):
        from .playwright_sync import BrowserPlaywrightSync

        cfg = Config.with_configs(self.config, config)
        _, headers, _ = self.auth(headers=cfg.get_headers(), config=cfg)
        return BrowserPlaywrightSync(
            self.get_cdp_url(),
            browser_type=browser_type,
            headers=headers,
        )

    def async_playwright(
        self, browser_type: str = "chrome", config: Optional[Config] = None
    ):
        from .playwright_async import BrowserPlaywrightAsync

        cfg = Config.with_configs(self.config, config)
        _, headers, _ = self.auth(headers=cfg.get_headers(), config=cfg)
        return BrowserPlaywrightAsync(
            self.get_cdp_url(),
            browser_type=browser_type,
            headers=headers,
        )
