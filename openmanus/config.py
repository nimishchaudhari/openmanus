"""
Configuration module for OpenManus.

This module handles environment variable loading, configuration settings,
and default values for the OpenManus framework.
"""

import os
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


class ModelConfig(BaseModel):
    """Configuration for language models."""

    provider: str = Field(..., description="Model provider (e.g. 'openai', 'anthropic', 'llama')")
    model_name: str = Field(..., description="Name of the model to use")
    api_key: str = Field(default="", description="API key for the model provider")
    api_base: Optional[str] = Field(default=None, description="Base URL for API requests")
    context_length: int = Field(default=4096, description="Maximum context length for the model")
    temperature: float = Field(default=0.7, description="Temperature for model sampling")
    timeout: int = Field(default=60, description="Request timeout in seconds")
    fallback_models: List[str] = Field(default_factory=list, description="List of fallback models")
    streaming: bool = Field(default=False, description="Whether to use streaming responses")


class MemoryConfig(BaseModel):
    """Configuration for memory systems."""

    episodic_memory_url: str = Field(
        default="redis://localhost:6379/0", description="Redis URL for episodic memory"
    )
    semantic_memory_path: str = Field(
        default="./data/semantic", description="Path to store semantic memory vector database"
    )
    procedural_memory_url: str = Field(
        default="bolt://localhost:7687", description="Neo4j URL for procedural memory"
    )
    procedural_memory_user: str = Field(default="neo4j", description="Neo4j username")
    procedural_memory_password: str = Field(default="password", description="Neo4j password")


class AppConfig(BaseModel):
    """Main application configuration."""

    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    port: int = Field(default=8000, description="Port to run the API server on")
    model: ModelConfig
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    max_workers: int = Field(default=5, description="Maximum number of executor workers")


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.

    Returns:
        AppConfig: The application configuration.
    """
    # Default model configuration from environment variables
    model_config = ModelConfig(
        provider=os.getenv("LLM_PROVIDER", "openai"),
        model_name=os.getenv("LLM_MODEL", "gpt-4"),
        api_key=os.getenv("LLM_API_KEY", ""),
        api_base=os.getenv("LLM_API_BASE"),
        context_length=int(os.getenv("LLM_CONTEXT_LENGTH", "4096")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        fallback_models=os.getenv("LLM_FALLBACK_MODELS", "").split(",") if os.getenv("LLM_FALLBACK_MODELS") else [],
        streaming=os.getenv("LLM_STREAMING", "").lower() == "true",
    )

    # Memory configuration
    memory_config = MemoryConfig(
        episodic_memory_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        semantic_memory_path=os.getenv("SEMANTIC_MEMORY_PATH", "./data/semantic"),
        procedural_memory_url=os.getenv("NEO4J_URL", "bolt://localhost:7687"),
        procedural_memory_user=os.getenv("NEO4J_USER", "neo4j"),
        procedural_memory_password=os.getenv("NEO4J_PASSWORD", "password"),
    )

    # App configuration
    app_config = AppConfig(
        debug=os.getenv("DEBUG", "").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        port=int(os.getenv("PORT", "8000")),
        model=model_config,
        memory=memory_config,
        max_workers=int(os.getenv("MAX_WORKERS", "5")),
    )

    return app_config


# Global configuration instance
config = load_config()
