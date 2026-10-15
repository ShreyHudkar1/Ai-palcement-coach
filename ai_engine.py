from dotenv import load_dotenv
import os
import streamlit as st
load_dotenv()
from google import genai


def get_api_key():
    # First, check environment variables.
    api_key = os.environ.get("GEMINI_API_KEY")

    # Then check Streamlit secrets.
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        raise RuntimeError(
            "Gemini API key is missing. "
            "Please configure GEMINI_API_KEY securely."
        )

    return api_key


def ask_gemini(prompt):
    client = genai.Client(api_key=get_api_key())

    # Use a model currently available to your API key.
    model_name = "gemini-3.5-flash-lite"

    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    return response.text or "The AI returned an empty response."

