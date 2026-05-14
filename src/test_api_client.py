import requests


BASE_URL = "http://127.0.0.1:8000"


TEST_CASES = [
    {
        "id": "api_calc_001",
        "task": "calculate 23 * 17 and explain the result",
        "expected_tools": ["calculator"],
        "expected_keywords": ["391"]
    },
    {
        "id": "api_rag_001",
        "task": "what is RAG? Use the local knowledge base to answer.",
        "expected_tools": ["rag"],
        "expected_keywords": ["Retrieval-Augmented Generation", "knowledge base", "retriever", "generator"]
    },
    {
        "id": "api_file_001",
        "task": "read data/knowledge.txt and summarize the difference between RAG and Agent",
        "expected_tools": ["file_reader", "llm"],
        "expected_keywords": ["RAG", "knowledge base", "Agent", "tools", "planning"]
    }
]


def test_health():
    url = f"{BASE_URL}/health"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    print("Health check:")
    print(data)

    assert data["status"] == "ok"


def run_agent(task):
    url = f"{BASE_URL}/agent/run"

    payload = {
        "task": task,
        "max_steps": 5,
        "max_retries": 2
    }

    response = requests.post(url, json=payload, timeout=180)
    response.raise_for_status()

    return response.json()


def check_expected_tools(history, expected_tools):
    actual_tools = [item.get("tool") for item in history]

    for expected_tool in expected_tools:
        if expected_tool not in actual_tools:
            return False, actual_tools

    return True, actual_tools


def check_expected_keywords(final_answer, expected_keywords):
    lower_answer = final_answer.lower()
    missing_keywords = []

    for keyword in expected_keywords:
        if keyword.lower() not in lower_answer:
            missing_keywords.append(keyword)

    return len(missing_keywords) == 0, missing_keywords


def test_agent_case(case):
    data = run_agent(case["task"])

    final_answer = data.get("final_answer", "")
    history = data.get("history", [])
    meta = data.get("meta", {})

    print("\n" + "=" * 80)
    print(f"Case ID: {case['id']}")
    print(f"Task: {case['task']}")

    print("\nFinal answer:")
    print(final_answer)

    print("\nMeta:")
    print(meta)

    print("\nHistory:")
    for item in history:
        print(f"Step {item.get('step')} | Tool: {item.get('tool')}")
        print(f"Arguments: {item.get('arguments')}")
        print(f"Result: {str(item.get('result'))[:300]}")

    tools_pass, actual_tools = check_expected_tools(
        history=history,
        expected_tools=case["expected_tools"]
    )

    keywords_pass, missing_keywords = check_expected_keywords(
        final_answer=final_answer,
        expected_keywords=case["expected_keywords"]
    )

    print("\nCheck result:")
    print(f"Expected tools: {case['expected_tools']}")
    print(f"Actual tools:   {actual_tools}")
    print(f"Tools pass:     {tools_pass}")
    print(f"Keywords pass:  {keywords_pass}")

    if missing_keywords:
        print(f"Missing keywords: {missing_keywords}")

    assert "request_id" in data
    assert "final_answer" in data
    assert "history" in data
    assert "meta" in data
    assert tools_pass
    assert keywords_pass


def main():
    test_health()

    for case in TEST_CASES:
        test_agent_case(case)

    print("\n" + "=" * 80)
    print("All API quality tests passed.")


if __name__ == "__main__":
    main()