from abc import ABC, abstractproperty, abstractmethod, abstractclassmethod
from typing import Optional, Callable

import backoff
import openai
import yaml
from loguru import logger

from openai import OpenAI, RateLimitError, InternalServerError, APIConnectionError
from openai.types.chat.completion_create_params import ResponseFormat

from genie_flow_invoker.codec import JsonInputDecoder, JsonOutputEncoder
from genie_flow_invoker.genie import GenieInvoker

from .utils import chat_completion_message


class BackoffAPICallerInvoker(GenieInvoker, ABC):

    def __init__(
            self,
            openai_client: OpenAI,
            model: str,
            backoff_max_time: int,
            backoff_max_tries: int,
    ):
        """
        :param openai_client: OpenAI client to pass invocations to
        :param model: name of the model to use
        :param backoff_max_time: maximum time in seconds to backoff every retry
        :param backoff_max_tries: maximum number of times to backoff
        """

        self.openai_client = openai_client
        self.model = model
        self.backoff_max_time = backoff_max_time
        self.backoff_max_tries = backoff_max_tries

    @classmethod
    @abstractmethod
    def _create_client(cls, config: dict[str, str]) -> OpenAI:
        raise NotImplementedError("Subclass must implement this method")

    def call_with_backoff(self, func: Callable, **kwargs):
        """
        Call a function with a backoff if a Rate limit error occurs.

        :param func: the function to call
        :param kwargs: the keyword arguments to pass to the function
        :return: the result of the function
        """
        def backoff_logger(details):
            logger.info(
                "Backing off {wait:0.1f} seconds after {tries} tries ",
                "for a {cls} invocation",
                **details,
                cls=self.__class__.__name__,
            )

        @backoff.on_exception(
            wait_gen=backoff.fibo,
            max_value=self.backoff_max_time,
            max_tries=self.backoff_max_tries,
            exception=(RateLimitError, InternalServerError, APIConnectionError),
            on_backoff=backoff_logger,
        )
        def make_call():
            return func(**kwargs)

        return make_call()


class AbstractChatInvoker(
    BackoffAPICallerInvoker,
    ABC,
):

    @property
    def _response_format(self) -> Optional[dict]:
        return None

    def invoke(self, content: str) -> str:
        """
        Invoking the chat API of OpenAI involves sending a list of chat elements. The content
        passed to this should be a YAML list. If parsing of that YAML document fails, this
        invoker creates a single chat message form the role 'user' with the content as the
        content sent.

        - role: assistant
          content: This is a single-line uttering
        - role: user
          content: >
        But multi-line is possible.
        Like this.
        These all are put into the same tag.

        Here, `role` can be either "system", "assistant" or "user".

        :param content: YAML version of a list of all chat elements that need to be taken into
        account for the chat invocation.

        :returns: the raw content of the returned response from the API
        """
        try:
            messages_raw = yaml.safe_load(content)
        except yaml.YAMLError:
            logger.debug("cannot parse the following content as YAML: '{}'", content)
            messages_raw = content

        if isinstance(messages_raw, str):
            messages_raw = [dict(role="user", content=messages_raw)]

        messages = [chat_completion_message(element) for element in messages_raw]
        logger.debug("Invoking OpenAI Chat with the following prompts: {}", messages)

        if (
            self._response_format is not None
            and self._response_format.get("type") == "json_object"
        ):
            if "json" not in content.lower():
                logger.error(
                    "sending a JSON invocation to Azure OpenAI without mentioning "
                    "the word 'json'."
                )
                raise ValueError("The JSON invoker prompt needs to contain the word 'json'")

        response = self.call_with_backoff(
            func=self.openai_client.chat.completions.create,
            model=self.model,
            messages=messages,
            response_format=self._response_format,
        )

        try:
            return response.choices[0].message.content
        except Exception as e:
            logger.exception("Failed to call OpenAI", exc_info=e)
            raise


class AbstractImageInvoker(
    BackoffAPICallerInvoker,
    JsonInputDecoder,
    JsonOutputEncoder,
    ABC,
):

    def __init__(
            self,
            openai_client: OpenAI,
            model: str,
            generation_config: dict,
            backoff_max_time: 61,
            backoff_max_tries: 15,
    ):
        """
        :param openai_client: OpenAI client to pass invocations to
        :param model: name of the model to use
        :param backoff_max_time: maximum time in seconds to backoff every retry
        :param backoff_max_tries: maximum number of times to backoff
        """
        super(BackoffAPICallerInvoker).__init__(
            openai_client,
            model,
            backoff_max_time,
            backoff_max_tries,
        )
        self.generation_config = generation_config

    def invoke(self, content: str) -> str:
        """
        Invoking the image generation API of OpenAI involved sending a prompt. The content
        passed to this should either be a text prompt or be a JSON configuration. In either
        case, the parameters used will be merged with any parameter that has been given
        in the `meta.yaml` section of `generation:`. The name of the model is given in the
        core of the parameters in `meta.yaml`.

        The parameters that are required for generation are:
        - model -- (no default) which model to use for generation
        - prompt -- (no default) the prompt to use for generation
        - size -- (default: 1024x1024) the size to use for generation
        - quality -- (default: standard) either 'standard' or 'hd'
        - n -- (default: 1) the number of images to generate

        Parameters specified in the JSON content take precedence over the ones
        specified in the `generation:` part of the `meta.yaml` file. Those in turn
        take precedence over the defaults.

        If the OpenAI generator method returns a BadRequestError, this method returns
        a dict with keys:
        - error_code - a string identifying the reason code for rejecting the request
        - reason - a human language description of why the request was rejected

        For more details on the parameters, see
        https://platform.openai.com/docs/api-reference/images/create

        :param content: either the prompt or a JSON serialization of parameters
        :return: the JSON version of the response from the API
        """
        try:
            content_params = self._decode_input(content)
        except ValueError:
            content_params = dict(prompt=content)

        # set the defaults first, then apply config and then content
        params = dict(
            model=self.model,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        params.update(self.generation_config)
        params.update(content_params)
        logger.debug("generating image with the generate parameters: {}", params)

        try:
            image_result = self.call_with_backoff(
                func=self.openai_client.images.generate,
                **params,
            )
            return self._encode_output(
                [
                    dict(
                        revised_prompt=i.revised_prompt,
                        image_url=i.url,
                    )
                    for i in image_result.data
                ]
            )
        except openai.BadRequestError as e:
            logger.info("Bad Request to OpenAI: {}", e.message)
            return self._encode_output(
                dict(
                    reason=e.body["message"],
                    error_code=e.body["code"],
                )
            )
        except Exception as e:
            logger.exception("Failed to generate the image", exc_info=e)
            raise
