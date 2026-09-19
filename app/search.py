from sentence_transformers import SentenceTransformer
from app.database import get_connection


# ==========================================
# LOAD BGE-M3
# ==========================================

print("Loading BGE-M3 model...")

model = SentenceTransformer("BAAI/bge-m3")

print("BGE-M3 loaded successfully!")


# ==========================================
# SEARCH FUNCTION
# ==========================================

def search_policies(query, top_k=3):

    # --------------------------------------
    # Create BGE-M3 embedding for query
    # --------------------------------------

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()


    # --------------------------------------
    # Connect to PostgreSQL
    # --------------------------------------

    conn = get_connection()
    cursor = conn.cursor()


    # --------------------------------------
    # pgvector similarity search
    # --------------------------------------

    cursor.execute(
        """
        SELECT
            policy_id,
            category,
            title,
            content,
            1 - (embedding <=> %s::vector) AS similarity
        FROM hr_policies
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (
            query_embedding,
            query_embedding,
            top_k
        )
    )


    results = cursor.fetchall()


    cursor.close()
    conn.close()


    # --------------------------------------
    # Convert results into dictionaries
    # --------------------------------------

    policies = []

    for result in results:

        policy_id, category, title, content, similarity = result

        policies.append({
            "policy_id": policy_id,
            "category": category,
            "title": title,
            "content": content,
            "score": float(similarity)
        })


    return policies


# ==========================================
# TEST SEARCH
# ==========================================

if __name__ == "__main__":

    question = input(
        "\nAsk an HR policy question: "
    )


    results = search_policies(question)


    print("\n==========================================")
    print("SEARCH RESULTS")
    print("==========================================\n")


    for i, result in enumerate(results):

        print(f"Result {i + 1}")
        print("------------------------------------------")

        print("Policy ID:", result["policy_id"])
        print("Category:", result["category"])
        print("Title:", result["title"])

        print(
            "Similarity Score:",
            round(result["score"], 4)
        )

        print("Content:", result["content"])

        print()