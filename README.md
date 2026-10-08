# async-llm-client

Preentrega 1 del curso AI Engineering de Coderhouse: cliente unificado y asíncrono para OpenAI y Anthropic, desarrollado con Python 3.12.

Permite seleccionar el proveedor mediante configuración, obtener una respuesta completa o recibir fragmentos por streaming. Los mensajes y la configuración se validan con Pydantic.

## Archivos

| Archivo | Responsabilidad |
| --- | --- |
| `schemas.py` | Roles, proveedores, mensajes, configuración y respuestas con Pydantic. |
| `clients.py` | Contrato abstracto y clientes asíncronos de OpenAI y Anthropic. |
| `manager.py` | Selección del cliente y delegación de generación, streaming y cierre. |
| `errors.py` | Excepción común `LLMError` para errores de streaming. |
| `settings.py` | Lectura de variables de entorno y construcción de la configuración. |
| `main.py` | Demostración de respuesta completa y streaming. |
| `.env.example` | Plantilla de configuración, sin claves. |
| `requirements.txt` | Dependencias con versiones fijadas. |
| `.gitignore` | Exclusión de secretos, entorno virtual y cachés. |

## Instalación

Desde la carpeta del proyecto, crear un entorno virtual con Python 3.12.

En Windows con Git Bash:

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

En Linux o macOS con Python 3.12 instalado:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Configuración

Copiar la plantilla:

```bash
cp .env.example .env
```

Editar `.env` para seleccionar el proveedor y el modelo. Ejemplo para OpenAI:

```dotenv
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=300

OPENAI_API_KEY=clave-del-proveedor
ANTHROPIC_API_KEY=
```

Para Anthropic, cambiar `LLM_PROVIDER` a `anthropic`, `LLM_MODEL` a `claude-haiku-4-5-20251001` y completar `ANTHROPIC_API_KEY`. Solo se exige la clave del proveedor seleccionado.

| Variable | Uso |
| --- | --- |
| `LLM_PROVIDER` | `openai` o `anthropic`. Por defecto: `openai`. |
| `LLM_MODEL` | Identificador del modelo del proveedor elegido. Obligatorio. |
| `LLM_TEMPERATURE` | Entre 0 y 2; para Anthropic esta implementación restringe el valor a 0–1. Por defecto: `0.7`. |
| `LLM_MAX_TOKENS` | Entero mayor que cero. Por defecto: `300`. |
| `OPENAI_API_KEY` | Clave requerida cuando el proveedor es OpenAI. |
| `ANTHROPIC_API_KEY` | Clave requerida cuando el proveedor es Anthropic. |

Las variables ya definidas en el entorno tienen prioridad sobre `.env`. El archivo se busca junto a `settings.py`.

Pydantic rechaza claves y modelos vacíos, roles inválidos, mensajes sin contenido y parámetros fuera de rango. `SecretStr` oculta la clave al representar la configuración; no cifra el archivo `.env`. La validación local de la clave comprueba que exista, no que sea auténtica.

El cliente Anthropic envía la temperatura mediante `extra_body`, para el modelo indicado y la versión del SDK usada. Si se cambia de modelo, se debe revisar qué parámetros admite.

## Ejecución

```bash
python main.py
```

El script pregunta «¿Qué es la entropía?» primero en modo completo y luego por streaming. Son dos solicitudes independientes, ejecutadas en secuencia. Las llamadas utilizan los SDKs asíncronos y no usan `time.sleep()`.

Para obtener respuestas reales se requiere una clave válida, acceso al modelo y cuota disponible. Los fragmentos del stream pueden contener partes de palabras, palabras o varias palabras; no necesariamente coinciden con un token individual.

## Manejo de errores y recursos

- `generate()` devuelve `ModelResponse`. En caso de error de la API o conexión, `content` es una cadena vacía y `error` contiene el proveedor y el tipo de error. En caso de éxito, `error` es `None`.
- `stream()` transforma los errores del SDK en `LLMError`; `main.py` los captura para mantener el programa funcionando.
- Los errores de configuración se muestran antes de crear el cliente.
- Cada SDK se configura con timeout de 20 segundos y sin reintentos automáticos. Ese timeout no impone un límite global de 20 segundos a toda la ejecución.
- Los streams se cierran al salir de su bloque y `main.py` cierra el cliente en un `finally`.

## Pruebas realizadas y pendientes

Se realizaron pruebas locales de validación y solicitudes con claves ficticias para ambos proveedores. Las solicitudes mostraron `AuthenticationError` controlado en modo completo y streaming, y el programa continuó hasta finalizar.

Para repetir la prueba de autenticación, colocar `clave-ficticia-para-probar` en la variable de clave del proveedor elegido y ejecutar `python main.py`. Requiere conexión con la API. Si hay un problema de red, puede aparecer un error de conexión en lugar de autenticación.

Para probar la validación, cambiar temporalmente `LLM_TEMPERATURE` a `3` y ejecutar el script. Debe informar configuración inválida sin realizar consultas. Luego restaurar el valor a `0.7`.

Durante la revisión del código también se comprobaron con SDKs simulados las respuestas exitosas, la iteración del streaming, los errores de conexión y cuota, y el cierre de recursos. Estas comprobaciones no sustituyen una prueba de integración con los proveedores.

La generación exitosa y la recepción de fragmentos reales de OpenAI y Anthropic quedan pendientes de prueba con claves válidas y cuota disponible.
