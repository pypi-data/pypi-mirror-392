from email import header
import resource
from typing import Optional, Union

from litellm import completion, ResponseInputParam, responses
from litellm.types.utils import LlmProviders

from agentrun.utils.config import Config
from agentrun.utils.data_api import DataAPI, ResourceType
from agentrun.utils.log import logger


class ModelCompletionAPI:

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        provider: LlmProviders = LlmProviders.OPENAI,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.provider = provider

    def completions(
        self,
        messages: list = [],
        model: Optional[str] = None,
        custom_llm_provider: Optional[LlmProviders] = None,
        **kwargs,
    ):
        logger.debug(
            "ModelCompletionAPI completions called %s, messages: %s",
            self.base_url,
            messages,
        )
        return completion(
            **kwargs,
            api_key=self.api_key,
            base_url=self.base_url,
            model=model or self.model,
            custom_llm_provider=custom_llm_provider or self.provider,
            messages=messages,
        )

    def responses(
        self,
        input: Union[str, ResponseInputParam],
        model: Optional[str] = None,
        custom_llm_provider: Optional[LlmProviders] = None,
        **kwargs,
    ):
        logger.debug(
            "ModelCompletionAPI responses called %s, input: %s",
            self.base_url,
            input,
        )
        return responses(
            **kwargs,
            api_key=self.api_key,
            base_url=self.base_url,
            model=model or self.model,
            custom_llm_provider=custom_llm_provider or self.provider,
            input=input,
        )


class ModelDataAPI(DataAPI):

    def __init__(
        self, model_name: str, config: Optional[Config] = None
    ) -> None:
        super().__init__(
            resource_name=model_name,
            resource_type=ResourceType.LiteLLM,
            config=config,
        )
        self.update_model_name(model_name=model_name, config=config)

    def update_model_name(
        self, model_name: str, config: Optional[Config] = None
    ):
        self.model_name = model_name
        self.namespace = f"models/{self.model_name}"
        self.access_token = None

        self.client = ModelCompletionAPI(
            api_key="",
            base_url=self.with_path("/v1").rstrip("/"),
            model=self.model_name,
        )
        self.config.update(config)

    def completions(
        self,
        messages: list = [],
        model: Optional[str] = None,
        config: Optional[Config] = None,
        **kwargs,
    ):
        cfg = Config.with_configs(self.config, config)
        _, headers, _ = self.auth(headers=self.config.get_headers(), config=cfg)
        return self.client.completions(
            **kwargs,
            custom_llm_provider=LlmProviders.OPENAI,
            messages=messages,
            model=model,
            headers=headers,
        )

    def responses(
        self,
        input: Union[str, ResponseInputParam],
        model: Optional[str] = None,
        config: Optional[Config] = None,
        **kwargs,
    ):
        cfg = Config.with_configs(self.config, config)
        _, headers, _ = self.auth(headers=self.config.get_headers(), config=cfg)
        return self.client.responses(
            **kwargs,
            custom_llm_provider=LlmProviders.OPENAI,
            model=model,
            input=input,
            headers=headers,
        )
