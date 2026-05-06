from __future__ import annotations

from rag_pipeline.core.config import Settings
from rag_pipeline.services.llm.anthropic_client import AnthropicClient
from rag_pipeline.services.llm.base import LlmClient
from rag_pipeline.services.llm.openai_client import OpenAiClient


def build_llm_client(settings: Settings) -> LlmClient:
    model = settings.llm_model or ""
    if settings.llm_provider == "anthropic":
        key = settings.anthropic_api_key.get_secret_value() if settings.anthropic_api_key else ""
        return AnthropicClient(api_key=key, model=model)
    key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else ""
    return OpenAiClient(api_key=key, model=model)

