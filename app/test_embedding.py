from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

result = client.models.embed_content(
    model="gemini-embedding-2",
    contents="Employees are entitled to 20 days of annual leave per year.",
    config=types.EmbedContentConfig(
        output_dimensionality=768
    )
)

embedding = result.embeddings[0].values

print("Embedding dimension:", len(embedding))