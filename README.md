# 🤖 HR Policy RAG Chatbot

A Retrieval-Augmented Generation (RAG) based **HR Policy Information Assistant** that answers employee questions using a private HR policy knowledge base.

The system combines **BGE-M3 embeddings**, **PostgreSQL with pgvector**, **semantic search**, and **Google Gemini** to retrieve relevant HR policies and generate grounded answers.


## 📌 Project Overview

Employees often need quick answers to questions about company policies such as:

* Annual leave
* Sick leave
* Working hours
* Remote work
* Notice period
* Maternity leave
* Attendance
* Other HR-related policies

Instead of relying only on an LLM, this system first searches the organization's private HR policy database and then provides the retrieved information to the LLM as context.

This reduces the risk of the chatbot generating information that is not present in the organization's policies.


## 🎯 Objectives

The main objectives of this project are:

1. Build a practical Retrieval-Augmented Generation system.
2. Process and store HR policy documents.
3. Generate semantic embeddings using **BGE-M3**.
4. Store embeddings in **PostgreSQL with pgvector**.
5. Perform semantic similarity search.
6. Retrieve the most relevant HR policies for a user query.
7. Generate answers using **Google Gemini**.
8. Reduce hallucinations by grounding responses in retrieved policies.
9. Create a foundation that can later support conversational memory and voice-based assistants.


## 🧠 What is RAG?

**Retrieval-Augmented Generation (RAG)** is a technique that combines information retrieval with Large Language Models.

Instead of asking the LLM to answer a question only from its internal knowledge, the system follows this process:

```text
User Question
      ↓
Generate Query Embedding
      ↓
Semantic Search
      ↓
PostgreSQL + pgvector
      ↓
Retrieve Relevant HR Policies
      ↓
Build Context
      ↓
Gemini LLM
      ↓
Grounded Answer
```

This allows the chatbot to answer questions using the organization's private knowledge base.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      User Query     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   BGE-M3 Embedding  │
                    │       Model         │
                    └──────────┬──────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │ PostgreSQL + pgvector      │
                │                            │
                │ HR Policies + Embeddings   │
                └─────────────┬──────────────┘
                              │
                       Semantic Search
                              │
                              ▼
                ┌────────────────────────────┐
                │ Relevant Policy Chunks     │
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
                    └─────────────────────┘


## 🔄 RAG Pipeline

### 1. Document Processing

HR policies are stored in the knowledge base.

Example:

```text
Policy ID: HR001
Category: Leave
Title: Annual Leave

Employees are entitled to 20 days of annual leave per year.

The documents are processed into smaller pieces called **chunks**.

Chunking makes it easier to retrieve only the relevant part of a document.



### 2. Embedding Generation

Each policy chunk is converted into a numerical vector using the:

**BGE-M3 embedding model**

An embedding represents the semantic meaning of the text as numbers.

For example:

```text
"How many annual leave days are available?"
```

is converted into an embedding vector.

The same process is applied to the HR policy documents

### 3. Vector Database

The generated embeddings are stored in:

**PostgreSQL + pgvector**

PostgreSQL stores the structured HR policy information, while the **pgvector extension** allows PostgreSQL to store and search vector embeddings.

Example conceptual structure:

```text
HR Policy
 ├── policy_id
 ├── category
 ├── title
 ├── content
 └── embedding



### 4. Semantic Search

When the user asks a question, the question is converted into an embedding.

The system compares the query embedding with stored policy embeddings and retrieves the most semantically relevant policies.

This is different from simple keyword matching.

For example:

```text
User:
"Can I work from home?"

Retrieved Policy:
"Employees may work remotely with prior manager approval."
```

Even though the wording is different, the system can identify the semantic relationship.

### 5. Context Retrieval

The most relevant policy chunks are passed to the LLM as context.

Conceptually:

```text
Question:
Can I work from home?

Retrieved Context:
Employees may work remotely with prior manager approval.
```


### 6. LLM Response Generation

Google Gemini receives:

* User question
* Retrieved HR policy context

It then generates a natural-language response based on the retrieved information.



## 🛡️ Hallucination Handling

A major focus of this project is reducing **LLM hallucination**.

A hallucination occurs when an AI generates information that is unsupported by the available knowledge.

For example, if the HR database says:

```text
Employees are entitled to 20 days of annual leave per year.
```

The chatbot should not invent:

```text
Employees are entitled to 30 days of annual leave.

### Grounding Strategy

The chatbot follows a retrieval-first approach:

```text
User Question
      ↓
Retrieve HR Policy
      ↓
Check Relevance
      ↓
Provide Retrieved Context
      ↓
Generate Answer
```

If relevant information cannot be found in the HR knowledge base, the chatbot can avoid presenting unsupported information as company policy.

This makes the system more suitable for private organizational knowledge.


## 🧩 Technologies Used

| Technology    | Purpose                                    |
| ------------- | ------------------------------------------ |
| Python        | Core programming language                  |
| PostgreSQL    | Relational database                        |
| pgvector      | Vector storage and similarity search       |
| BGE-M3        | Text embedding model                       |
| Google Gemini | Large Language Model                       |
| NumPy         | Numerical/vector operations where required |
| Pandas        | Data processing                            |
| python-dotenv | Environment variable management            |
| Git           | Version control                            |
| GitHub        | Source code hosting                        |


## 📂 Project Structure

```text
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
├── .gitignore
├── requirements.txt
└── README.md
```

> `.env` is intentionally excluded from GitHub because it contains sensitive credentials.


## 🗄️ Database Design

The system uses **PostgreSQL** as the main database.

The `pgvector` extension enables vector operations inside PostgreSQL.

Conceptually:

```text
PostgreSQL
│
└── HR Policies
    │
    ├── Policy ID
    ├── Category
    ├── Title
    ├── Content
    └── Embedding Vector
```

This allows both structured data and vector embeddings to be managed within the same database system.


## 🔍 Example Questions

The chatbot can handle questions such as:

```text
How many days of annual leave can employees take?

What are the working hours?

Can employees work from home?

Do I need manager approval for remote work?

What is the notice period?

What is the sick leave policy?

### Example

**Question:**

```text
How many days of annual leave can employees take?
```

**Retrieved Policy:**

```text
Employees are entitled to 20 days of annual leave per year.
```

**Generated Answer:**

```text
Employees are entitled to 20 days of annual leave per year.
```

The answer is grounded in the HR policy stored in the knowledge base.


## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/abinayasai05-boop/hr-policy-rag-chatbot.git
```

```bash
cd hr-policy-rag-chatbot
```

### 2. Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```


## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_connection_string
```

Never commit the `.env` file to GitHub.

The `.gitignore` file should contain:

```text
.env
venv/
__pycache__/
*.pyc
```

## 🐘 PostgreSQL + pgvector Setup

Create a PostgreSQL database and enable the pgvector extension.

Conceptually:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The database is then used to store:

* HR policy information
* Embedding vectors
* Metadata required for retrieval
  
## ▶️ Running the Project

After configuring the environment variables and PostgreSQL database, run the appropriate application/ingestion scripts from the project root.

Example:

```powershell
python app/ingestion.py
```

Then run the chatbot:

```powershell
python app/chatbot.py
```


## 🧪 Testing

The system can be tested using questions related to the HR knowledge base.

Example:

```text
You: How many days of annual leave can employees take?
```

The system:

```text
1. Converts the question into an embedding
2. Searches PostgreSQL using vector similarity
3. Retrieves relevant HR policies
4. Sends the context to Gemini
5. Generates a grounded response
```

## 📊 Key Concepts Demonstrated

This project demonstrates practical understanding of:

* Retrieval-Augmented Generation
* Document processing
* Text chunking
* Embeddings
* BGE-M3
* Vector databases
* PostgreSQL
* pgvector
* Semantic search
* Similarity search
* LLM integration
* Context retrieval
* Prompt grounding
* Hallucination reduction
* Private knowledge bases

## 🚀 Future Enhancements

Potential improvements include:

### 💬 Conversation Memory

Store previous conversations so the chatbot can understand follow-up questions.

Example:

```text
User:
How many annual leave days do I get?

Bot:
20 days per year.

User:
Can I use them for personal reasons?
```

The chatbot can use conversation history together with retrieved HR policies.

### 🎙️ Voice-Based HR Assistant

The RAG system can later become the knowledge and memory layer for a voice chatbot.

Possible architecture:

```text
Voice Input
     ↓
Speech-to-Text
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


### 🌐 Web Interface

A web-based interface can be added using technologies such as Streamlit or Flask.

### 📄 More HR Documents

The knowledge base can be expanded with:

* Employee handbook
* Maternity leave policy
* Payroll policies
* Benefits
* Attendance rules
* Performance policies
* Travel policies
* Resignation procedures


## 🎓 Project Outcome

This project provides a practical implementation of a RAG pipeline for a private HR knowledge base.

It demonstrates how **embedding models, vector databases, semantic retrieval, and LLMs** can work together to create an AI assistant that answers questions using organization-specific information rather than relying only on the LLM's general knowledge.


## 👩‍💻 Author

**Abinaya Sai**

GitHub:
https://github.com/abinayasai05-boop


## 📜 License

This project is intended for educational and internship/project demonstration purposes.
