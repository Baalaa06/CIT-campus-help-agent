from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Groq LLM
    groq_api_key: str = Field(..., description="Groq API key")
    llm_model: str = "llama-3.1-8b-instant"
    response_llm_model: str = "llama-3.3-70b-versatile"
    max_tokens: int = 2048
    temperature: float = 0.1

    # Firebase
    firebase_service_account_path: str = Field(default="./firebase-service-account.json", description="Path to Firebase service account JSON file")
    firebase_service_account_json: str = Field(default="{}", description="Firebase service account JSON string (used on Render)")
    firebase_web_api_key: str = Field(default="", description="Firebase Web API key")

    # LangGraph checkpointer (SQLite — internal only)
    checkpoint_db_path: str = "./data_store/checkpoints.db"

    # ChromaDB — embedded persistent mode
    chroma_persist_dir: str = "./data_store/chroma_db"
    chroma_collection_name: str = "campus_docs"

    # RAG
    data_dir: str = "./data"
    chunk_size: int = 800
    chunk_overlap: int = 150
    retrieval_top_k: int = 10
    rerank_top_k: int = 3
    confidence_threshold: float = 0.7

    # Embeddings — HuggingFace Inference API (no local model download)
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    huggingface_api_key: str = Field(default="", description="HuggingFace API token for inference API")

    # Reranker — Cohere API (free tier 1000 calls/month)
    cohere_api_key: str = Field(default="", description="Cohere API key for reranking")
    rerank_top_k: int = 3

    # LangSmith (optional)
    langchain_tracing_v2: str = "false"
    langchain_api_key: str = ""
    langchain_project: str = "campus-help-agent"

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_url: str = "http://localhost:8000"

    # Security
    rate_limit: str = "20/minute"
    max_query_length: int = 1000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def ensure_data_store(self) -> None:
        Path("./data_store").mkdir(parents=True, exist_ok=True)
        Path(self.chroma_persist_dir).mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    s.ensure_data_store()
    return s


settings = get_settings()
