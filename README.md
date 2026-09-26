
🤖 HR Policy RAG Chatbot
A Retrieval-Augmented Generation (RAG) based HR Policy Information Assistant that answers employee questions using a private HR policy knowledge base.

The system combines Gemini Embedding 2, PostgreSQL with pgvector, semantic search, Google Gemini, and conversation memory to provide grounded answers to HR policy questions.

📌 Project Overview
Employees often need quick answers about company policies such as:

Annual leave

Sick leave

Working hours

Work from home

Remote work eligibility

Notice period

Maternity and paternity leave

Attendance

Salary and salary slips

Overtime

Performance reviews

Employee training

Code of conduct

Confidentiality

Instead of relying only on an LLM, the chatbot first searches the organization's private HR policy database and then provides the retrieved information to Gemini as context.

The application also maintains conversation memory so that follow-up questions such as:

"Who needs to approve it?"

can be understood using the context of an earlier question such as:

"Can employees work from home?"

This retrieval-first approach helps reduce unsupported answers and keeps responses grounded in the organization's HR policies.

🎯 Objectives
The main objectives of this project are:

Build a practical Retrieval-Augmented Generation system.

Process and store HR policy information.

Generate semantic embeddings using Gemini Embedding 2.

Store embeddings in PostgreSQL with pgvector.

Perform vector similarity search.

Retrieve the most relevant HR policies for a user query.

Generate grounded answers using Google Gemini.

Reduce hallucinations using relevance thresholds and retrieved policy context.

Store conversation history in PostgreSQL.

Support contextual follow-up questions.

Provide the RAG system through a Flask web interface.

Deploy the application as a cloud-based web service.

🧠 What is RAG?
Retrieval-Augmented Generation (RAG) combines information retrieval with Large Language Models.

Instead of asking the LLM to answer only from its internal knowledge, the system follows this process:

User Question
      ↓
Check Conversation Context
      ↓
Rewrite Follow-up Question
      ↓
Generate Query Embedding
      ↓
Semantic Search
      ↓
PostgreSQL + pgvector
      ↓
Retrieve Relevant HR Policies
      ↓
Check Relevance
      ↓
Build Policy Context
      ↓
Google Gemini
      ↓
Grounded Answer
      ↓
Save Conversation Memory
This allows the chatbot to answer using the organization's private HR knowledge base while also supporting conversational follow-up questions.

🏗️ System Architecture
                    ┌─────────────────────┐
                    │      User Query     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Conversation Memory │
                    │     PostgreSQL      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Query Understanding │
                    │   / Query Rewrite   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Gemini Embedding 2  │
                    │    768 dimensions   │
                    └──────────┬──────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │ PostgreSQL + pgvector      │
                │                            │
                │ HR Policies + Embeddings   │
                └─────────────┬──────────────┘
                              │
                         Vector Search
                              │
                              ▼
                ┌────────────────────────────┐
                │ Relevant HR Policies       │
                └─────────────┬──────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ Context + User Question    │
                └─────────────┬──────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │    Google Gemini    │
                    │        LLM          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Grounded Response  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Save Conversation   │
                    │      Memory         │
                    └─────────────────────┘
🔄 RAG Pipeline
1. HR Policy Data
HR policies are stored in the knowledge base.

Example:

Policy ID: HR001
Category: Leave
Title: Annual Leave

Employees are entitled to 20 days of annual leave per year.
The current knowledge base contains 25 HR policies covering leave, working hours, remote work, resignation, salary, overtime, performance, training, conduct, and confidentiality.

2. Embedding Generation
Each HR policy is converted into a numerical vector using:

Gemini Embedding 2

The application uses an embedding dimensionality of:

768
A user question is also converted into an embedding using the same embedding model.

For example:

"How many annual leave days are available?"
is converted into a semantic embedding vector.

3. Vector Database
The generated embeddings are stored in:

PostgreSQL + pgvector

PostgreSQL stores the structured HR policy information, while the pgvector extension stores and searches vector embeddings.

Conceptual structure:

HR Policy
 ├── policy_id
 ├── category
 ├── title
 ├── content
 └── embedding (VECTOR(768))
4. Semantic Search
When the user asks a question, the question is converted into an embedding.

The system compares the query embedding with stored policy embeddings using vector similarity search.

For example:

User:
"Can I work from home?"

Retrieved Policy:
"Employees may work remotely with prior manager approval."
Even though the wording is different, semantic search can identify the relationship between the question and the policy.

5. Relevance Filtering
The system retrieves the most relevant policies and checks their similarity.

The current application uses:

Top K: 3
Similarity Threshold: 0.55
If relevant HR policy information cannot be found above the configured threshold, the chatbot avoids presenting unsupported information as company policy.

Fallback response:

I couldn't find this information in the HR policies.
6. Context Retrieval
The relevant policy results are formatted into context for Gemini.

Conceptually:

Question:
Can I work from home?

Retrieved Context:
Employees may work remotely with prior manager approval.
7. LLM Response Generation
Google Gemini receives:

The user's question

Retrieved HR policy context

Relevant conversation history when available

The LLM generates a natural-language answer grounded in the retrieved HR policy information.

💬 Conversation Memory
A major enhancement in the current version is conversation memory.

Previous user questions and chatbot answers are stored in PostgreSQL.

The system uses a session ID to associate messages with the same browser conversation.

Example
User:
Can employees work from home?

Bot:
Employees may work remotely with prior manager approval.

User:
Who needs to approve it?

Bot:
The work-from-home request requires prior manager approval.
The second question contains the word "it", but the system can use the previous conversation to understand that "it" refers to working from home.

Conversation Flow
User Question
      ↓
Browser Session ID
      ↓
Retrieve Previous Conversation
      ↓
Resolve Follow-up References
      ↓
Rewrite Search Query
      ↓
Vector Search
      ↓
Retrieve HR Policy
      ↓
Generate Grounded Answer
      ↓
Save User + Assistant Messages
Conversation Memory Database
The application stores conversation data in a PostgreSQL table:

conversation_memory
 ├── id
 ├── session_id
 ├── user_message
 ├── assistant_message
 └── created_at
This provides persistent conversation history for the active chatbot session.

🛡️ Hallucination Handling
A major focus of this project is reducing LLM hallucination.

A hallucination occurs when an AI generates information that is unsupported by the available knowledge.

For example, if the HR database says:

Employees are entitled to 20 days of annual leave per year.
the chatbot should not invent:

Employees are entitled to 30 days of annual leave.
Grounding Strategy
The chatbot follows a retrieval-first approach:

User Question
      ↓
Retrieve HR Policies
      ↓
Check Similarity
      ↓
Reject Weak Matches
      ↓
Provide Retrieved Context
      ↓
Generate Answer
If the required information is not available in the HR knowledge base, the chatbot returns a controlled fallback rather than inventing a company policy.

🧩 Technologies Used
Technology	Purpose
Python	Core programming language
Flask	Web application framework
PostgreSQL	Main relational database
pgvector	Vector storage and similarity search
Gemini Embedding 2	Semantic text embeddings
Google Gemini	Large Language Model
NumPy	Numerical/vector operations where required
Pandas	HR policy data processing
python-dotenv	Environment variable management
Git	Version control
GitHub	Source code hosting
Render	Cloud deployment
📂 Project Structure
hr-policy-rag-chatbot/
│
├── app/
│   ├── __init__.py
│   ├── chatbot.py
│   ├── database.py
│   ├── ingestion.py
│   └── search.py
│
├── data/
│   └── hr_policies.csv
│
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   └── index.html
│
├── web_app.py
├── requirements.txt
├── .gitignore
└── README.md
.env is intentionally excluded from GitHub because it contains sensitive credentials.

🗄️ Database Design
The application uses PostgreSQL with pgvector.

The database supports both:

HR policy vector retrieval

Conversation memory

Conceptually:

PostgreSQL
│
├── hr_policies
│   ├── policy_id
│   ├── category
│   ├── title
│   ├── content
│   └── embedding VECTOR(768)
│
└── conversation_memory
    ├── id
    ├── session_id
    ├── user_message
    ├── assistant_message
    └── created_at
This allows structured policy data, vector embeddings, and conversational history to be managed within the same database system.

🔍 Example Questions
The chatbot can handle questions such as:

How many days of annual leave can employees take?

What are the standard working hours?

Can employees work from home?

Who needs to approve work from home?

Who is eligible for remote work?

What is the notice period?

What is the sick leave policy?

How are salaries paid?

What is the overtime policy?

How often are performance reviews conducted?
Conversational Example
User:
Can employees work from home?

Bot:
Employees may work remotely with prior manager approval.

User:
Who needs to approve it?

Bot:
Prior manager approval is required for working from home.
Hallucination Test
Questions outside the knowledge base can be used to test grounding:

What is the employee health insurance policy?

What is the annual bonus percentage?

What is the employee promotion policy?

Does the company provide transportation allowance?
For unsupported questions, the expected controlled response is:

I couldn't find this information in the HR policies.
⚙️ Installation
1. Clone the Repository
git clone https://github.com/abinayasai05-boop/hr-policy-rag-chatbot.git
cd hr-policy-rag-chatbot
2. Create a Virtual Environment
Windows:

python -m venv venv
Activate it:

.\venv\Scripts\Activate.ps1
3. Install Dependencies
pip install -r requirements.txt
🔐 Environment Variables
Create a .env file in the project root.

The application uses environment variables for API credentials, database connection, model configuration, and Flask session security.

Example:

GEMINI_API_KEY=your_gemini_api_key

GEMINI_MODEL=gemini-3.5-flash-lite

GEMINI_EMBEDDING_MODEL=gemini-embedding-2

EMBEDDING_DIMENSION=768

DB_HOST=your_postgresql_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password

FLASK_SECRET_KEY=your_flask_secret_key
Never commit .env to GitHub.

The .gitignore file should contain:

.env
venv/
__pycache__/
*.pyc
🐘 PostgreSQL + pgvector Setup
Create a PostgreSQL database and enable the pgvector extension:

CREATE EXTENSION IF NOT EXISTS vector;
The HR policy table uses a 768-dimensional vector:

embedding VECTOR(768)
The conversation memory table stores the conversation associated with each browser session:

CREATE TABLE conversation_memory (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
📥 Loading HR Policies
The HR policy data is stored in:

data/hr_policies.csv
Run ingestion from the project root:

python -m app.ingestion
The ingestion process generates embeddings and stores the policy records in PostgreSQL.

Verify the policy count:

SELECT COUNT(*) FROM hr_policies;
The current knowledge base contains:

25
HR policies.

Verify the embedding dimensions:

SELECT vector_dims(embedding), COUNT(*)
FROM hr_policies
GROUP BY vector_dims(embedding);
Expected:

768 | 25
▶️ Running the Project
CLI Chatbot
From the project root:

python -m app.chatbot
Flask Web Application
Run:

python web_app.py
The application will be available locally at:

http://127.0.0.1:5000
Health check:

http://127.0.0.1:5000/health
🌐 Web Application
The project includes a Flask-based web interface.

The web application:

Creates a browser session ID.

Receives the user's question.

Sends the question to the RAG pipeline.

Uses conversation memory for follow-up questions.

Retrieves relevant HR policies.

Generates a grounded Gemini response.

Returns the answer to the browser.

The Flask session ID is reused across /chat requests so that the same conversation can be associated with the same conversation_memory records.

🚀 Deployment
The application can be deployed as a cloud web service.

Render Configuration
Build command:

pip install -r requirements.txt
Start command:

gunicorn web_app:app
Required Render environment variables include:

GEMINI_API_KEY
GEMINI_MODEL
GEMINI_EMBEDDING_MODEL
EMBEDDING_DIMENSION
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
FLASK_SECRET_KEY
For a Render PostgreSQL database, the web service should use the database connection details provided by Render.

Deployment Architecture
User Browser
     ↓
Render Web Service
     ↓
Flask Web Application
     ↓
RAG Chatbot
     ├── Conversation Memory
     ├── Gemini Embedding 2
     ├── PostgreSQL + pgvector
     └── Google Gemini
🧪 Testing
Basic RAG Test
You:
How many days of annual leave can employees take?
The system:

1. Generates the query embedding
2. Searches PostgreSQL using vector similarity
3. Retrieves relevant HR policies
4. Checks the similarity threshold
5. Sends the retrieved context to Gemini
6. Generates a grounded response
7. Saves the conversation
Conversation Memory Test
You:
Can employees work from home?

Bot:
Employees may work remotely with prior manager approval.

You:
Who needs to approve it?
The second question should be interpreted using the previous conversation.

Hallucination Test
Ask a question that is not contained in the HR knowledge base:

What is the employee health insurance policy?
The chatbot should not invent an answer.

Expected:

I couldn't find this information in the HR policies.
📊 Key Concepts Demonstrated
This project demonstrates practical understanding of:

Retrieval-Augmented Generation

Private knowledge bases

Document processing

Embeddings

Gemini Embedding 2

768-dimensional vector embeddings

Vector databases

PostgreSQL

pgvector

Semantic search

Similarity search

Query rewriting

Conversation memory

Session management

LLM integration

Context retrieval

Prompt grounding

Hallucination reduction

Flask web applications

Cloud deployment

Environment variable management

🚀 Future Enhancements
Potential improvements include:

🎙️ Voice-Based HR Assistant
The RAG system can later become the knowledge and memory layer for a voice chatbot.

Possible architecture:

Voice Input
     ↓
Speech-to-Text
     ↓
Conversation Memory
     ↓
RAG Pipeline
     ↓
PostgreSQL + pgvector
     ↓
Gemini
     ↓
Text-to-Speech
     ↓
Voice Response
📄 More HR Documents
The knowledge base can be expanded with:

Employee handbook

Payroll policies

Benefits

Attendance rules

Performance policies

Travel policies

Resignation procedures

Additional organizational documents

🔐 Authentication
Employee authentication can be added so that access to the private HR knowledge base is restricted to authorized users.

📈 Evaluation
Future versions can include automated evaluation for:

Retrieval accuracy

Similarity scores

Answer grounding

Hallucination rate

Response latency

Follow-up question accuracy

🎓 Project Outcome
This project provides a practical implementation of a production-oriented RAG pipeline for a private HR knowledge base.

It demonstrates how:

Gemini Embedding 2 + PostgreSQL + pgvector + semantic retrieval + conversation memory + Google Gemini

can work together to create an AI assistant that answers questions using organization-specific information rather than relying only on general LLM knowledge.

The project also demonstrates deployment through a Flask web application and cloud hosting.

👩‍💻 Author
Abinaya Sai

GitHub:

https://github.com/abinayasai05-boop

📜 License
This project is intended for educational and internship/project demonstration purposes
