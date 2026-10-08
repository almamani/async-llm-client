import asyncio

from pydantic import ValidationError

from errors import LLMError
from manager import AsyncLLMManager
from schemas import ChatMessage, MessageRole
from settings import cargar_configuracion


async def main():
    try:
        config = cargar_configuracion()
    except ValidationError as error:
        print("Configuración inválida:")

        for detalle in error.errors():
            campo = ".".join(str(parte) for parte in detalle["loc"])
            print(f"- {campo}: {detalle['msg']}")

        return
    except ValueError:
        print("Proveedor inválido: usá openai o anthropic.")
        return

    manager = AsyncLLMManager(config)

    mensajes = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content="Respondé en español de forma breve y clara.",
        ),
        ChatMessage(
            role=MessageRole.USER,
            content="¿Qué es la entropía?",
        ),
    ]

    try:
        print("\nRespuesta completa:")

        respuesta = await manager.generate(mensajes)

        if respuesta.error is not None:
            print(f"Error controlado: {respuesta.error}")
        else:
            print(respuesta.content)

        print("\nRespuesta por streaming:")

        try:
            async for texto in manager.stream(mensajes):
                print(texto, end="", flush=True)
            print()
        except LLMError as error:
            print(f"\nError controlado: {error}")

    finally:
        await manager.close()

    print("\nPrograma finalizado.")


if __name__ == "__main__":
    asyncio.run(main())