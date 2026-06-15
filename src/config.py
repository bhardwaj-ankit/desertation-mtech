"""Configuration management for the project."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "mistralai/Mistral-7B-v0.1")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma")
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    RAG_RETRIEVAL_K = int(os.getenv("RAG_RETRIEVAL_K", 5))
    RAG_CONFIDENCE_THRESHOLD = float(os.getenv("RAG_CONFIDENCE_THRESHOLD", 0.70))

print("✓ Configuration loaded successfully")
