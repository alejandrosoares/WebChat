import sys
from typing import List
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(1, str(BASE_DIR / "src"))

from langchain_core.language_models.chat_models import BaseChatModel
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.schema.output_parser import StrOutputParser

from conf import settings
from components.record_managers.handlers import RecordManagerHandler
from components.models.openai import get_openai_model
from loaders import SiteLoader
from cleaners import LLMPageCleaner
from prompts import CLEAN_DOCUMENT_TEMPLATE


load_dotenv()


def ingest() -> None:
    print("Starting ingestion...")
    model = get_openai_model()
    docs = retrieve_cleaned_documents(model)
    rm_handler = RecordManagerHandler()
    rm_handler.initialize_record_manager(docs=docs)


def retrieve_cleaned_documents(model: BaseChatModel) -> List[Document]:
    """Clean the documents."""

    docs = SiteLoader(site_url=settings.WEBSITE_URL).load()
    prompt = ChatPromptTemplate.from_template(CLEAN_DOCUMENT_TEMPLATE)
    cleaner = LLMPageCleaner(
        prompt=prompt,
        model=model,
        output_parser=StrOutputParser(),
    )
    cleaned_docs = cleaner.clean(docs)
    return cleaned_docs


if __name__ == "__main__":
    ingest()