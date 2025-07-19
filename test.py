import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# List all models
models = genai.list_models()

for model in models:
    print(f"📌 {model.name} — supports: {model.supported_generation_methods}")
