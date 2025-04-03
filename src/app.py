import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(1, str(BASE_DIR / "src"))

from langchain.schema import (
    AIMessage,
    HumanMessage,
)
from conf import settings
from chat import create_chat_chain
from components.record_managers.handlers import RecordManagerHandler
from components.retrievers.ensemble_retrievers import get_ensemble_retriever
from components.models.openai import get_openai_model
from utils.loggers import log_chat_interaction


load_dotenv()


st.title(f"Chat with {settings.WEBSITE_NAME.capitalize()}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hello! I'm {settings.WEBSITE_NAME.capitalize()} Bot, and I'm here to help you. How can I assist you today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("e.g. what are your services?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # Create answer chain
        model = get_openai_model()
        rm_handler = RecordManagerHandler()
        retriever = get_ensemble_retriever(
            model=model,
            rm_handler=rm_handler
        )

        use_chat_history = len(st.session_state.messages) > 1

        chat_history = []
        if use_chat_history:
            for message in st.session_state.messages[:-1]:
                if message["role"] == "user":
                    chat_history.append(HumanMessage(content=message["content"]))
                elif message["role"] == "assistant":
                    chat_history.append(AIMessage(content=message["content"]))

        answer_chain = create_chat_chain(
            model=model,
            retriever=retriever,
            use_chat_history=use_chat_history,
            k=6,
        )

        message_placeholder = st.empty()
        full_response = ""
        for token in answer_chain.stream(
            {
                "question": prompt,
                "chat_history": chat_history,
            }
        ):
            full_response += token.content
            message_placeholder.markdown(full_response + "â–Œ")

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Logging
    log_chat_interaction(
        question=prompt,
        answer=full_response,
        message="From ale"
    )
