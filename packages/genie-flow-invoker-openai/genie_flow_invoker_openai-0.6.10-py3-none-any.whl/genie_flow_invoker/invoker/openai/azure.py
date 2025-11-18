from typing import Optional, Callable

import openai
from loguru import logger
from openai import OpenAI
from openai.lib.azure import AzureOpenAI

from genie_flow_invoker.utils import get_config_value
from .base import AbstractChatInvoker, AbstractImageInvoker


def _create_client(cls, config: dict[str, str]) -> AzureOpenAI:
    api_key = get_config_value(
        config,
        "AZURE_OPENAI_API_KEY",
        "api_key",
        "API Key",
    )

    api_version = get_config_value(
        config,
        "AZURE_OPENAI_API_VERSION",
        "api_version",
        "API Version",
    )

    endpoint = get_config_value(
        config,
        "AZURE_OPENAI_ENDPOINT",
        "endpoint",
        "Endpoint",
    )
    if endpoint is None:
        raise ValueError("No endpoint provided")

    logger.debug(
        "creating an AzureOpenAI client with api_verion {} and endpoint {}",
        api_version,
        endpoint,
    )
    return openai.AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint,
    )


class AzureOpenAIChatInvoker(AbstractChatInvoker):
    """
    A Chat Completion invoker for Azure OpenAI clients.
    """

    @classmethod
    def _create_client(cls, config: dict[str, str]) -> OpenAI:
        return _create_client(cls, config)

    @classmethod
    def from_config(cls, config: dict[str, str]) -> "AzureOpenAIChatInvoker":
        return cls(
            openai_client=cls._create_client(config),
            model=get_config_value(
                config,
                "AZURE_OPENAI_DEPLOYMENT_NAME",
                "deployment_name",
                "Deployment Name",
            ),
            backoff_max_time=get_config_value(
                config,
                "AZURE_OPENAI_BACKOFF_MAX_TIME",
                "backoff_max_time",
                "Max backoff time (seconds)",
                61,
            ),
            backoff_max_tries=get_config_value(
                config,
                "AZURE_OPENAI_MAX_BACKOFF_TRIES",
                "backoff_max_tries",
                "Max backoff tries",
                15,
            ),
        )


class AzureOpenAIChatJsonInvoker(AzureOpenAIChatInvoker):
    """
    A chat completion invoker for Azure OpenAI clients witch will return a JSON string.

    **Important:** when using JSON mode, you **must** also instruct the model to
              produce JSON yourself via a system or user message. Without this, the model may
              generate an unending stream of whitespace until the generation reaches the token
              limit
    """

    @property
    def _response_format(self) -> Optional[dict]:
        return {"type": "json_object"}


class AzureOpenAIImageInvoker(AbstractImageInvoker):

    @classmethod
    def _create_client(cls, config: dict[str, str]) -> OpenAI:
        return _create_client(cls, config)

    @classmethod
    def from_config(cls, config: dict[str, str]) -> "AzureOpenAIImageInvoker":
        return cls(
            openai_client=cls._create_client(config),
            model=get_config_value(
                config,
                "AZURE_OPENAI_DEPLOYMENT_NAME",
                "deployment_name",
                "Deployment Name",
            ),
            backoff_max_time=get_config_value(
                config,
                "AZURE_OPENAI_BACKOFF_MAX_TIME",
                "backoff_max_time",
                "Max backoff time (seconds)",
                61,
            ),
            backoff_max_tries=get_config_value(
                config,
                "AZURE_OPENAI_MAX_BACKOFF_TRIES",
                "backoff_max_tries",
                "Max backoff tries",
                15,
            ),
            generation_config=config.get("generation", {}),
        )
