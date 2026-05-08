import json
from pathlib import Path
from datetime import datetime

from llm import ask_llm
from tools import calculator_tool, file_reader_tool
from rag_tool import rag_tool


def extract_json_from_text(text: str) -> dict:
    """
    尝试从 LLM 输出中提取 JSON。
    有时模型可能会输出 ```json ... ```，所以这里做一点清理。
    """

    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except Exception:
        return {
            "tool": "llm",
            "input": text
        }


def plan_tool_call_with_llm(user_input: str) -> dict:
    """
    使用 Qwen2.5 生成工具调用计划。
    输出格式必须是 JSON：
    {
        "tool": "calculator / file_reader / rag / llm",
        "input": "工具输入"
    }
    """

    prompt = f"""
你是一个 AI Agent 的工具调用规划器。

你需要根据用户输入，选择最合适的工具。

可选工具只有四个：

1. calculator
用途：数学计算。
适合问题：
- calculate 23 * 17
- 帮我算一下 88 / 4
- 100 + 25 * 3

2. file_reader
用途：读取本地 txt 文件。
适合问题：
- read data/knowledge.txt
- 读取 data/knowledge.txt
- 打开 data/xxx.txt

3. rag
用途：回答本地知识库相关问题。
适合问题：
- what is RAG?
- what is Transformer?
- 什么是 AI Agent？
- CNN 是什么？
- 知识库中提到的内容是什么？

4. llm
用途：普通问答、解释、闲聊、不需要查本地知识库的问题。
适合问题：
- 解释一下机器学习
- 给我学习建议
- 写一段总结

要求：
你必须严格只输出 JSON。
不要输出解释。
不要输出 Markdown。
不要输出 ```json。

JSON 格式必须是：

{{
  "tool": "工具名",
  "input": "工具输入"
}}

用户输入：
{user_input}
"""

    raw_output = ask_llm(prompt).strip()

    plan = extract_json_from_text(raw_output)

    tool = plan.get("tool", "llm")
    tool_input = plan.get("input", user_input)

    allowed_tools = ["calculator", "file_reader", "rag", "llm"]

    if tool not in allowed_tools:
        tool = "llm"
        tool_input = user_input

    return {
        "tool": tool,
        "input": tool_input
    }


def save_agent_history(user_input: str, plan: dict, result: str):
    """
    保存 Agent 每一次执行记录。
    """

    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)

    history_file = output_dir / "agent_history.jsonl"

    record = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "user_input": user_input,
        "tool": plan.get("tool"),
        "tool_input": plan.get("input"),
        "result": result
    }

    with open(history_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_agent(user_input: str) -> str:
    """
    Agent 主执行函数：
    1. 让 LLM 生成工具调用计划
    2. Python 解析 JSON
    3. 调用对应工具
    4. 保存执行历史
    5. 返回结果
    """

    plan = plan_tool_call_with_llm(user_input)

    tool = plan["tool"]
    tool_input = plan["input"]

    if tool == "calculator":
        result = calculator_tool(tool_input)

    elif tool == "file_reader":
        result = file_reader_tool(tool_input)

    elif tool == "rag":
        result = rag_tool(tool_input)

    else:
        normal_prompt = f"""
请用中文清楚回答用户的问题。

用户问题：
{tool_input}
"""
        result = ask_llm(normal_prompt)

    save_agent_history(user_input, plan, result)

    final_output = (
        f"工具调用计划：\n"
        f"{json.dumps(plan, ensure_ascii=False, indent=2)}\n\n"
        f"执行结果：\n"
        f"{result}"
    )

    return final_output


def main():
    print("RAG Agent 已启动。")
    print("输入 exit / quit / q 退出。")
    print("-" * 50)

    while True:
        user_input = input("\n请输入你的问题或任务：").strip()

        if user_input.lower() in ["exit", "quit", "q"]:
            print("程序已退出。")
            break

        if not user_input:
            continue

        result = run_agent(user_input)

        print("\n" + "=" * 50)
        print(result)
        print("=" * 50)


if __name__ == "__main__":
    main()