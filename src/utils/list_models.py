import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Configure API
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

print("Available Gemini models:\n")
print("-" * 60)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            model_name = model.name.replace('models/', '')
            print(f"✅ {model_name}")
            print(f"   Full name: {model.name}")
            print(f"   Display: {model.display_name}")
            print()
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure GOOGLE_API_KEY is set in your .env file!")