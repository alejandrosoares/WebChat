from typing import List
from abc import ABC, abstractmethod

from langchain.schema import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.schema.output_parser import StrOutputParser

from conf import settings


class BaseCleaner(ABC):
    """Base class for cleaning documents."""

    @abstractmethod
    def clean(self, docs: List[Document]) -> List[Document]:
        """Clean the documents."""
        pass


class LLMPageCleaner(BaseCleaner):
    """
    Class for cleaning documents using a LLM model.
    """

    def __init__(
            self, 
            prompt: str, 
            model: BaseChatModel, 
            output_parser: StrOutputParser, 
            max_concurrency: int = settings.DEFAULT_CLEANER_BATCH_SIZE
    ) -> None:
        self._prompt = prompt
        self._model = model
        self._output_parser = output_parser
        self._chain = self._prompt | self._model | self._output_parser
        self._max_concurrency = max_concurrency

    def clean(self, docs: List[Document]) -> List[Document]:
        """Clean the documents."""
        cleaned_content = self._chain.batch(
            [{"content": doc.page_content} for doc in docs],
            config={
                "max_concurrency": self._max_concurrency
            }
        )
        cleaned_docs = [
            Document(
                page_content=result,
                metadata=doc.metadata,
            )
            for result, doc in zip(cleaned_content, docs)
        ]
        return cleaned_docs