# OptiChain: Constraint-Aware Logistics & OTIF Predictive Engine

OptiChain is a decoupled, full-stack decision-intelligence application designed to solve complex multi-warehouse supply chain bottlenecks. Using a high-performance **LangChain Expression Language (LCEL)** RAG pipeline, OptiChain parses multi-warehouse logistics data, enforces strict supplier and routing constraints, evaluates **Economic Order Quantity (EOQ)**, and dynamically predicts stockout risks to safeguard enterprise **On-Time In-Full (OTIF)** performance.

---

## Key Features

- **Constraint-Aware RAG:** Leverages local HuggingFace embeddings (`all-MiniLM-L6-v2`) and ChromaDB to securely vectorize and query inventory constraints, lead times, and warehouse metrics.
- **Enterprise SCM Modeling:** Analyzes operational parameters such as safety stock, EOQ, supplier capacities, and customs delays to generate contextual business recommendations.
- **Modern LCEL Architecture:** Bypasses legacy LangChain chains with highly optimized, customized LCEL runnables for near-zero latency inference.
- **Decoupled Architecture:** Features a modular React/TypeScript frontend and a robust FastAPI backend communicating over a secure REST API pipeline.
- **Blazing Fast Local Inference:** Utilizes Groq paired with Llama-3.1-8B for millisecond response times without compromising reasoning quality.

---

## Tech Stack & Architecture

```text
               +-------------------------------------------+
               |        React & TypeScript Frontend        |
               +---------------------+---------------------+
                                     | (CORS/REST API)
                                     v
               +---------------------+---------------------+
               |         FastAPI Application Server        |
               +---------------------+---------------------+
                                     |
                +--------------------+--------------------+
                |                                         |
                v                                         v
    +-----------+-----------+                 +-----------+-----------+
    |  Chroma Vector Store  |                 |    Groq (Llama-3.1)   |
    | (Local Embeddings)    |                 |   (AI Reasoning)      |
    +-----------------------+                 +-----------------------+

