# create_structure.py
import os

structure = [
    "requirements.txt",
    ".env.example",
    "app/__init__.py",
    "app/main.py",
    "app/settings.py",
    "app/api/__init__.py",
    "app/api/deps.py",
    "app/api/routers/__init__.py",
    "app/api/routers/health.py",
    "app/api/routers/chat.py",
    "app/mcp/__init__.py",
    "app/mcp/server.py",
    "app/mcp/tools/__init__.py",
    "app/mcp/tools/ask_llm.py",
    "app/mcp/tools/search_kb.py",
    "app/db/__init__.py",
    "app/db/base.py",
    "app/db/models.py",
    "app/db/repositories.py",
    "app/services/__init__.py",
    "app/services/chat_service.py",
    "app/services/kb_service.py",
    "app/schemas/__init__.py",
    "app/schemas/chat.py",
    "app/schemas/common.py",
    "tests/__init__.py",
    "tests/test_chat.py",
]

for path in structure:
    dir_path = os.path.dirname(path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            pass

print("✅ Проектная структура создана.")