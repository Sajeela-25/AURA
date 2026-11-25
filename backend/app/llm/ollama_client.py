
import httpx
from ollama import chat, ResponseError


# Local Ollama model
MODEL_NAME = "qwen2.5:7b"


def generate_response(
    system_prompt: str,
    user_prompt: str,
    model: str = MODEL_NAME
) -> str:
    """
    Generate a response using a locally running Ollama model.

    Args:
        system_prompt: Instructions that control model behaviour.
        user_prompt: The user's question and relevant context.
        model: Name of the Ollama model.

    Returns:
        Generated response as a string.
    """

    if not system_prompt.strip():
        raise ValueError("System prompt cannot be empty.")

    if not user_prompt.strip():
        raise ValueError("User prompt cannot be empty.")

    try:
        response = chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            stream=False,
            options={
                "temperature": 0,
                "seed": 42
            }
        )

        return response.message.content.strip()

    except httpx.ConnectError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. "
            "Make sure the Ollama application is running."
        ) from error

    except ResponseError as error:
        raise RuntimeError(
            f"Ollama model error: {error}"
        ) from error
