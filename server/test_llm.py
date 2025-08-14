# test_llm_stream.py
import httpx, json

URL = "https://chat.aitil.kg/suroo"
payload = {
    "model": "aitil",
    "messages": [
        {"role": "system", "content": "КАЙСЫ ТИЛДЕ СУРОО БЕРИЛСЕ ОШОЛ ТИЛДЕ ЖООП БЕР М:На русском, кыргызча, english БИР ГАНА ТИЛДЕ ЖООП БЕР"},
        {"role": "user", "content": "привет как дела"}
    ],
    "temperature": 0.5,
    "max_tokens": 200,
    "stream": True
}
headers = {"Accept": "text/event-stream", "Content-Type": "application/json"}

with httpx.stream("POST", URL, json=payload, headers=headers, timeout=None) as r:
    r.raise_for_status()
    for line in r.iter_lines():
        if not line:  # пропускаем пустые keep-alive строки
            continue
        if line.startswith("data:"):
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                print("\n--- конец ---")
                break
            try:
                obj = json.loads(data)
                chunk = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if chunk:
                    print(chunk, end="", flush=True)
            except json.JSONDecodeError:
                # иногда приходят служебные события — игнорим
                pass
