import re
import json
from typing import Any, AsyncGenerator, Dict, List, Optional
import logging
logger = logging.getLogger(__name__)
from app.db.models import Customer

import httpx

# System prompt is authoritative and already includes tools. DO NOT modify it.
from app.services.llm_services.system_promt import get_system_prompt


FUNC_CALL_PATTERN = re.compile(r"\[FUNC_CALL:(.*?)\]", re.DOTALL)


class PromptBuilder:
    """
    Minimal, strict builder per your constraints:
    - Uses *exactly* the system prompt returned by get_system_prompt(language)
    - Optionally injects a compact user profile as a separate `user` message
    - Ignores conversation history for now (as requested)
    - Leaves tools entirely to the system prompt (no extra sections)
    """

    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt

    @staticmethod
    def _render_user_profile(user: "Customer") -> str:
        """Render compact profile for Customer model."""
        try:

            return (
                f"Профиль:\n"
                f"- username: {user.first_name}\n"
                f"- ID: {user.id}\n"
            )
        except Exception as e:
            logger.error("Failed to render user profile: %s", e)
            return "Профиль: белгилүү эмес"


    def build(
        self,
        *,
        user_message: str,
        user: Optional[Customer] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,  # intentionally unused
    ) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = []
        # System — use string content exactly as API expects
        messages.append({"role": "system", "content": self.system_prompt})

        # Optional profile as a separate `user` turn (cheap personalization for the model)
        if user is not None:
            profile = self._render_user_profile(user)
            messages.append({"role": "user", "content": profile})

        # Current user message
        messages.append({"role": "user", "content": user_message})
        return messages


class AitilLLMClient:
    """Async client that:
    - Builds messages with PromptBuilder (no DB history yet)
    - Streams SSE tokens
    - Aggregates full answer and extracts [FUNC_CALL:{...}] markers (no execution yet)
    """

    def __init__(
        self,
        *,
        llm_url: str = "https://chat.aitil.kg/suroo",
        model: str = "aitil",
        temperature: float = 0.5,
        default_language: str = "ky",
        request_timeout: Optional[float] = None,
    ) -> None:
        self.llm_url = llm_url
        self.model = model
        self.temperature = temperature
        self.default_language = default_language
        self.request_timeout = request_timeout

    # -------------------- Public API --------------------
    async def astream_answer(
        self,
        message: str,
        *,
        language: Optional[str] = None,
        user: Optional[Customer] = None,
    ) -> AsyncGenerator[str, None]:
        payload = self._build_payload(
            message=message,
            language=language or self.default_language,
            user=user,
            stream=True,
        )
        async for chunk in self._sse_stream(payload):
            yield chunk

    async def respond(
        self,
        message: str,
        *,
        language: Optional[str] = None,
        user: Optional[Customer] = None,
    ) -> Dict[str, Any]:
        payload = self._build_payload(
            message=message,
            language=language or self.default_language,
            user=user,
            stream=True,
        )
        parts: List[str] = []
        async for chunk in self._sse_stream(payload):
            parts.append(chunk)
        full_text = "".join(parts)
        func_calls = self._extract_func_calls(full_text)
        return {"text": full_text, "func_calls": func_calls}

    # -------------------- Internals --------------------
    def _build_payload(
        self,
        *,
        message: str,
        language: str,
        user: Optional[Customer],
        stream: bool,
    ) -> Dict[str, Any]:
        system_prompt = get_system_prompt(language)
        builder = PromptBuilder(system_prompt)
        messages = builder.build(user_message=message, user=user)

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": stream,
        }
        #logger.info("LLM request payload: %s", json.dumps(payload, ensure_ascii=False, indent=2))

        return payload


    async def _sse_stream(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        headers = {"Accept": "text/event-stream", "Content-Type": "application/json"}
        timeout = None if self.request_timeout is None else httpx.Timeout(self.request_timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", self.llm_url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[len("data:") :].strip()
                    if data == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                        chunk = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        continue

    def _extract_func_calls(self, text: str) -> List[str]:
        return [m.group(1).strip() for m in FUNC_CALL_PATTERN.finditer(text)]


# -------------------- Factory --------------------

def build_llm_client() -> AitilLLMClient:
    return AitilLLMClient(
        llm_url="https://chat.aitil.kg/suroo",
        model="aitil",
        temperature=0.5,
        default_language="ky",
        request_timeout=None,
    )
