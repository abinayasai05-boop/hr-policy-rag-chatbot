import os
import uuid

from flask import Flask, render_template, request, jsonify, session
from app.chatbot import generate_answer


app = Flask(__name__)

# --------------------------------------------------
# Flask Secret Key
# --------------------------------------------------
# Add FLASK_SECRET_KEY to your .env file locally.
# Add the same variable in Render Environment Variables.

app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise ValueError("FLASK_SECRET_KEY is not set.")


# --------------------------------------------------
# Home Page
# --------------------------------------------------
@app.route("/")
def home():

    # Create a unique session ID for this browser
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    return render_template("index.html")


# --------------------------------------------------
# Chat API
# --------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "answer": "Invalid request."
            }), 400

        question = data.get("question", "").strip()

        if not question:
            return jsonify({
                "answer": "Please enter an HR policy question."
            }), 400

        # Get browser session ID
        session_id = session.get("session_id")

        # Generate grounded answer using RAG
        answer = generate_answer(
            question,
            session_id
        )

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print("Error:", e)

        return jsonify({
            "answer": "Sorry, something went wrong. Please try again."
        }), 500


# --------------------------------------------------
# Health Check
# --------------------------------------------------
@app.route("/health")
def health():

    return jsonify({
        "status": "healthy",
        "service": "HR Policy RAG Chatbot"
    })


# --------------------------------------------------
# Local Development
# --------------------------------------------------
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=False
    )