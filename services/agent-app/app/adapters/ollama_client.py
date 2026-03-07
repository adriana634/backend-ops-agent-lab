import logging
import httpx

from httpx import ReadTimeout

logger = logging.getLogger(__name__)

class OllamaTimeout(Exception):
    """Raised when a request to Ollama times out."""

class OllamaClient:
    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def answer(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }

        logger.info("Calling Ollama model=%s", self._model)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self._base_url}/chat", json=payload)
                if response.status_code >= 300:
                    logger.error(
                        "Ollama returned non-2xx status=%s model=%s",
                        response.status_code,
                        self._model,
                    )
                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content", "")
                logger.info("Ollama call success model=%s output_len=%d", self._model, len(content))
                return content
        except ReadTimeout:
            logger.exception("Ollama request timed out for model=%s", self._model)
            raise OllamaTimeout()
        except Exception:
            logger.exception("Ollama request failed for model=%s", self._model)
            raise
