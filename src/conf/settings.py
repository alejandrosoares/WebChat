import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = f"{BASE_DIR}/logs"


WEBSITE_NAME = os.getenv("WEBSITE_NAME", "")
WEBSITE_URL = os.getenv("WEBSITE_URL", "")
WEBSITE_DESCRIPTION = os.getenv("WEBSITE_DESCRIPTION", "")


if not WEBSITE_NAME:
    raise Exception("Environment variable 'WEBSITE_NAME' is not set or is empty.")
if not WEBSITE_URL:
    raise Exception("Environment variable 'WEBSITE_URL' is not set or is empty.")
if not WEBSITE_DESCRIPTION:
    raise Exception("Environment variable 'WEBSITE_DESCRIPTION' is not set or is empty.")


# DB
DB_COLLECTION_NAME = f"{WEBSITE_NAME}_app"
DB_DIR_NAME = "datastore"
DB_COLLECTION_DIR = f"{BASE_DIR}/{DB_DIR_NAME}/chroma/{DB_COLLECTION_NAME}/"


# LLM
LLM_MODEL = "gpt-3.5-turbo-16k"
LLM_TEMPERATURE = 0.0


# RECORD MANAGER
DEFAULT_RM_BATCH_SIZE = 1000


# EMSENBLE RETRIEVER
DEFAULT_SEMATIC_SEARCH_TYPE = "mmr"
DEFAULT_FETCH_K = 12
DEFAULT_K = 6
DEFAULT_LAMBDA_MULT = 0.3
DEFAULT_KEYWORD_WEIGHT = 0.3
DEFAULT_SEMANTIC_WEIGHT = 0.7
DEFAULT_C = 0.0


# LOADERS
DEFAULT_THREADS = 10
DEFAULT_LIMIT = 0


# CLEANERS
DEFAULT_CLEANER_BATCH_SIZE = 5