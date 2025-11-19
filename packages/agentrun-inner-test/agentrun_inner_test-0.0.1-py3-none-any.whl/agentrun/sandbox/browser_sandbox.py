import asyncio
import time
from typing import Optional

from agentrun.sandbox import Sandbox
from agentrun.sandbox.api.browser_data import BrowserDataAPI
from agentrun.utils.log import logger


class BrowserSandbox(Sandbox):

    _data_api: Optional["BrowserDataAPI"] = None

    def __enter__(self):
        # Poll health check
        max_retries = 60  # Maximum 60 seconds
        retry_count = 0

        logger.info("Waiting for browser to be ready...")

        while retry_count < max_retries:
            retry_count += 1

            try:
                health = self.check_health()

                if health["status"] == "ok":
                    logger.info(
                        f"✓ Browser is ready! (took {retry_count} seconds)"
                    )
                    return self

                logger.info(
                    f"[{retry_count}/{max_retries}] Health status: not ready"
                )

            except Exception as e:
                logger.error(
                    f"[{retry_count}/{max_retries}] Health check failed: {e}"
                )

            if retry_count < max_retries:
                time.sleep(1)

        raise RuntimeError(
            f"Health check timeout after {max_retries} seconds. "
            "Browser did not become ready in time."
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sandbox_id is None:
            raise ValueError("Sandbox ID is not set")
        logger.info(f"Stopping browser sandbox {self.sandbox_id}...")
        self.stop(sandbox_id=self.sandbox_id)

    async def __aenter__(self):
        # Poll health check asynchronously
        max_retries = 60  # Maximum 60 seconds
        retry_count = 0

        logger.info("Waiting for browser to be ready...")

        while retry_count < max_retries:
            retry_count += 1

            try:
                health = await self.check_health_async()

                if health["status"] == "ok":
                    logger.info(
                        f"✓ Browser is ready! (took {retry_count} seconds)"
                    )
                    return self

                logger.info(
                    f"[{retry_count}/{max_retries}] Health status:"
                    f" {health.code} - {health.message}"
                )

            except Exception as e:
                logger.error(
                    f"[{retry_count}/{max_retries}] Health check failed: {e}"
                )

            if retry_count < max_retries:
                await asyncio.sleep(1)

        raise RuntimeError(
            f"Health check timeout after {max_retries} seconds. "
            "Browser did not become ready in time."
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.sandbox_id is None:
            raise ValueError("Sandbox ID is not set")
        logger.info(f"Stopping browser sandbox {self.sandbox_id}...")
        await self.stop_async(sandbox_id=self.sandbox_id)

    @property
    def data_api(self):
        if self._data_api is None:
            if self.sandbox_id is None:
                raise ValueError("Sandbox ID is not set")

            self._data_api = BrowserDataAPI(
                sandbox_id=self.sandbox_id, config=self._config
            )

        return self._data_api

    async def check_health_async(self):
        return await self.data_api.check_health_async()

    def check_health(self):
        return self.data_api.check_health()

    def get_cdp_url(self):
        return self.data_api.get_cdp_url()

    def get_vnc_url(self):
        return self.data_api.get_vnc_url()

    def sync_playwright(self):
        return self.data_api.sync_playwright()

    def async_playwright(self):
        return self.data_api.async_playwright()
