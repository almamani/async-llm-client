import os
from pathlib import Path

from dotenv import load_dotenv

from schemas import LLMConfig, Provider


def cargar_configuracion() -> LLMConfig:
    ruta_env = Path(__file__).with_name(".env")
    load_dotenv(ruta_env)

    provider = Provider(
        os.getenv("LLM_PROVIDER", "openai")
    )

    nombres_claves = {
        Provider.OPENAI: "OPENAI_API_KEY",
        Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
    }

    return LLMConfig(
        provider=provider,
        model=os.getenv("LLM_MODEL", ""),
        api_key=os.getenv(nombres_claves[provider], ""),
        temperature=os.getenv("LLM_TEMPERATURE", "0.7"),
        max_tokens=os.getenv("LLM_MAX_TOKENS", "300"),
    )