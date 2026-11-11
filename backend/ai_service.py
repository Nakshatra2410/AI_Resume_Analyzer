import os

from dotenv import load_dotenv
from openai import OpenAI

# Load env variables from .env
load_dotenv()

# Read API configuration
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")

if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing from .env")

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

def test_openai_connection():
    response = client.responses.create(
        model=MODEL,
        input="Reply with exactly: API connection successful.",
        max_output_tokens=20
    )

    return response.output_text