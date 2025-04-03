from typing import Optional

from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings

from conf import settings


def get_chroma_vectorstore(
    embeddings: Optional[Embeddings] = None
) -> Chroma:
    """
    Creates a Chroma vector store using the specified
    embeddings and configuration settings.
    Args:
        embeddings (Optional[Embeddings]): An optional embedding function
            to be used for vectorizing data.
    Returns:
        Chroma: An instance of the Chroma vector store.
    """

    vectorstore = Chroma(
        collection_name=settings.DB_COLLECTION_NAME,
        persist_directory=settings.DB_COLLECTION_DIR,
        embedding_function=embeddings,
    )
    return vectorstore