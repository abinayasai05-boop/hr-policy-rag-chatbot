import os
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv

from app.database import get_connection


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GEMINI EMBEDDING CLIENT
# ============================================================

print("Initializing Gemini Embedding 2...")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-2"
)

EMBEDDING_DIMENSION = int(
    os.getenv(
        "EMBEDDING_DIMENSION",
        "768"
    )
)

print("Gemini Embedding 2 initialized successfully!")
print(f"Embedding model: {EMBEDDING_MODEL}")
print(f"Embedding dimension: {EMBEDDING_DIMENSION}")


# ============================================================
# FUNCTION TO CREATE EMBEDDING
# ============================================================

def create_embedding(text):
    """
    Generate a cloud-based embedding using Gemini Embedding 2.
    """

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION
        )
    )

    return result.embeddings[0].values


# ============================================================
# LOAD HR POLICY DATASET
# ============================================================

df = pd.read_csv("data/hr_policies.csv")

print("\nHR Policy Dataset Loaded Successfully!")
print(f"Number of policies: {len(df)}")


# ============================================================
# CONNECT TO POSTGRESQL
# ============================================================

conn = get_connection()
cursor = conn.cursor()


# ============================================================
# INSERT POLICIES INTO POSTGRESQL
# ============================================================

for _, row in df.iterrows():

    # Create text that represents the HR policy
    text = (
        f"title: {row['title']} | "
        f"text: {row['content']}"
    )

    print(
        f"Creating Gemini embedding for "
        f"{row['policy_id']} - {row['title']}"
    )

    # Generate cloud embedding
    embedding = create_embedding(text)

    print(
        f"Embedding dimension: {len(embedding)}"
    )

    # Insert into PostgreSQL + pgvector
    cursor.execute(
        """
        INSERT INTO hr_policies
        (policy_id, category, title, content, embedding)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            row["policy_id"],
            row["category"],
            row["title"],
            row["content"],
            embedding
        )
    )


# ============================================================
# COMMIT CHANGES
# ============================================================

conn.commit()

cursor.close()
conn.close()


print("\nAll HR policies inserted successfully!")
print("Gemini embeddings stored in PostgreSQL + pgvector.")
print(f"Embedding dimension: {EMBEDDING_DIMENSION}")