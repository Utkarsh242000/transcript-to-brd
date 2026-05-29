"""
Configuration management with environment variables and CLI overrides.
"""

import os
from pathlib import Path
from typing import Optional, Literal
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load .env file
load_dotenv()


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: Literal["openai", "azure", "mock"] = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "mock"))
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4"))
    azure_api_key: Optional[str] = field(default_factory=lambda: os.getenv("AZURE_OPENAI_KEY"))
    azure_endpoint: Optional[str] = field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT"))
    azure_deployment: Optional[str] = field(default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT"))


@dataclass
class EmbeddingsConfig:
    """Embeddings provider configuration."""
    provider: Literal["openai", "huggingface", "mock"] = field(default_factory=lambda: os.getenv("EMBEDDINGS_PROVIDER", "mock"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"))
    huggingface_model: str = field(default_factory=lambda: os.getenv("HUGGINGFACE_MODEL", "all-MiniLM-L6-v2"))


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""
    index_path: Path = field(default_factory=lambda: Path(os.getenv("FAISS_INDEX_PATH", "knowledge_base/index")))
    kb_facts_path: Path = field(default_factory=lambda: Path(os.getenv("KB_FACTS_PATH", "knowledge_base/confirmed_facts.yaml")))
    kb_conventions_path: Path = field(default_factory=lambda: Path(os.getenv("KB_CONVENTIONS_PATH", "knowledge_base/conventions.yaml")))
    kb_history_path: Path = field(default_factory=lambda: Path(os.getenv("KB_HISTORY_PATH", "knowledge_base/history.jsonl")))


@dataclass
class ProcessingConfig:
    """Text processing configuration."""
    chunk_size: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "256")))
    chunk_overlap: int = field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "50")))
    top_k_retrieval: int = field(default_factory=lambda: int(os.getenv("TOP_K_RETRIEVAL", "5")))
    similarity_threshold: float = field(default_factory=lambda: float(os.getenv("SIMILARITY_THRESHOLD", "0.5")))


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    file: Path = field(default_factory=lambda: Path(os.getenv("LOG_FILE", "logs/app.log")))
    format: Literal["json", "plain"] = field(default_factory=lambda: os.getenv("LOG_FORMAT", "plain"))


@dataclass
class OutputConfig:
    """Output directory configuration."""
    dir: Path = field(default_factory=lambda: Path(os.getenv("OUTPUT_DIR", "output")))
    audit_dir: Path = field(default_factory=lambda: Path(os.getenv("AUDIT_DIR", "output/audit")))

    def __post_init__(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class FeaturesConfig:
    """Feature flags and behavior configuration."""
    interactive_mode: bool = field(default_factory=lambda: os.getenv("INTERACTIVE_MODE", "true").lower() == "true")
    auto_confirm_high_confidence: bool = field(default_factory=lambda: os.getenv("AUTO_CONFIRM_HIGH_CONFIDENCE", "false").lower() == "true")
    confidence_threshold: float = field(default_factory=lambda: float(os.getenv("CONFIDENCE_THRESHOLD", "0.85")))
    mock_mode: bool = field(default_factory=lambda: os.getenv("MOCK_MODE", "false").lower() == "true")


@dataclass
class AppConfig:
    """Main application configuration."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    embeddings: EmbeddingsConfig = field(default_factory=EmbeddingsConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)

    def __post_init__(self):
        """Ensure required directories exist."""
        self.vector_store.index_path.mkdir(parents=True, exist_ok=True)
        self.vector_store.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.logging.file.parent.mkdir(parents=True, exist_ok=True)


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def reset_config() -> None:
    """Reset global configuration (useful for testing)."""
    global _config
    _config = None


def update_config(**kwargs) -> AppConfig:
    """Update configuration with keyword arguments."""
    config = get_config()
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config