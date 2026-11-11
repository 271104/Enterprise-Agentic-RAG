"""Application configuration loaded from environment variables."""

import os
from importlib.util import find_spec
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "gemini").lower()
    qdrant_url: str | None = os.getenv("QDRANT_CLUSTER_ENDPOINT")
    qdrant_api_key: str | None = os.getenv("QDRANT_API_KEY")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "enterprise_rag")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    portkey_api_key: str | None = os.getenv("PORTKEY_API_KEY")
    groq_slug: str = os.getenv("GROQ_SLUG", "rag")
    groq_slug_2: str = os.getenv("GROQ_SLUG_2", "brag")
    logfire_token: str | None = os.getenv("LOGFIRE_TOKEN")
    langsmith_tracing: str = os.getenv("LANGSMITH_TRACING", "false")
    langsmith_api_key: str | None = os.getenv("LANGSMITH_API_KEY")
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "enterprise-agentic-rag")
    langsmith_endpoint: str = os.getenv(
        "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
    )

    def validate_runtime(self) -> None:
        """Raise a readable error when required runtime integrations are unconfigured."""
        required = {
            "QDRANT_CLUSTER_ENDPOINT": self.qdrant_url,
            "PORTKEY_API_KEY": self.portkey_api_key,
            "GROQ_API_KEY": self.groq_api_key,
        }
        if self.embedding_provider == "gemini":
            required["GEMINI_API_KEY"] = self.gemini_api_key
        elif self.embedding_provider != "local":
            raise RuntimeError("EMBEDDING_PROVIDER must be 'gemini' or 'local'")
        elif find_spec("sentence_transformers") is None:
            raise RuntimeError(
                "sentence-transformers must be installed when EMBEDDING_PROVIDER=local"
            )
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                "Missing required configuration: " + ", ".join(missing)
            )


settings = Settings()

# LangChain reads these variables directly for optional tracing.
os.environ["LANGCHAIN_TRACING_V2"] = settings.langsmith_tracing
os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key or ""
os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint
