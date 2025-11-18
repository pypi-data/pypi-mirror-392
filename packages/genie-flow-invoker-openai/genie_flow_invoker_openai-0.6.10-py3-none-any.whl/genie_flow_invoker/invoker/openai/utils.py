from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionUserMessageParam, ChatCompletionMessageParam

_CHAT_COMPLETION_MAP = {
    "system": ChatCompletionSystemMessageParam,
    "assistant": ChatCompletionAssistantMessageParam,
    "user": ChatCompletionUserMessageParam,
}


def chat_completion_message(dialogue_element: dict[str, str]) -> ChatCompletionMessageParam:
    try:
        role = dialogue_element["role"]
    except KeyError:
        raise KeyError("not provided a role")

    try:
        chat_cls = _CHAT_COMPLETION_MAP[role]
    except KeyError:
        raise KeyError(f"unknown chat role '{role}'")

    try:
        content = dialogue_element["content"]
    except KeyError:
        raise KeyError("not provided content")

    return chat_cls(role=role, content=content)
