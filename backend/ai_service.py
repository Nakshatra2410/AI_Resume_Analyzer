import os

from dotenv import load_dotenv
from openai import OpenAI

# Load env variables from .env
load_dotenv()

# Read API configuration
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")

client = None

if API_KEY:
    client = OpenAI(api_key=API_KEY)

def generate_ai_suggestions(
    resume_text: str,
    job_description: str,
    rule_based_suggestions: list[str]
) -> list[str]:

    if not client:
        return rule_based_suggestions

    return rule_based_suggestions