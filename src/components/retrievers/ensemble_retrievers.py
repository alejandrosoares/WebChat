from langchain_core.language_models.chat_models import BaseChatModel
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.retrievers import BM25Retriever

from conf import settings
from components.record_managers.handlers import BaseRecordManagerHandler


def get_ensemble_retriever(
    model: BaseChatModel,
    rm_handler: BaseRecordManagerHandler,
    k: int = settings.DEFAULT_K,
    fetch_k: int = settings.DEFAULT_FETCH_K,
    lambda_mult: float = settings.DEFAULT_LAMBDA_MULT,
    keyword_weight: float = settings.DEFAULT_KEYWORD_WEIGHT,
    semantic_weight: float = settings.DEFAULT_SEMANTIC_WEIGHT,
    c: float = settings.DEFAULT_C,
) -> EnsembleRetriever:
    """
    Constructs an EnsembleRetriever that combines semantic and keyword-based retrieval.
    Args:
        llm (BaseChatModel): The language model used for multi-query retrieval.
        rm_handler (BaseRecordManagerHandler): The record manager handler providing access to documents and vectorstore.
        k (int, optional): The number of top results to retrieve. Defaults to settings.DEFAULT_K.
        fetch_k (int, optional): The number of documents to fetch for semantic retrieval. Defaults to settings.DEFAULT_FETCH_K.
        lambda_mult (float, optional): The lambda multiplier for the semantic retriever's MMR search. Defaults to settings.DEFAULT_LAMBDA_MULT.
        keyword_weight (float, optional): The weight assigned to the keyword-based retriever in the ensemble. Defaults to settings.DEFAULT_KEYWORD_WEIGHT.
        semantic_weight (float, optional): The weight assigned to the semantic retriever in the ensemble. Defaults to settings.DEFAULT_SEMANTIC_WEIGHT.
        c (float, optional): The normalization constant for the ensemble retriever. Defaults to settings.DEFAULT_C.
    Returns:
        EnsembleRetriever: An ensemble retriever combining keyword-based and semantic retrieval strategies.
    """

    vectorstore = rm_handler.vectorstore
    docs = rm_handler.get_docs_from_record_manager()

    keyword_retriever = BM25Retriever.from_documents(docs)
    keyword_retriever.k = k

    semantic_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": fetch_k,
            "lambda_mult": lambda_mult,
        },
    )

    multi_query_retriever = MultiQueryRetriever.from_llm(
        retriever=semantic_retriever,
        llm=model,
    )

    retriever = EnsembleRetriever(
        retrievers=[keyword_retriever, multi_query_retriever],
        weights=[keyword_weight, semantic_weight],
        c=c,
    )

    return retriever
