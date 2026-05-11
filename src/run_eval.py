import json
import os

from multi_step_agent import run_multi_step_agent_with_history


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL_CASES_PATH = os.path.join(PROJECT_ROOT, "tests", "eval_cases.json")
EVAL_RESULTS_PATH = os.path.join(PROJECT_ROOT, "outputs", "eval_results.json")


def load_eval_cases():
    with open(EVAL_CASES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def check_keywords(answer, expected_keywords):
    answer_lower = answer.lower()

    missing_keywords = []

    for keyword in expected_keywords:
        if keyword.lower() not in answer_lower:
            missing_keywords.append(keyword)

    return missing_keywords


def evaluate_case(case):
    question = case["question"]
    expected_first_tool = case["expected_first_tool"]
    expected_keywords = case["expected_keywords"]

    print("\n" + "=" * 80)
    print(f"Running case: {case['id']}")
    print(f"Question: {question}")

    final_answer, history = run_multi_step_agent_with_history(
        user_goal=question,
        max_steps=5,
        max_retries=2
    )

    if history:
        actual_first_tool = history[0].get("tool", "")
    else:
        actual_first_tool = ""

    tool_pass = actual_first_tool == expected_first_tool

    missing_keywords = check_keywords(final_answer, expected_keywords)
    keyword_pass = len(missing_keywords) == 0

    final_pass = tool_pass and keyword_pass

    result = {
        "id": case["id"],
        "question": question,
        "expected_first_tool": expected_first_tool,
        "actual_first_tool": actual_first_tool,
        "tool_pass": tool_pass,
        "expected_keywords": expected_keywords,
        "missing_keywords": missing_keywords,
        "keyword_pass": keyword_pass,
        "final_pass": final_pass,
        "final_answer": final_answer,
        "history": history
    }

    print(f"Expected first tool: {expected_first_tool}")
    print(f"Actual first tool: {actual_first_tool}")
    print(f"Tool pass: {tool_pass}")
    print(f"Keyword pass: {keyword_pass}")
    print(f"Final pass: {final_pass}")
    print(f"Final answer: {final_answer}")

    if missing_keywords:
        print(f"Missing keywords: {missing_keywords}")

    return result


def save_eval_results(results):
    os.makedirs(os.path.dirname(EVAL_RESULTS_PATH), exist_ok=True)

    summary = {
        "total_cases": len(results),
        "passed_cases": sum(1 for item in results if item["final_pass"]),
        "tool_pass_cases": sum(1 for item in results if item["tool_pass"]),
        "keyword_pass_cases": sum(1 for item in results if item["keyword_pass"]),
        "results": results
    }

    with open(EVAL_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return summary


def main():
    cases = load_eval_cases()

    results = []

    for case in cases:
        result = evaluate_case(case)
        results.append(result)

    summary = save_eval_results(results)

    print("\n" + "=" * 80)
    print("Evaluation Summary")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Passed cases: {summary['passed_cases']}")
    print(f"Tool pass cases: {summary['tool_pass_cases']}")
    print(f"Keyword pass cases: {summary['keyword_pass_cases']}")
    print(f"Saved results to: {EVAL_RESULTS_PATH}")


if __name__ == "__main__":
    main()