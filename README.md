# [RXZ.] AI Anime & Manga Recommender

An AI-powered anime and manga recommendation system built with Retrieval-Augmented Generation (RAG). Ask in natural language and get personalized recommendations backed by a searchable database of 85,000+ titles.

---

## Overview

This project combines vector similarity search with a large language model to recommend anime and manga based on natural language queries. The system understands context across a conversation, remembers your preferences, and explains why each title matches your request.

Built as a personal portfolio project to explore RAG pipelines, LangChain agent architectures, and production ML deployment.

---

## Features

- **Conversational recommendations** — multi-turn chat with memory across the session
- **Combined anime + manga** — single interface for both, with a filter to scope results
- **Source-backed answers** — every recommendation shows the retrieved titles with scores, genres, and status
- **Query expansion** — LLM rewrites your query into richer search terms before retrieval
- **Streaming responses** — answers stream token by token instead of appearing all at once
- **Recommendation history** — browse past queries and their sources in a dedicated page

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Groq (LLaMA 3.3 70B) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store | FAISS |
| RAG Framework | LangChain |
| Agent | LangGraph ReAct |
| Data | Kaggle — Complete Anime & Manga Dataset 2026 |
| Language | Python 3.12 |
| Package Manager | uv |

---

## Project Structure

```
AI_Anime_Manga_Recommender/
│
├── app/                          # Streamlit frontend
│   ├── components/
│   │   ├── anime_card.py         # Renders individual result cards
│   │   └── chat_interfaces.py    # Chat bubble rendering
│   ├── pages/
│   │   ├── home.py               # Landing page
│   │   ├── recommendations.py    # Main chat interface
│   │   └── history.py            # Past queries browser
│   ├── utils/
│   │   └── session_state.py      # Centralized session state management
│   └── main.py                   # Entry point + page router
│
├── backend/
│   ├── agents/
│   │   └── anime_agent.py        # LangGraph ReAct agent
│   ├── chains/
│   │   ├── retrieval_chain.py    # RAG chain with streaming support
│   │   └── recommender_chain.py  # Query expansion + recommendation logic
│   ├── prompts/
│   │   ├── system_prompt.txt     # Otaku Oracle persona + output format
│   │   └── recommendation_prompt.txt
│   ├── tools/
│   │   ├── anime_search.py       # FAISS search as LangChain tool
│   │   └── preference_tool.py    # Preference extraction tool
│   └── vectorstore/
│       ├── data_loader.py        # Load, clean, and build embed_text
│       ├── ingest.py             # Embed + build + save FAISS index
│       └── retriever.py          # Load index, MMR retriever
│
├── config/
│   ├── settings.py               # Pydantic BaseSettings
│   ├── logging.py                # Thread-safe logger
│   └── customException.py        # Structured exception handling
│
├── data/
│   ├── raw/                      # Original CSV files from Kaggle (not committed)
│   ├── processed/                # combined_dataset.csv (not committed)
│   └── vectorstore/              # Persisted FAISS index (not committed)
│
├── .env.example
├── packages.txt                  # HF Spaces system dependencies
├── requirements.txt              # HF Spaces Python dependencies
├── pyproject.toml
└── README.md
```

---

## Setup & Installation

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Groq API key — [console.groq.com](https://console.groq.com)
- HuggingFace token — [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### 1. Clone the repository

```bash
git clone https://github.com/rich-aard/AI_Anime_Manga_Recommender.git
cd AI_Anime_Manga_Recommender
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
LOG_LEVEL=INFO
APP_ENV=development
```

### 4. Download the dataset

Download from Kaggle: [Complete Anime & Manga Dataset 2026](https://www.kaggle.com/datasets/patelris/anime-and-manga-dataset-2026/data)

Place the files in `data/raw/`:
```
data/raw/anime_dataset.csv
data/raw/manga_dataset.csv
```

### 5. Build the vector index

**Linux / Mac:**
```bash
uv run python -m backend.vectorstore.data_loader
uv run python -m backend.vectorstore.ingest
```

**Windows (PowerShell):**
```powershell
uv run python -m backend.vectorstore.data_loader
uv run python -m backend.vectorstore.ingest
```

Ingestion takes approximately 50 minutes on CPU for 85,977 documents.

### 6. Run the app

**Linux / Mac:**
```bash
uv run streamlit run app/main.py
```

**Windows (PowerShell):**
```powershell
uv run streamlit run app/main.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Usage

**Basic recommendation:**
> "Recommend me a dark psychological anime"

**Similarity-based:**
> "Something similar to Berserk"

**Preference-based:**
> "I love action anime with strong character development, no romance"

**Cross-media:**
> "Show me both anime and manga with supernatural themes"

**Follow-up:**
> "Give me more like the first one"

Use the sidebar to filter results by Anime, Manga, or Both.

---

## Configuration

| Variable | Description | Default |
|---|---|---|
| `GROQ_API_KEY` | Groq API key for LLM inference | required |
| `HF_TOKEN` | HuggingFace token for embeddings | required |
| `LOG_LEVEL` | Logging level | `INFO` |
| `APP_ENV` | Environment | `development` |

---

## How It Works

```
User query
    │
    ▼
Query Expansion (LLM rewrites query into synopsis-like prose)
    │
    ▼
FAISS Vector Search (MMR retrieval, k=5, fetch_k=100)
    │
    ▼
Context Formatting (title + genres + score + synopsis)
    │
    ▼
LLM Generation (LLaMA 3.3 70B via Groq, streamed)
    │
    ▼
Numbered recommendations with sources
```

---

## Dataset

[Complete Anime & Manga Dataset 2026](https://www.kaggle.com/datasets/patelris/anime-and-manga-dataset-2026/data) by patelris on Kaggle.

```
Anime:    25,634 titles
Manga:    60,343 titles
Total:    85,977 indexed titles
```

---