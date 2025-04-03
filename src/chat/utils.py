from typing import List

from langchain_community.document_transformers import LongContextReorder
from langchain.schema import Document


def get_k_or_less_documents(
    docs: List[Document], 
    k: int
) -> List[Document]:
    return docs if len(docs) <= k else docs[:k]


def reorder_documents(
        docs: List[Document]
) -> List[Document]:
    reorder = LongContextReorder()

    for i, doc in enumerate(docs):
        doc.metadata["original_index"] = i

    return reorder.transform_documents(docs)


def format_docs(docs: List[Document]) -> str:
    formatted_docs: List[str] = []
    for i, doc in enumerate(docs):
        doc_string = f"<doc id='{doc.metadata.get('original_index', i)}'>{doc.page_content}</doc>"
        formatted_docs.append(doc_string)
    return "\n".join(formatted_docs)
