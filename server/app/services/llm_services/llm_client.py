import re
import json
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
import logging
logger = logging.getLogger(__name__)
from app.db.models import Customer
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import shlex
from app.services.mcp_services.tool_arguments import filter_tool_args
import httpx

from app.services.llm_services.system_promt import get_system_prompt

async def call_mcp_tool(tool_name: str, tool_args: dict):
    params = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp.mcp_server"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            # Сначала инициализация
            await session.initialize()

            # Немного подождать, чтобы тулзы успели зарегистрироваться
            import asyncio
            await asyncio.sleep(0.5)

            # Берём список тулов, чтобы убедиться, что есть нужный
            tools = await session.list_tools()
            if not any(t.name == tool_name for t in tools.tools):
                raise ValueError(f"Tool {tool_name} not found on MCP server")

            # Вызываем инструмент
            result = await session.call_tool(tool_name, tool_args)
            return result.content[0].text if result.content else None


_FUNC_RE = re.compile(r"^name=(?P<name>[^,]+)(?:\s*,\s*(?P<args>.*))?$",re.DOTALL)
_ARG_RE  = re.compile(r"\s*(?P<k>\w+)\s*=\s*(?P<v>.+?)\s*(?=,\s*\w+=|$)")
FUNC_CALL_PATTERN = re.compile(r"\[FUNC_CALL:(.*?)\]", re.DOTALL)

def _coerce_value(v: str) -> Any:
    """Пытается привести строковое значение к int/float/bool/None/JSON, иначе возвращает исходную строку."""
    s = v.strip()

    # boolean
    low = s.lower()
    if low == "true":
        return True
    if low == "false":
        return False

    # null/none
    if low in ("null", "none"):
        return None

    # integer
    if re.fullmatch(r"[+-]?\d+", s):
        try:
            return int(s)
        except Exception:
            pass

    # float
    if re.fullmatch(r"[+-]?\d+\.\d+", s):
        try:
            return float(s)
        except Exception:
            pass

    # JSON object/array
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        try:
            return json.loads(s)
        except Exception:
            pass

    # по умолчанию — как строка
    return s


def _parse_func_call(s: str) -> Tuple[str, Dict[str, Any]]:
    m = _FUNC_RE.match(s.strip())
    if not m:
        raise ValueError(f"Bad func_call format: {s}")
    name = m.group("name").strip()
    args = m.group("args") or ""
    kwargs: Dict[str, Any] = {}
    for kv in _ARG_RE.finditer(args):
        k = kv.group("k")
        v = kv.group("v")

        # снять внешние кавычки, если есть
        if (len(v) >= 2) and ((v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'"))):
            v = v[1:-1]

        kwargs[k] = _coerce_value(v)

    return name, kwargs


class PromptBuilder:

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

    async def respond(self, message: str, *, language: Optional[str] = None, user: Optional[Customer] = None ) -> Dict[str, Any]:
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
        logger.info("Full response text: %s", full_text)
        func_calls = self._extract_func_calls(full_text)
        if not func_calls:
            return {full_text}

        results: List[str] = []
        for fc in func_calls:
            try:
                name, kwargs = _parse_func_call(fc)
                if user and "customer_id" not in kwargs:
                    kwargs["customer_id"] = user.id
                if "lang" not in kwargs:
                    kwargs["lang"] = language or self.default_language
                kwargs = filter_tool_args(name, kwargs)
                logger.info("Calling MCP tool: %s with args: %s", name, kwargs)
                output = await call_mcp_tool(name, kwargs)
                results.append(output)
            except Exception as e:
                results.append(f"[ERROR calling {fc}: {e}]")

        return {
            "text": "\n".join(results) if results else full_text,
            "func_calls": func_calls,
        }

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
        logger.info("LLM request payload: %s", json.dumps(payload, ensure_ascii=False, indent=2))

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


def build_llm_client() -> AitilLLMClient:
    return AitilLLMClient(
        llm_url="https://chat.aitil.kg/suroo",
        model="aitil",
        temperature=0.5,
        default_language="ky",
        request_timeout=None,
    )
