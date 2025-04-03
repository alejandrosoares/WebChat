import json
import datetime

from conf import settings


LOG_FILE = f"{settings.LOG_DIR}/chat_interactions.json"


def log_chat_interaction(question: str, answer: str, **kwargs) -> None:
    """
    Logs a chat interaction by appending the question, answer, and additional metadata to a log file.
    Args:
        question (str): The question asked during the chat interaction.
        answer (str): The answer provided during the chat interaction.
        **kwargs: Additional metadata to include in the log entry (e.g., document index).
    Returns:
        None
    """

    def _get_current_logs():
        try:
            with open(LOG_FILE, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        
    timestamp = datetime.datetime.now().isoformat()
    logs = _get_current_logs()

    logs.append({"timestamp": timestamp, "question": question, "answer": answer, **kwargs})
    
    with open(LOG_FILE, "w") as file:
        json.dump(logs, file, indent=4)