from flask import Flask, render_template, request, jsonify, session
from app.chatbot import generate_answer
import uuid

app = Flask(__name__)

# Secret key for Flask sessions
app.secret_key = "hr-rag-secret-key"


@app.route("/")
def home():

    # Create a unique session ID for this browser
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        question = data.get("question", "").strip()

        if not question:

            return jsonify({
                "answer": "Please enter an HR policy question."
            })

        # Get browser session ID
        session_id = session.get("session_id")

        # Generate grounded answer
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


if __name__ == "__main__":

    app.run(debug=True)