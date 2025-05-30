from google import genai
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("API_KEY not found in environment variables. Please check your .env file.")

# Initialize the client with the API key explicitly
client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)

print(response.text)
