# Autonomous Privacy-First Procurement Agent 📦🧠

A production-grade, decoupled microservices architecture that automates small business supply chain workflows locally. This system monitors local inventory data, detects supply chain bottlenecks, and utilizes an isolated local Large Language Model (LLM) to draft vendor procurement orders—running **100% offline with a $0 cloud footprint and absolute data privacy.**

## 📊 System Architecture+---------------------------------------+
             |       YOUR LOCAL OFFLINE HOST        |
             |                                       |
             |   +-------------------------------+   |
             |   |   grocery_ai_frontend         |   |
             |   |   (Streamlit Web UI Dashboard)|   |
             |   +---------------+---------------+   |
             |                   |                   |
             |      Internal Private Network         |
             |                   |                   |
             |   +---------------+---------------+   |
             |   |   grocery_ai_backend          |   |
             |   |   (Ollama / Llama 3.2 1B)     |   |
             |   +---------------+---------------+   |
             |                   |                   |
             |                   v                   |
             |   +-------------------------------+   |
             |   |          Data Layer           |   |
             |   |      (SQLite Inventory DB)    |   |
             |   +-------------------------------+   |
             +---------------------------------------+


### 🚀 Core Features
* **Zero Cloud Bleed:** No API tokens, no monthly cloud subscriptions, and no recurring inference fees.
* **Absolute Privacy:** Sensitive operational data, inventory health, and vendor metrics never leave the local machine.
* **Resource Optimized:** Designed to run seamlessly on consumer-grade local hardware using a decoupled microservices design.
* **Automated Logic:** Automatically maps out supply bottlenecks and packages highly contextual payloads to deliver structurally sound emails.

---

## 🛠️ Quick Start (Local Deployment)

### Prerequisites
* Ensure you have [Docker and Docker Compose](https://docs.docker.com/) installed on your host machine.
* Ensure you have [Ollama](https://ollama.com/) installed and running locally with the `llama3.2:1b` model pulled (`ollama run llama3.2:1b`).

### 1. Clone the Repository
```bash
git clone [https://github.com/jonnyHumbolt/small-biz-local-ai.git](https://github.com/jonnyHumbolt/small-biz-local-ai.git)
cd small-biz-local-ai
