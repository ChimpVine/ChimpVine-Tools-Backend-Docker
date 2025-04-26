from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate that the key is set
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in environment variables")

# Initialize the LLM model
def get_llm(tokens=4095, temp=0.5):
    return ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=temp,
        max_tokens=tokens
    )
