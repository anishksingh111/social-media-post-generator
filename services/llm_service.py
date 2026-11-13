import os
import streamlit as st
from langchain_groq import ChatGroq

def get_api_key():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise ValueError("The app owner needs to configure GROQ_API_KEY in the .env file (or Streamlit Secrets before deployment).")
    return key

@st.cache_resource(show_spinner=False)
def get_chat_model(model_name: str, temperature: float = 0.7):
    return ChatGroq(
        api_key=get_api_key(),
        model=model_name,
        temperature=float(temperature),
        max_retries=2,
        timeout=90
    )
