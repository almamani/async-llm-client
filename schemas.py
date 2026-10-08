from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def validar_contenido(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("El contenido no puede estar vacío.")

        return valor

class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMConfig(BaseModel):
    provider: Provider
    model: str = Field(min_length=1)
    api_key: SecretStr

    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=300, gt=0)

    @field_validator("api_key")
    @classmethod
    def validar_api_key(cls, valor: SecretStr) -> SecretStr:
        if not valor.get_secret_value().strip():
            raise ValueError("La API key no puede estar vacía.")

        return valor

    @field_validator("model")
    @classmethod
    def validar_modelo(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("El modelo no puede estar vacío.")

        return valor

    @model_validator(mode="after")
    def validar_temperatura_por_proveedor(self):
        if self.provider == Provider.ANTHROPIC:
            if self.temperature > 1:
                raise ValueError(
                    "La temperatura para Anthropic debe estar entre 0 y 1."
                )

        return self    

class ModelResponse(BaseModel):
    provider: Provider
    model: str = Field(min_length=1)
    content: str
    error: str | None = None
    