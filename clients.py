from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from openai import AsyncOpenAI, APIError as OpenAIAPIError
from anthropic import AsyncAnthropic, APIError as AnthropicAPIError

from errors import LLMError

from schemas import ChatMessage, LLMConfig, MessageRole, ModelResponse



class BaseLLMClient(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    async def generate(
        self,
        messages: list[ChatMessage],
    ) -> ModelResponse:
        pass

    @abstractmethod
    def stream(
        self,
        messages: list[ChatMessage],
    ) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass


class OpenAIClient(BaseLLMClient):
    def __init__(self, config: LLMConfig):
        super().__init__(config)

        self.client = AsyncOpenAI(
            api_key=config.api_key.get_secret_value(),
            timeout=20.0,
            max_retries=0,
        )

    async def generate(
        self,
        messages: list[ChatMessage],
    ) -> ModelResponse:
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    mensaje.model_dump(mode="json")
                    for mensaje in messages
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            return ModelResponse(
                provider=self.config.provider,
                model=response.model,
                content=response.choices[0].message.content or "",
            )

        except OpenAIAPIError as error:
            return ModelResponse(
                provider=self.config.provider,
                model=self.config.model,
                content="",
                error=f"Falló OpenAI: {type(error).__name__}",
            )

    async def stream(
        self, messages: list[ChatMessage]
    ) -> AsyncIterator[str]:
        try:
            respuesta = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    mensaje.model_dump(mode="json")
                    for mensaje in messages
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True,
            )

            try:
                async for fragmento in respuesta:
                    if not fragmento.choices:
                        continue

                    texto = fragmento.choices[0].delta.content

                    if texto:
                        yield texto
            finally:
                await respuesta.close()

        except OpenAIAPIError as error:
            raise LLMError(
                f"Falló OpenAI: {type(error).__name__}"
            ) from error

    async def close(self) -> None:
        await self.client.close() 


class AnthropicClient(BaseLLMClient):
    def __init__(self, config: LLMConfig):
        super().__init__(config)

        self.client = AsyncAnthropic(
            api_key=config.api_key.get_secret_value(),
            timeout=20.0,
            max_retries=0,
        )

    async def generate(
        self, messages: list[ChatMessage]
    ) -> ModelResponse:
        instrucciones = []
        conversacion = []

        for mensaje in messages:
            if mensaje.role == MessageRole.SYSTEM:
                instrucciones.append(mensaje.content)
            else:
                conversacion.append(
                    mensaje.model_dump(mode="json")
                )

        try:
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                extra_body={"temperature": self.config.temperature},
                system="\n\n".join(instrucciones),
                messages=conversacion,
            )

            texto = "".join(
                bloque.text
                for bloque in response.content
                if bloque.type == "text"
            )

            return ModelResponse(
                provider=self.config.provider,
                model=response.model,
                content=texto,
            )

        except AnthropicAPIError as error:
            return ModelResponse(
                provider=self.config.provider,
                model=self.config.model,
                content="",
                error=f"Falló Anthropic: {type(error).__name__}",
            )

    async def stream(
        self, messages: list[ChatMessage]
    ) -> AsyncIterator[str]:
        instrucciones = []
        conversacion = []

        for mensaje in messages:
            if mensaje.role == MessageRole.SYSTEM:
                instrucciones.append(mensaje.content)
            else:
                conversacion.append(
                    mensaje.model_dump(mode="json")
                )

        try:
            async with self.client.messages.stream(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                extra_body={"temperature": self.config.temperature},
                system="\n\n".join(instrucciones),
                messages=conversacion,
            ) as respuesta:
                async for texto in respuesta.text_stream:
                    yield texto

        except AnthropicAPIError as error:
            raise LLMError(
                f"Falló Anthropic: {type(error).__name__}"
            ) from error    

    async def close(self) -> None:
        await self.client.close()      