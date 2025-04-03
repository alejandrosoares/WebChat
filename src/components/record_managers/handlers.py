from abc import ABC, abstractmethod
from typing import List, Iterable

from langchain_core.vectorstores import VectorStore
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.indexes import SQLRecordManager, index
from langchain.schema import Document

from conf import settings
from components.vectorstores.chroma import get_chroma_vectorstore


class BaseRecordManagerHandler(ABC):

    """Abstract base class for record manager handlers."""

    @abstractmethod
    def initialize_record_manager(self, docs: List[Document]) -> None:
        """Initialize the record manager."""
        pass

    @abstractmethod
    def get_docs_from_record_manager(self) -> List[Document]:
        """Get the documents."""
        pass


class RecordManagerHandler(BaseRecordManagerHandler):

    def __init__(
        self, 
        vectorstore: VectorStore = None, 
        batch_size: int = settings.DEFAULT_RM_BATCH_SIZE
    ) -> None:
        self.vectorstore = self._get_or_create_vectorstore(vectorstore)
        self.record_manager = self._create_record_manager()
        self._batch_size = batch_size

    def initialize_record_manager(self, docs: List[Document]) -> None:
        """Initialize the record manager by creating the schema and indexing the documents."""
        self.record_manager.create_schema()
        self._index_docs(docs=docs)

    def get_docs_from_record_manager(self) -> Iterable[Document]:
        """Get the documents."""
        vector_keys = self.vectorstore.get(
            ids=self.record_manager.list_keys(), include=["documents", "metadatas"]
        )
        docs = (
            Document(page_content=page_content, metadata=metadata)
            for page_content, metadata in zip(
                vector_keys["documents"], vector_keys["metadatas"]
            )
        )

        return docs
    
    def _index_docs(self, docs) -> None:
        index(
            docs_source=docs,
            record_manager=self.record_manager,
            vector_store=self.vectorstore,
            cleanup="full",
            batch_size=self._batch_size,
        )
    
    def _get_or_create_vectorstore(self, vectorstore: VectorStore) -> VectorStore:
        return vectorstore if vectorstore else get_chroma_vectorstore(
            embeddings=OpenAIEmbeddings()
        )
    
    def _create_record_manager(self) -> SQLRecordManager:
        db_url = f"sqlite:///{settings.DB_DIR_NAME}/{settings.DB_COLLECTION_NAME}.db"
        namespace = f"{self._get_namespace_folder()}/{settings.DB_COLLECTION_NAME}"
        return SQLRecordManager(
            db_url=db_url,
            namespace=namespace,
        )

    def _get_namespace_folder(self) -> str:
        namespace_folder = self.vectorstore.__class__.__name__.lower()
        return namespace_folder

