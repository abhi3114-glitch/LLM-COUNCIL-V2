import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")

if api_key:
    genai.configure(api_key=api_key)
    
    try:
        print("Listing available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
                
        print("\nTesting generation with gemini-2.0-flash-exp...")
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("Hello, are you working?")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")
