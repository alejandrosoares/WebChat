CLEAN_DOCUMENT_TEMPLATE = """
You are a text-processing assistant. 
Your task is to clean and structure the following web site content into a clear and organized format. This content is going to be stored in a vectordatabase for retrieval and used for a question-answering LLM system. 
Remove unnecessary newlines, redundant text, and formatting artifacts. Organize the content into meaningful sections with headings, and use bullet points or lists where appropriate.

{content}
"""

