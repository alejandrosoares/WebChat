from langchain_openai import ChatOpenAI

from conf import settings


def get_openai_model() -> ChatOpenAI:
    """
    Creates and returns an instance of the ChatOpenAI model configured with
    the specified settings.

    The model and temperature settings are retrieved from the global `settings`
    object, which should define `LLM_MODEL` and `LLM_TEMPERATURE`.

    Returns:
        ChatOpenAI: An instance of the ChatOpenAI model configured with the
        specified model and temperature settings.
    """
    model = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
    )
    return model