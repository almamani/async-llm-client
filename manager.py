from collections.abc import AsyncIterator

from clients import BaseLLMClient, OpenAIClient, AnthropicClient
from schemas import ChatMessage, LLMConfig, ModelResponse, Provider


class AsyncLLMManager:
    def __init__(self, config: LLMConfig):
        self.client: BaseLLMClient

        if config.provider == Provider.OPENAI:
            self.client = OpenAIClient(config)
        elif config.provider == Provider.ANTHROPIC:
            self.client = AnthropicClient(config)
        else:
            raise ValueError("Proveedor no soportado")

    async def generate(
        self, messages: list[ChatMessage]
    ) -> ModelResponse:
        return await self.client.generate(messages)

    async def stream(
        self, messages: list[ChatMessage]
    ) -> AsyncIterator[str]:
        async for texto in self.client.stream(messages):
            yield texto

    async def close(self) -> None:
        await self.client.close()        