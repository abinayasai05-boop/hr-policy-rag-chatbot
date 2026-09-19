import pandas as pd
from sentence_transformers import SentenceTransformer

from app.database import get_connection


print("Loading BGE-M3 embedding model...")

model = SentenceTransformer("BAAI/bge-m3")

print("BGE-M3 loaded successfully!")


# Load HR policy dataset
df = pd.read_csv("data/hr_policies.csv")

print("\nHR Policy Dataset Loaded Successfully!")
print(f"Number of policies: {len(df)}")


# Connect to PostgreSQL
conn = get_connection()
cursor = conn.cursor()


# Insert policies into PostgreSQL
for _, row in df.iterrows():

    text = f"{row['title']}: {row['content']}"

    print(f"Creating embedding for {row['policy_id']} - {row['title']}")

    embedding = model.encode(
        text,
        normalize_embeddings=True
    ).tolist()

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


conn.commit()

cursor.close()
conn.close()


print("\nAll HR policies inserted successfully!")
print("Embeddings stored in PostgreSQL + pgvector.")