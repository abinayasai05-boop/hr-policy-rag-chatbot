import os
import uuid
import time

from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer

from app.database import get_connection


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Please check your .env file."
    )


# ============================================================
# CONNECT TO GEMINI
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# ============================================================
# GEMINI CONFIGURATION
# ============================================================
# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

MAX_GEMINI_RETRIES = 2

# ============================================================
# RAG CONFIGURATION
# ============================================================

TOP_K = 3

# Minimum similarity required
# before using retrieved policy information.

SIMILARITY_THRESHOLD = 0.55

# Number of previous conversation turns
# used as memory.

MEMORY_LIMIT = 5


# ============================================================
# LOAD BGE-M3 EMBEDDING MODEL
# ============================================================

print("\nLoading BGE-M3 embedding model...")

embedding_model = SentenceTransformer(
    "BAAI/bge-m3"
)

print("BGE-M3 loaded successfully!")


# ============================================================
# GEMINI RESPONSE FUNCTION
# ============================================================

def generate_gemini_response(prompt):
    """
    Generate a response using Gemini.

    Temporary errors such as 503 are retried
    automatically.

    Returns:
        response text
        None if Gemini remains unavailable
    """

    for attempt in range(MAX_GEMINI_RETRIES):

        try:

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            if (
                not response
                or not response.text
                or not response.text.strip()
            ):

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text.strip()

        except Exception as e:

            error_text = str(e).upper()

            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "SERVICE UNAVAILABLE" in error_text
                or "DEADLINE EXCEEDED" in error_text
                or "TIMEOUT" in error_text
                or "RESOURCE EXHAUSTED" in error_text
            )

            # ------------------------------------------------
            # Non-temporary error
            # ------------------------------------------------

            if not is_temporary_error:

                print("\nGemini Error:")
                print(e)

                raise

            # ------------------------------------------------
            # Last retry
            # ------------------------------------------------

            if attempt == MAX_GEMINI_RETRIES - 1:

                print(
                    "\nGemini is temporarily unavailable "
                    "after multiple attempts."
                )

                return None

            # ------------------------------------------------
            # Exponential backoff
            # ------------------------------------------------

            wait_time = 2 ** attempt

            print(
                f"\nGemini temporarily unavailable "
                f"(attempt {attempt + 1}/"
                f"{MAX_GEMINI_RETRIES}). "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)

    return None


# ============================================================
# SAVE CONVERSATION TO POSTGRESQL
# ============================================================

def save_conversation(
    user_message,
    assistant_message,
    session_id
):
    """
    Save the conversation to PostgreSQL.
    """

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO conversation_memory
            (
                session_id,
                user_message,
                assistant_message
            )
            VALUES (%s, %s, %s);
            """,
            (
                session_id,
                user_message,
                assistant_message
            )
        )

        conn.commit()

        cursor.close()

    finally:

        conn.close()


# ============================================================
# GET CONVERSATION HISTORY
# ============================================================

def get_conversation_history(
    session_id,
    limit=MEMORY_LIMIT
):
    """
    Get previous conversation messages
    for the current session.
    """

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                user_message,
                assistant_message
            FROM conversation_memory
            WHERE session_id = %s
            ORDER BY created_at DESC
            LIMIT %s;
            """,
            (
                session_id,
                limit
            )
        )

        results = cursor.fetchall()

        cursor.close()

    finally:

        conn.close()

    # Newest messages are returned first.
    # Reverse them for chronological order.

    results.reverse()

    history = ""

    for user_message, assistant_message in results:

        history += f"""
User: {user_message}
Assistant: {assistant_message}
"""

    return history


# ============================================================
# CREATE SEARCH QUERY USING CONVERSATION MEMORY
# ============================================================

def create_search_query(
    question,
    session_id
):
    """
    Rewrite conversational questions into
    standalone HR policy search queries.

    Example:

    Previous:
        User: Tell me about annual leave.

    Current:
        User: What about sick leave?

    Search query:
        What is the sick leave policy?
    """

    history = get_conversation_history(
        session_id,
        limit=MEMORY_LIMIT
    )

    # --------------------------------------------------------
    # No previous conversation
    # --------------------------------------------------------

    if not history:

        return question

    # --------------------------------------------------------
    # Query rewriting prompt
    # --------------------------------------------------------

    prompt = f"""
You are a query rewriting component in an
HR policy retrieval system.

Your task is ONLY to rewrite the CURRENT USER
QUESTION into a standalone search query.

Use the previous conversation only to resolve
references such as:

- it
- they
- them
- this
- that
- this leave
- that policy
- this rule

Do NOT answer the question.

Do NOT invent information.

Do NOT add HR policy facts that are not present
in the conversation.

Return ONLY the rewritten search query.

==========================================
PREVIOUS CONVERSATION
==========================================

{history}

==========================================
CURRENT USER QUESTION
==========================================

{question}

==========================================
OUTPUT
==========================================

Return ONLY the standalone search query.
"""

    # --------------------------------------------------------
    # Ask Gemini to rewrite query
    # --------------------------------------------------------

    search_query = generate_gemini_response(
        prompt
    )

    # --------------------------------------------------------
    # Gemini unavailable
    # --------------------------------------------------------

    if not search_query:

        print(
            "\nUsing original question for "
            "semantic search."
        )

        return question

    return search_query


# ============================================================
# SEARCH HR POLICIES USING PGVECTOR
# ============================================================

def search_policies(
    query,
    top_k=TOP_K
):
    """
    Convert query to BGE-M3 embedding and
    perform cosine similarity search using
    PostgreSQL + pgvector.
    """

    # --------------------------------------------------------
    # Generate BGE-M3 embedding
    # --------------------------------------------------------

    query_embedding = embedding_model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    # --------------------------------------------------------
    # Connect to PostgreSQL
    # --------------------------------------------------------

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # ----------------------------------------------------
        # pgvector cosine distance search
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                policy_id,
                category,
                title,
                content,
                1 - (embedding <=> %s::vector)
                AS similarity
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

    finally:

        conn.close()

    # --------------------------------------------------------
    # Format retrieved policies
    # --------------------------------------------------------

    policies = []

    for result in results:

        (
            policy_id,
            category,
            title,
            content,
            similarity
        ) = result

        policies.append(
            {
                "policy_id": policy_id,
                "category": category,
                "title": title,
                "content": content,
                "score": float(similarity)
            }
        )

    return policies


# ============================================================
# CREATE POLICY CONTEXT
# ============================================================

def create_policy_context(results):
    """
    Convert retrieved policies into context
    for the Gemini RAG prompt.
    """

    context = ""

    for result in results:

        context += f"""
Policy ID: {result['policy_id']}
Category: {result['category']}
Title: {result['title']}
Content: {result['content']}

"""

    return context


# ============================================================
# GENERATE RAG ANSWER
# ============================================================

def generate_answer(
    question,
    session_id
):
    """
    Complete RAG pipeline:

    1. Conversation memory
    2. Query rewriting
    3. BGE-M3 embedding
    4. PostgreSQL + pgvector search
    5. Similarity threshold
    6. Gemini grounded answer
    7. Conversation memory
    """

    # ========================================================
    # STEP 1: CREATE SEARCH QUERY
    # ========================================================

    search_query = create_search_query(
        question,
        session_id
    )

    print(
        "\nSearch Query:",
        search_query
    )


    # ========================================================
    # STEP 2: SEARCH HR POLICIES
    # ========================================================

    results = search_policies(
        search_query,
        top_k=TOP_K
    )


    # ========================================================
    # STEP 3: CHECK RETRIEVAL RESULTS
    # ========================================================

    if not results:

        answer = (
            "I couldn't find this information "
            "in the HR policies."
        )

        save_conversation(
            question,
            answer,
            session_id
        )

        return answer


    # ========================================================
    # STEP 4: GET TOP SIMILARITY SCORE
    # ========================================================

    top_score = results[0]["score"]

    print(
        "\nTop Similarity Score:",
        round(top_score, 4)
    )


    # ========================================================
    # STEP 5: HALLUCINATION PROTECTION
    # ========================================================

    if top_score < SIMILARITY_THRESHOLD:

        answer = (
            "I couldn't find this information "
            "in the HR policies."
        )

        print(
            "\nHallucination protection:"
            " No sufficiently relevant policy found."
        )

        save_conversation(
            question,
            answer,
            session_id
        )

        return answer


    # ========================================================
    # STEP 6: CREATE POLICY CONTEXT
    # ========================================================

    context = create_policy_context(
        results
    )


    # ========================================================
    # STEP 7: GET CONVERSATION HISTORY
    # ========================================================

    history = get_conversation_history(
        session_id,
        limit=MEMORY_LIMIT
    )


    # ========================================================
    # STEP 8: CREATE GROUNDED RAG PROMPT
    # ========================================================

    prompt = f"""
You are an HR Policy Assistant.

Your job is to answer the user's question
using ONLY the HR policy information provided
in the HR POLICY INFORMATION section.

==========================================
STRICT RULES
==========================================

1. Use ONLY the provided HR policies.

2. Do NOT use outside knowledge.

3. Do NOT invent information.

4. Do NOT make assumptions.

5. Do NOT create new HR policies.

6. Do NOT use previous conversation as a source
   of HR policy facts.

7. Previous conversation may ONLY be used to
   understand references such as:
   "it", "they", "them", "this", or "that".

8. Every HR policy fact in the answer must
   come from the HR POLICY INFORMATION section.

9. Preserve policy numbers, dates, durations,
   eligibility requirements, conditions and
   quantities accurately.

10. If the answer cannot be determined from
    the provided HR policies, respond exactly:

"I couldn't find this information in the HR policies."

11. Do not mention similarity scores.

12. Do not mention the RAG system.

13. Do not mention the embedding model.

14. Do not mention PostgreSQL or pgvector.

15. Keep the answer clear and concise.

==========================================
PREVIOUS CONVERSATION
==========================================

{history}

==========================================
HR POLICY INFORMATION
==========================================

{context}

==========================================
CURRENT USER QUESTION
==========================================

{question}

==========================================
FINAL INSTRUCTION
==========================================

Answer the CURRENT USER QUESTION using ONLY
the HR POLICY INFORMATION.

If the information is not present, respond
exactly:

"I couldn't find this information in the HR policies."
"""


    # ========================================================
    # STEP 9: GENERATE FINAL ANSWER
    # ========================================================

    answer = generate_gemini_response(
        prompt
    )


    # ========================================================
    # STEP 10: GEMINI FAILURE FALLBACK
    # ========================================================

    if not answer:

        # Do NOT invent an answer.
        #
        # Instead, return the most relevant
        # retrieved policy directly.

        answer = results[0]["content"]

        print(
            "\nGemini unavailable."
        )

        print(
            "Returning retrieved policy directly."
        )


    # ========================================================
    # STEP 11: SAVE CONVERSATION
    # ========================================================

    save_conversation(
        question,
        answer,
        session_id
    )


    # ========================================================
    # STEP 12: RETURN ANSWER
    # ========================================================

    return answer


# ============================================================
# CHAT LOOP
# ============================================================

if __name__ == "__main__":

    print(
        "\n=========================================="
    )

    print(
        "          HR POLICY RAG CHATBOT"
    )

    print(
        "=========================================="
    )

    print(
        "\nEmbedding Model:"
    )

    print(
        "BAAI/bge-m3"
    )

    print(
        "\nVector Database:"
    )

    print(
        "PostgreSQL + pgvector"
    )

    print(
        "\nLLM:"
    )

    print(
        GEMINI_MODEL
    )

    print(
        "\nConversation Memory:"
    )

    print(
        "PostgreSQL"
    )

    print(
        "\nHallucination Protection:"
    )

    print(
        "Enabled"
    )

    print(
        "\nSimilarity Threshold:"
    )

    print(
        SIMILARITY_THRESHOLD
    )

    print(
        "\nType 'exit', 'quit', or 'bye' to stop."
    )


    # ========================================================
    # CREATE CHAT SESSION
    # ========================================================

    cli_session_id = str(
        uuid.uuid4()
    )

    print(
        "\nSession ID:",
        cli_session_id
    )


    # ========================================================
    # START CHAT
    # ========================================================

    while True:

        try:

            question = input(
                "\nYou: "
            ).strip()

        except KeyboardInterrupt:

            print(
                "\n\nChatbot: Goodbye!"
            )

            break

        except EOFError:

            print(
                "\n\nChatbot: Goodbye!"
            )

            break


        # ====================================================
        # EMPTY QUESTION
        # ====================================================

        if not question:

            print(
                "\nChatbot: "
                "Please enter an HR policy question."
            )

            continue


        # ====================================================
        # EXIT COMMAND
        # ====================================================

        if question.lower() in [
            "exit",
            "quit",
            "bye"
        ]:

            print(
                "\nChatbot: Goodbye!"
            )

            break


        # ====================================================
        # GENERATE ANSWER
        # ====================================================

        try:

            answer = generate_answer(
                question,
                cli_session_id
            )

            print(
                "\nChatbot:"
            )

            print(
                answer
            )

        except Exception as e:

            print(
                "\nError:"
            )

            print(
                str(e)
            )