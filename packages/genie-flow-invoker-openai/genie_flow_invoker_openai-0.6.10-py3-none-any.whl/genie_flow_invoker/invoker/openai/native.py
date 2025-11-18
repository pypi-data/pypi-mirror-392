from typing import Optional

from openai import OpenAI
from openai.types.chat.completion_create_params import ResponseFormat

from genie_flow_invoker.utils import get_config_value

from .base import AbstractChatInvoker, AbstractImageInvoker


def _create_client(cls, config: dict[str, str]) -> OpenAI:
    api_key = get_config_value(
        config,
        "OPENAI_API_KEY",
        "api_key",
        "API key for OpenAI",
    )
    base_url = get_config_value(
        config,
        "OPENAI_BASE_URL",
        "base_url",
        "Base URL for OpenAI",
    )
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


class OpenAIChatInvoker(AbstractChatInvoker):

    @classmethod
    def _create_client(cls, config: dict[str, str]) -> OpenAI:
        return _create_client(cls, config)

    @classmethod
    def from_config(cls, config: dict[str, str]) -> "OpenAIChatInvoker":
        return cls(
            openai_client=cls._create_client(config),
            model=get_config_value(
                config,
                "OPENAI_MODEL",
                "model",
                "Name of OpenAI model",
            ),
            backoff_max_time=get_config_value(
                config,
                "OPENAI_BACKOFF_MAX_TIME",
                "backoff_max_time",
                "Max backoff time (seconds)",
                61,
            ),
            backoff_max_tries=get_config_value(
                config,
                "OPENAI_MAX_BACKOFF_TRIES",
                "backoff_max_tries",
                "Max backoff tries",
                15,
            )
        )


class OpenAIChatJsonInvoker(OpenAIChatInvoker):
    """
    A chat completion invoker for OpenAI clients witch will return a JSON string.

    **Important:** when using JSON mode, you **must** also instruct the model to
              produce JSON yourself via a system or user message. Without this, the model may
              generate erroneous responses.
    """

    @property
    def _response_format(self) -> Optional[dict]:
        return dict(type="json_object")


class OpenAIImageInvoker(AbstractImageInvoker):

    @classmethod
    def _create_client(cls, config: dict[str, str]) -> OpenAI:
        return _create_client(cls, config)

    @classmethod
    def from_config(cls, config: dict[str, str]) -> "OpenAIImageInvoker":
        return cls(
            openai_client=cls._create_client(config),
            model=get_config_value(
                config,
                "OPENAI_MODEL_NAME",
                "model",
                "Name of the model to use",
            ),
            backoff_max_time=get_config_value(
                config,
                "OPENAI_BACKOFF_MAX_TIME",
                "backoff_max_time",
                "Max backoff time (seconds)",
                61,
            ),
            backoff_max_tries=get_config_value(
                config,
                "OPENAI_MAX_BACKOFF_TRIES",
                "backoff_max_tries",
                "Max backoff tries",
                15,
            ),
            generation_config=config.get("generation", {}),
        )
