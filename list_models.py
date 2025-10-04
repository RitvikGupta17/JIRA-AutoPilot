import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the .env file to get the API key
load_dotenv()

# Configure the API key
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in your .env file.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error configuring API key: {e}")
    exit()

print("\n--- 🤖 Available Gemini Models ---")
print("Listing models that support the 'generateContent' method...\n")

try:
    # List all available models and filter them
    for m in genai.list_models():
      # Check if the 'generateContent' method is supported by the model
      if 'generateContent' in m.supported_generation_methods:
        print(f"Model name: {m.name}")

except Exception as e:
    print(f"An error occurred while listing models: {e}")

print("\n------------------------------------")
print("You can use any of these model names in your llm_service.py file.")