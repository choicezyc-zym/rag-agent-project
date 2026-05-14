import requests


BASE_URL = "http://127.0.0.1:8000"


def test_health():
    url = f"{BASE_URL}/health"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    print("Health check:")
    print(data)

    assert data["status"] == "ok"


def test_agent(task):
    url = f"{BASE_URL}/agent/run"

    payload = {
        "task": task,
        "max_steps": 5,
        "max_retries": 2
    }

    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()

    data = response.json()

    print("\n" + "=" * 80)
    print(f"Task: {task}")
    print("Final answer:")
    print(data.get("final_answer", ""))

    print("\nMeta:")
    print(data.get("meta", {}))

    print("\nHistory:")
    for item in data.get("history", []):
        print(f"Step {item.get('step')} | Tool: {item.get('tool')}")
        print(f"Arguments: {item.get('arguments')}")
        print(f"Result: {item.get('result')[:300]}")

    assert "final_answer" in data
    assert "history" in data
    assert "meta" in data


def main():
    test_health()

    test_agent("calculate 23 * 17 and explain the result")

    test_agent("what is RAG? Use the local knowledge base to answer.")

    test_agent("read data/knowledge.txt and summarize the difference between RAG and Agent")

    print("\n" + "=" * 80)
    print("All API tests passed.")


if __name__ == "__main__":
    main()