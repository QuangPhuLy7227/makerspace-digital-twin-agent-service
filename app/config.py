from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Digital Twin Agent Service"
    app_env: str = "development"
    app_debug: bool = True

    host: str = "0.0.0.0"
    port: int = 9000

    backend_api_base: str = "http://host.docker.internal:5017"
    backend_timeout_seconds: int = 10

    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "qwen2.5:7b-instruct"

    agent_max_tool_calls: int = 5

    # New: static knowledge / RAG
    static_knowledge_dir: str = "data/static_knowledge"
    rag_index_dir: str = "data/rag_index"
    rag_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 4
    rag_chunk_size: int = 900
    rag_chunk_overlap: int = 150
    static_knowledge_use_llm: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()