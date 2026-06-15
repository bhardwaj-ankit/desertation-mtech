# Technology Stack & Tools Guide

**Project:** Agentic Multimodal AI Framework for Aircraft Techlog Intelligence  
**BITS ID:** 2024AA5039  
**Last Updated:** 2026-05-24

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Complete Technology Stack](#complete-technology-stack)
3. [Installation Guide](#installation-guide)
4. [Configuration](#configuration)
5. [Quick Start](#quick-start)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  USER INTERFACE LAYER                       │
│            (Streamlit + FastAPI Endpoints)                  │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│              AGENT ORCHESTRATION LAYER                      │
│    (LangGraph: Planning, Tool Routing, State Management)    │
└─────────────────────────────────────────────────────────────┘
         ↓
┌────────────────┬──────────────────┬──────────────────────────┐
│                │                  │                          │
↓                ↓                  ↓                          ↓
[RAG Pipeline] [Triage Agent]  [Recurrence Agent]     [Reasoning Agent]
(LangChain/    (PyTorch)       (PyTorch LSTM)         (Fine-tuned LLM)
Llama-Index)   (MLP)           (Attention)            (Mistral-7B + LoRA)
    ↓              ↓                  ↓                          ↓
[Vector DB]  [Classifier]      [LSTM Encoder]          [RAG Context]
(Chroma)     (8-class)         (Seq Modeling)          (Retrieved Docs)
                               
         ↓                ↓                ↓                ↓
┌─────────────────────────────────────────────────────────────┐
│              SAFETY & GOVERNANCE LAYER                      │
│  (Confidence Scoring, Abstention, Audit Logging, Citations) │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT GENERATION                        │
│        (Recommendation + Citations + Confidence Score)      │
└─────────────────────────────────────────────────────────────┘
```

---

## Complete Technology Stack

### **1. LLM & Agent Orchestration**

| Component | Tool | Version | Purpose | Installation |
|-----------|------|---------|---------|--------------|
| Agentic Framework | **LangGraph** | 0.0.4+ | Agent planning, tool routing, state management | `pip install langgraph` |
| RAG Framework | **LangChain** | 0.1.0+ | RAG pipeline, document loaders, chains | `pip install langchain` |
| RAG Alternative | **Llama-Index** | 0.9.0+ | Alternative RAG (document indexing, querying) | `pip install llama-index` |
| **Recommended Setup:** | LangGraph (orchestration) + LangChain (RAG) |

```python
# Example: LangGraph + LangChain RAG
from langgraph.graph import StateGraph
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Setup: LangGraph manages agent flow, LangChain handles RAG retrieval
```

---

### **2. Vector Databases**

| Database | Type | Best For | Pros | Cons | Installation |
|----------|------|----------|------|------|--------------|
| **Chroma** ✅ | Embedded/Cloud | Development & Small deployments | Easy setup, API, open-source | Limited scale | `pip install chromadb` |
| **FAISS** | In-memory | Research, experiments | Fast, lightweight, free | No persistence | `pip install faiss-cpu` |
| **Weaviate** | Cloud-native | Production, scaling | GraphQL, filtering, hybrid search | Complex setup | Docker container |
| **Milvus** | Distributed | Large-scale deployments | Scalable, high-performance | DevOps heavy | Docker + Kubernetes |
| **Qdrant** | Vector-first | Fast retrieval | Filtering, performance | Smaller community | Docker or managed |

**Recommendation:**
- **Development:** Chroma (local, no setup)
- **Production:** Weaviate or Milvus

```bash
# Chroma setup (recommended for dissertation)
pip install chromadb
```

---

### **3. Embedding Models**

| Model | Size | Speed | Quality (MTEB) | Cost | Use Case | Installation |
|-------|------|-------|--------|------|----------|--------------|
| **all-MiniLM-L6-v2** ✅ | 22M | ⚡⚡⚡ | 86 | Free | **Dissertation (default)** | Included in sentence-transformers |
| **all-mpnet-base-v2** | 109M | ⚡⚡ | 89 | Free | Production when compute available | Included in sentence-transformers |
| **E5-Base** | 109M | ⚡⚡ | 91 | Free | Academic research | `from transformers import AutoModel` |
| **BGE-Large** | 335M | ⚡ | 95 | Free | Maximum quality (research) | `from transformers import AutoModel` |
| **OpenAI text-embedding-3-small** | Proprietary | ⚡⚡ | 94 | $0.02/1M tokens | When using OpenAI API | `pip install openai` |

```bash
pip install sentence-transformers
# Usage: SentenceTransformer('all-MiniLM-L6-v2')
```

---

### **4. Large Language Models**

| Model | Size | License | Cost | Setup | Recommendation |
|-------|------|---------|------|-------|-----------------|
| **Mistral-7B** ✅ | 7B | Apache 2.0 | Free | Local or via API | **Best for dissertation** |
| **Llama-2-7B** | 7B | Llama 2 Community | Free | Local or via API | Good alternative |
| **Phi-3** | 3.8B | MIT | Free | Local (lightweight) | For low-resource environments |
| **GPT-4** | Proprietary | Proprietary | $0.03/1K tokens | API only | Best quality |
| **Claude-3 (Anthropic)** | Proprietary | Proprietary | $0.003/1K tokens | API only | Very good quality |

```bash
# For local Mistral-7B
pip install transformers torch

# Load model
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
```

---

### **5. Fine-tuning & Parameter-Efficient Adaptation**

| Tool | Method | Memory Reduction | Speed | Best For | Installation |
|------|--------|-----------------|-------|----------|--------------|
| **PEFT** ✅ | LoRA | 90% | Fast | **LLM fine-tuning (recommended)** | `pip install peft` |
| **QLoRA** | 4-bit Quantized LoRA | 95% | Very fast | Extreme resource constraints | `pip install peft bitsandbytes` |
| **Lit-GPT** | Multiple methods | Flexible | Medium | PyTorch Lightning workflows | `pip install lit-gpt` |
| **Axolotl** | All methods | Flexible | Medium | Comprehensive configuration | `pip install axolotl` |

```python
# LoRA fine-tuning example
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "v_proj"]
)

model = get_peft_model(model, lora_config)
```

---

### **6. Deep Learning Frameworks**

| Framework | Primary Use | Ecosystem | Recommendation |
|-----------|-------------|-----------|-----------------|
| **PyTorch** ✅ | Deep learning, ML research | Transformers, Lightning, TorchMetrics | **Primary framework** |
| **PyTorch Lightning** ✅ | Training loops, cleanup code | Callbacks, logging, distributed training | **For clean training** |
| **TensorFlow/Keras** | Alternative deep learning | TF.Text, KerasTuner | Not recommended for this project |

```bash
pip install torch pytorch-lightning
```

---

### **7. Transformer Models & NLP**

| Library | Purpose | Key Components | Installation |
|---------|---------|-----------------|--------------|
| **Transformers (HuggingFace)** ✅ | Model loading, inference, training | AutoModel, AutoTokenizer, Trainer | `pip install transformers` |
| **Tokenizers** | Fast tokenization | BPE, WordPiece tokenizers | Included with transformers |
| **spaCy** ✅ | NLP preprocessing, NER, POS | Pipelines, entity recognition | `pip install spacy` + `python -m spacy download en_core_web_sm` |
| **NLTK** | NLP utilities | Tokenization, stemming, lemmatization | `pip install nltk` |
| **TextBlob** | Simple NLP | Sentiment, POS tagging | Skip for this project |

---

### **8. Sequence Modeling (LSTM, Transformers)**

| Component | Framework | Use Case | Installation |
|-----------|-----------|----------|--------------|
| **nn.LSTM** (PyTorch) ✅ | Recurrence prediction | Temporal defect modeling | Built into PyTorch |
| **nn.Transformer** (PyTorch) | Sequence-to-sequence | Alternative to LSTM | Built into PyTorch |
| **Temporal Fusion Transformer** | Time-series forecasting | Operational signals (optional) | `pip install pytorch-forecasting` |

```python
import torch.nn as nn

lstm = nn.LSTM(
    input_size=3,
    hidden_size=64,
    num_layers=2,
    batch_first=True,
    dropout=0.2
)
```

---

### **9. Data Processing & Feature Engineering**

| Library | Purpose | Key Functions | Installation |
|---------|---------|----------------|--------------|
| **Pandas** ✅ | Data manipulation, preprocessing | read_csv, groupby, merge, apply | `pip install pandas` |
| **NumPy** ✅ | Numerical computing | arrays, matrix operations | `pip install numpy` |
| **Scikit-learn** ✅ | ML utilities, metrics | train_test_split, metrics, preprocessing | `pip install scikit-learn` |
| **Polars** | Fast dataframes (alternative to Pandas) | Operations similar to Pandas | `pip install polars` |
| **DuckDB** | SQL on dataframes | Large dataset queries | `pip install duckdb` |

---

### **10. Evaluation Metrics**

| Library | Metrics Provided | Best For | Installation |
|---------|------------------|----------|--------------|
| **scikit-learn** ✅ | Classification: F1, precision, recall, AUROC, confusion matrix | **All traditional ML metrics** | Included with scikit-learn |
| **torchmetrics** ✅ | AUROC, F1, AUPRC, accuracy | PyTorch model evaluation | `pip install torchmetrics` |
| **ragas** ✅ | RAG-specific: faithfulness, relevance, context precision, answer relevance | **RAG evaluation (required)** | `pip install ragas` |
| **BERTScore** | Semantic similarity | LLM output quality | `pip install bert-score` |

```bash
# RAG evaluation
pip install ragas
# Provides: faithfulness, answer_relevance, context_precision, context_recall
```

---

### **11. Text Chunking & Preprocessing**

| Tool | Method | Integration | Installation |
|------|--------|-------------|--------------|
| **LangChain Splitters** ✅ | RecursiveCharacterTextSplitter, SentenceSplitter | Built into LangChain | Included with langchain |
| **Llama-Index Splitters** | SemanticSplitter, TokenSplitter | Built into Llama-Index | Included with llama-index |
| **Custom chunking** ✅ | Maintenance-aware document splitting | Custom implementation | N/A |

---

### **12. Document Loading**

| Loader | Formats Supported | Integration | Installation |
|--------|-------------------|-------------|--------------|
| **LangChain Loaders** ✅ | PDF, DOCX, CSV, JSON, TXT, web | Built-in | Included with langchain |
| **Llama-Index Loaders** | PDF, DOCX, CSV, web, databases | Built-in | Included with llama-index |
| **PyPDF2** | PDF | Standalone | `pip install PyPDF2` |
| **python-docx** | DOCX | Standalone | `pip install python-docx` |

---

### **13. Web Framework & API**

| Tool | Purpose | Framework Type | Installation |
|------|---------|-----------------|--------------|
| **FastAPI** ✅ | REST API backend, OpenAPI docs | Modern async framework | `pip install fastapi uvicorn` |
| **Flask** | Alternative web framework | Lightweight | `pip install flask` |
| **Uvicorn** | ASGI server for FastAPI | Application server | Included with FastAPI |

```bash
pip install fastapi uvicorn
```

---

### **14. User Interface & Dashboard**

| Tool | Type | Best For | Installation |
|------|------|----------|--------------|
| **Streamlit** ✅ | Interactive dashboards, demos | **Evaluation UI & prototyping** | `pip install streamlit` |
| **Gradio** | Simple web interface | Quick demo interfaces | `pip install gradio` |
| **Dash** | Interactive dashboards | Complex analytics dashboards | `pip install dash` |
| **Jupyter Notebook** | Interactive notebooks | Research & exploration | `pip install jupyter` |

```bash
pip install streamlit
```

---

### **15. Monitoring, Logging & Experiment Tracking**

| Tool | Purpose | Best For | Installation |
|------|---------|----------|--------------|
| **Weights & Biases (W&B)** ✅ | Experiment tracking, logging | Training experiments, model versioning | `pip install wandb` |
| **MLflow** | Model versioning, tracking | Alternative to W&B | `pip install mlflow` |
| **TensorBoard** | Training visualization | PyTorch training logs | Included with PyTorch |
| **Python logging** ✅ | Event logging, audit trails | System logs, audit logging | Built-in |

```bash
pip install wandb
```

---

### **16. Testing & Code Quality**

| Tool | Purpose | Installation |
|------|---------|--------------|
| **pytest** ✅ | Unit testing, integration tests | `pip install pytest` |
| **coverage** ✅ | Code coverage analysis | `pip install coverage` |
| **black** | Code formatting | `pip install black` |
| **flake8** | Linting | `pip install flake8` |

---

### **17. Containerization & Reproducibility**

| Tool | Purpose | Installation |
|------|---------|--------------|
| **Docker** ✅ | Containerization for reproducibility | [Docker Desktop](https://www.docker.com/products/docker-desktop) |
| **docker-compose** | Multi-container orchestration | Included with Docker Desktop |

---

## Installation Guide

### **Step 1: Create Virtual Environment**

```bash
# Navigate to project directory
cd /Users/ankitbhardwaj/Documents/dissertaion-abstract

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.10+
```

### **Step 2: Create requirements.txt**

```bash
cat > requirements.txt << 'EOF'
# Core LLM & RAG
langgraph==0.0.4
langchain==0.1.0
llama-index==0.9.0
transformers==4.36.0

# Vector Database
chromadb==0.4.0
faiss-cpu==1.7.4

# Embeddings
sentence-transformers==2.2.2

# Deep Learning
torch==2.1.0
pytorch-lightning==2.1.0
torchmetrics==1.2.0

# Fine-tuning
peft==0.7.0

# Data Processing
pandas==2.1.0
numpy==1.24.0
scikit-learn==1.3.0

# NLP
spacy==3.7.2
nltk==3.8

# RAG Evaluation
ragas==0.0.20
rouge-score==0.1.2

# Web & UI
fastapi==0.104.0
uvicorn==0.24.0
streamlit==1.28.0

# Utilities
python-dotenv==1.0.0
tqdm==4.66.0
requests==2.31.0

# Monitoring
wandb==0.16.0

# Testing
pytest==7.4.0
coverage==7.3.0

# Optional: LLM APIs
openai==1.3.0
anthropic==0.7.0

# Documentation
pydantic==2.0.0
EOF
```

### **Step 3: Install Dependencies**

```bash
# Install all packages
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm

# Verify installations
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import transformers; print('Transformers: OK')"
python -c "import chromadb; print('Chroma: OK')"
python -c "import langchain; print('LangChain: OK')"
```

### **Step 4: Download Models (Optional)**

```bash
# Download Mistral-7B (requires ~14GB disk space)
python << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM

# This will download and cache Mistral-7B
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
print("Mistral-7B downloaded successfully!")
EOF
```

---

## Configuration

### **Environment Variables (.env)**

Create `.env` file in project root:

```bash
cat > .env << 'EOF'
# LLM Configuration
LLM_MODEL_NAME=mistralai/Mistral-7B-v0.1
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=512

# Vector Database
VECTOR_DB_TYPE=chroma  # Options: chroma, faiss, weaviate
VECTOR_DB_PATH=./data/vector_db

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# RAG Configuration
RAG_RETRIEVAL_K=5  # Top-k documents to retrieve
RAG_CONFIDENCE_THRESHOLD=0.70  # Confidence threshold for abstention

# Data Paths
DATA_RAW_PATH=./data/raw
DATA_PROCESSED_PATH=./data/processed
MODELS_PATH=./models

# Training
BATCH_SIZE=32
LEARNING_RATE=1e-3
NUM_EPOCHS=50
EARLY_STOPPING_PATIENCE=5

# Monitoring
WANDB_PROJECT=techlog-copilot
WANDB_ENTITY=your-username

# Optional: API Keys (if using cloud LLMs)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
EOF
```

---

## Quick Start

### **Project Structure**

```
dissertaion-abstract/
├── TOOLS.md                          # This file
├── README.md                         # Project overview
├── requirements.txt                  # Dependencies
├── .env                              # Configuration
├── .gitignore
│
├── research/                         # Original research documents
│   ├── Abstract report submitted.pdf
│   ├── initial_abstract.md
│   ├── deep-research-report.md
│   ├── Outline_Viva_Slides.pptx
│   └── ...
│
├── src/                              # Source code
│   ├── __init__.py
│   ├── config.py                     # Configuration loading
│   ├── embeddings.py                 # Embedding utilities
│   ├── vector_store.py               # Vector DB operations
│   ├── rag_pipeline.py               # RAG implementation
│   ├── agents/
│   │   ├── orchestrator.py           # Agent orchestration (LangGraph)
│   │   ├── triage_agent.py           # Defect classification
│   │   ├── recurrence_agent.py       # Recurrence prediction
│   │   └── reasoning_agent.py        # LLM reasoning
│   ├── models/
│   │   ├── triage_classifier.py      # Multimodal triage model
│   │   ├── recurrence_predictor.py   # LSTM recurrence model
│   │   └── fine_tuning.py            # LoRA fine-tuning
│   ├── utils/
│   │   ├── data_processing.py        # Preprocessing utilities
│   │   ├── evaluation.py             # Metrics & evaluation
│   │   └── logging.py                # Audit logging
│   ├── api.py                        # FastAPI application
│   └── ui.py                         # Streamlit dashboard
│
├── data/
│   ├── raw/                          # Raw datasets
│   │   ├── techlogs.csv
│   │   ├── manuals/
│   │   └── mel_cdl/
│   ├── processed/                    # Processed datasets
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── vector_db/                    # Vector store (Chroma)
│
├── models/                           # Trained models
│   ├── triage_classifier.pth
│   ├── recurrence_predictor.pth
│   ├── lora_adapters/
│   └── checkpoints/
│
├── tests/                            # Unit tests
│   ├── test_embeddings.py
│   ├── test_rag_pipeline.py
│   ├── test_agents.py
│   └── test_models.py
│
├── notebooks/                        # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_evaluation.ipynb
│
├── logs/                             # Training & audit logs
│   ├── training.log
│   └── audit_trail.json
│
├── Dockerfile                        # Containerization
└── docker-compose.yml                # Multi-container setup
```

### **Run Streamlit Dashboard**

```bash
cd /Users/ankitbhardwaj/Documents/dissertaion-abstract

streamlit run src/ui.py
# Opens at: http://localhost:8501
```

### **Run FastAPI Backend**

```bash
cd /Users/ankitbhardwaj/Documents/dissertaion-abstract

uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
# API docs at: http://localhost:8000/docs
```

### **Run Training Pipeline**

```bash
python src/models/fine_tuning.py
# Or with PyTorch Lightning CLI:
# pytorch-lightning train --config training_config.yaml
```

### **Run Tests**

```bash
pytest tests/ -v --cov=src --cov-report=html
```

---

## Quick Reference Commands

```bash
# Activate environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run code formatter
black src/

# Run linter
flake8 src/

# Run tests
pytest tests/ -v

# Build Docker image
docker build -t techlog-copilot:latest .

# Run container
docker run -p 8000:8000 -p 8501:8501 techlog-copilot:latest

# Clear Chroma cache
rm -rf data/vector_db/

# View training logs
tail -f logs/training.log

# View audit trail
cat logs/audit_trail.json | jq .
```

---

## Resources & Documentation

| Resource | Link | Purpose |
|----------|------|---------|
| LangGraph Docs | https://github.com/langchain-ai/langgraph | Agent orchestration |
| LangChain Docs | https://python.langchain.com/ | RAG & chains |
| PyTorch Docs | https://pytorch.org/docs/stable/index.html | Deep learning |
| Transformers Docs | https://huggingface.co/docs/transformers/ | LLM models |
| Chroma Docs | https://docs.trychroma.com/ | Vector database |
| FastAPI Docs | https://fastapi.tiangolo.com/ | Web framework |
| Streamlit Docs | https://docs.streamlit.io/ | Dashboard UI |
| RAGAS Docs | https://docs.ragas.io/ | RAG evaluation |

---

## Troubleshooting

### **Issue: CUDA/GPU not detected**
```bash
# Check PyTorch GPU support
python -c "import torch; print(torch.cuda.is_available())"

# Install CPU version
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
```

### **Issue: OOM (Out of Memory)**
```bash
# Use QLoRA (more memory efficient)
# Or reduce batch_size in .env
# Or use smaller embedding model (all-MiniLM instead of mpnet)
```

### **Issue: Chroma permission denied**
```bash
# Clear cache and reinitialize
rm -rf data/vector_db/
python -c "from chromadb import Client; Client()"
```

---

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Configure `.env` with your settings
3. ✅ Explore `research/` folder for project context
4. ✅ Start implementing `src/` modules
5. ✅ Run `streamlit run src/ui.py` to test UI
6. ✅ Execute `pytest tests/` to validate code

---

**Happy Coding! 🚀**
