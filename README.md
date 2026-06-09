# 🛒 Small Business Local AI Logistics Engine

A 100% offline, privacy-first AI command center built to automate logistics, manage inventory, and enforce vendor compliance for a local grocery concept. 

This system is explicitly engineered to run entirely on restricted hardware (**8GB RAM maximum footprint**) using a decoupled Docker architecture, local LLM inference, and an ephemeral vector memory layer—eliminating all SaaS fees and cloud privacy risks.

## ⚡ Core Architecture & Tech Stack

* **Inference Engine:** [Ollama](https://ollama.ai/) running `llama3.2:1b` (optimized for local CPU execution).
* **Database:** PostgreSQL upgraded with the `pgvector` extension for native similarity search.
* **Backend & Orchestration:** Python (psycopg2, sentence-transformers, PyTorch).
* **Environment:** Fully containerized via Docker & Docker Compose.
* **Interfaces:** 
  * Streamlit Web Dashboard for visual anomaly detection.
  * Interactive Terminal CLI for Agentic Tool Calling.

---

## 🚀 Key Engineering Milestones

### Phase 7: Local RAG & Vector Memory (Zero-Bloat Strategy)
Implemented a Retrieval-Augmented Generation (RAG) pipeline to feed local vendor contracts and shipping policies to the LLM without exceeding the 8GB hardware limit.
* **Ephemeral Compute Pattern:** Instead of running a permanent vector database, a Python script temporarily loads PyTorch to generate 384-dimensional embeddings from text chunking, writes them to PostgreSQL, and immediately terminates its own process to release ~750MB of RAM back to the OS.
* **Hallucination-Free Drafting:** The Streamlit dashboard automatically pulls context from `pgvector` via cosine similarity, injecting explicit regional routing policies into automated vendor email drafts.

### Phase 8: Terminal-Based Agentic Tool Calling
Decoupled the AI from the visual dashboard, establishing a natural-language operating system directly within the Linux terminal.
* **Autonomous SQL Generation:** The local `llama3.2:1b` model acts as a Data Analyst. It parses plain-English terminal inputs, maps them against the database schema, and generates raw, executable PostgreSQL strings.
* **Few-Shot Alignment:** Secured the 1B model's logic through strict prompt engineering (temperature `0.0` with mapped examples), allowing it to perfectly filter tables and count vectors without dropping parameters or hallucinating syntax.
* **Direct Execution:** A Python orchestration loop intercepts the LLM's SQL output, executes it against the live containerized database, and returns formatted data records directly to the user's screen.

---

## 🛠️ Quick Start & Installation

### 1. Clone & Setup Virtual Environment
```bash
git clone [https://github.com/jonnyHumbolt/small-biz-local-ai.git](https://github.com/jonnyHumbolt/small-biz-local-ai.git)
cd small-biz-local-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

2. Boot the Infrastructure

Ensure the local database and any web UI containers are running in the background.
Bash

docker compose up -d

3. Launch the Data Analyst Agent (CLI)

Interact with the live database using natural language.
Bash

python agent_cli.py

Example CLI Prompts:

    "Show me all items that are critically low."

    "Give me just the item names and their current stock numbers."

    "How many total vendor policies do we have stored?"

🔒 Privacy & Economics

By executing all mathematical embeddings and conversational inferences locally, this architecture guarantees zero data leakage to external APIs. Furthermore, it consolidates ERP, database hosting, and LLM automation into a single local machine environment, reducing monthly operational software overhead to $0.
