import requests


def ask_llm(prompt: str, model_name: str = "qwen2.5:7b") -> str:
    """
    调用本地 Ollama 中的 Qwen2.5 模型。
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        return result["response"].strip()

    except Exception as e:
        return f"LLM 调用失败：{e}"


if __name__ == "__main__":
    test_prompt = "请用一句话解释什么是 AI Agent。"
    print(ask_llm(test_prompt))