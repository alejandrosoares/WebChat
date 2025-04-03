from functools import partial
from operator import itemgetter

from langchain_core.language_models.chat_models import BaseChatModel
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema.runnable import Runnable, RunnableMap
from langchain.schema import (
    BaseRetriever,
    StrOutputParser,
)

from . import prompts
from . import utils


def create_chat_chain(
    model: BaseChatModel,
    retriever: BaseRetriever,
    use_chat_history: bool,
    k: int = 5,
) -> Runnable:
    retriever_chain = _create_retriever_chain(model, retriever, use_chat_history)

    _get_k_or_less_documents = partial(
        utils.get_k_or_less_documents,
        k=k
    )

    context = RunnableMap(
        {
            "context": (
                retriever_chain
                | _get_k_or_less_documents
                | utils.reorder_documents
                | utils.format_docs
            ),
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history"),
        }
    )

    prompt = ChatPromptTemplate.from_messages(
        messages=[
            ("system", prompts.SYSTEM_ANSWER_QUESTION_TEMPLATE),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    response_synthesizer = prompt | model
    response_chain = context | response_synthesizer

    return response_chain


def _create_retriever_chain(
    model: BaseChatModel,
    retriever: BaseRetriever,
    use_chat_history: bool,
) -> Runnable:
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(prompts.CONDENSE_QUESTION_TEMPLATE)

    if not use_chat_history:
        initial_chain = (itemgetter("question")) | retriever
        return initial_chain
    else:
        condense_question_chain = (
            {
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
            }
            | CONDENSE_QUESTION_PROMPT
            | model
            | StrOutputParser()
        )
        conversation_chain = condense_question_chain | retriever
        return conversation_chain