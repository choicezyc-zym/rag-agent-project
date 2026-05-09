import json
import os
import re
from datetime import datetime

from llm import ask_llm
from tools import calculator_tool, file_reader_tool
from rag_tool import rag_tool


# =========================
# 1. Tool Registry 工具注册表
# =========================

TOOLS = {
    "calculator": calculator_tool,
    "file_reader": file_reader_tool,
    "rag": rag_tool,
    "llm": ask_llm,
}


# =========================
# 2. 工具执行函数
# =========================

def run_tool(tool_name: str, tool_input: str) -> str:
    """
    根据 tool_name 调用对应工具。
    final 不在这里执行，因为 final 是停止信号，不是真工具。
    """

    if tool_name not in TOOLS:
        return f"Error: Unknown tool '{tool_name}'. Available tools: {list(TOOLS.keys())}"

    try:
        result = TOOLS[tool_name](tool_input)
        return str(result)
    except Exception as e:
        return f"Error while running tool '{tool_name}': {str(e)}"


# =========================
# 3. 从 LLM 输出中提取 JSON
# =========================

def extract_json(text: str) -> dict:
    """
    尝试从 LLM 输出中提取 JSON。
    即使模型输出了 ```json ... ```，也尽量解析出来。
    """

    text = text.strip()

    # 去掉 markdown code block
    text = text.replace("```json", "").replace("```", "").strip()

    # 如果本身就是 JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试用正则提取第一个 {...}
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_text = match.group(0)
        return json.loads(json_text)

    raise ValueError("Could not extract valid JSON from LLM output.")


# =========================
# 4. 构建 multi-step prompt
# =========================

def build_agent_prompt(user_goal: str, history: list) -> str:
    """
    每一轮把用户目标和历史步骤发给 LLM，
    让它决定下一步调用什么工具，或者输出 final。
    """

    history_text = json.dumps(history, ensure_ascii=False, indent=2)

    prompt = f"""
You are a multi-step AI agent.

Your job is to complete the user's task step by step.

Available tools:
1. calculator
   - Use this for math calculations.
   - Input should be a math expression, for example: "23 * 17".

2. file_reader
   - Use this to read a local file.
   - Input should be a file path, for example: "data/knowledge.txt".

3. rag
   - Use this to answer questions based on the local knowledge base.
   - Input should be the user's knowledge-based question.

4. llm
   - Use this for general reasoning, summarization, rewriting, or planning.
   - Input should be a clear instruction.

5. final
   - Use this when the task is completed.
   - This is not a real tool. It means you should stop and give the final answer.

User goal:
{user_goal}

Previous steps history:
{history_text}

Rules:
- At each step, output valid JSON only.
- Do not use markdown.
- Do not add explanations outside JSON.
- Choose only one tool per step.
- Use the previous steps history carefully. The history contains tool results from earlier steps.
- If the previous history already contains enough information to answer the user, use tool = "final".
- When using tool = "final", the input must be a complete natural language answer to the user's original goal.
- The final answer must be based on the information in history.
- Do not invent information that is not supported by tool results.
- Do not say the file content is not provided if file_reader has already returned file content in history.
- Do not use the llm tool to summarize previous tool results. If you need to summarize information already in history, use final directly.
- Do not put only a raw number or raw tool result in the final answer.
- Keep the final answer concise, preferably 1 to 3 short paragraphs.
- Avoid markdown lists inside JSON strings.
- If the user asks to explain something, the final answer must include a short explanation.
- If the task requires reading a file first, use file_reader before summarizing.
- If the task requires knowledge base information, use rag.
- If the task requires calculation, use calculator.
- If the task requires summarization or rewriting based on previous tool results, use the information in history and answer with final.
- Do not wrap the final answer in extra quotation marks.
- When using tool = "final", the input must be plain natural language.
- Do not use JSON objects, dictionaries, or key-value formats inside the final answer.


Output format:
{{
  "thought": "Briefly explain why this next step is needed.",
  "tool": "calculator | file_reader | rag | llm | final",
  "input": "The input for the selected tool, or a concise final answer if tool is final. Keep this string valid JSON."
}}

"""
    return prompt


# =========================
# 5. 保存 history 到 JSONL
# =========================

def save_history_record(user_goal: str, history: list, final_answer: str):
    """
    把一次完整 multi-step 任务保存到 outputs/multi_step_history.jsonl
    """

    os.makedirs("outputs", exist_ok=True)

    record = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "user_goal": user_goal,
        "steps": history,
        "final_answer": final_answer,
    }

    with open("outputs/multi_step_history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# =========================
# 6. Multi-step Agent 主函数
# =========================

def run_multi_step_agent(user_goal: str, max_steps: int = 5) -> str:
    """
    Multi-step Agent 核心循环：
    计划 -> 执行 -> 观察 -> 记录 -> 再计划 -> final
    """

    history = []

    for step in range(1, max_steps + 1):
        print(f"\n===== Step {step} =====")

        prompt = build_agent_prompt(user_goal, history)
        llm_output = ask_llm(prompt)

        print("\nLLM raw output:")
        print(llm_output)

        try:
            plan = extract_json(llm_output)
        except Exception as e:
            final_answer = f"Agent failed to parse JSON plan: {str(e)}"
            save_history_record(user_goal, history, final_answer)
            return final_answer

        thought = plan.get("thought", "")
        tool_name = plan.get("tool", "")
        tool_input = plan.get("input", "")

        print("\nParsed plan:")
        print(f"Thought: {thought}")
        print(f"Tool: {tool_name}")
        print(f"Input: {tool_input}")

        # final 是停止信号
        if tool_name == "final":
            final_answer = tool_input
            save_history_record(user_goal, history, final_answer)
            return final_answer

        # 执行工具
        tool_result = run_tool(tool_name, tool_input)

        print("\nTool result:")
        print(tool_result)

        # 防止 history 太长，保存时可以截断显示
        history.append({
            "step": step,
            "thought": thought,
            "tool": tool_name,
            "input": tool_input,
            "result": tool_result[:2000],
        })

    final_answer = "Agent reached max_steps before completing the task."
    save_history_record(user_goal, history, final_answer)
    return final_answer


# =========================
# 7. 命令行交互
# =========================

def main():
    print("Multi-step RAG Agent started.")
    print("Type 'exit' to quit.\n")

    while True:
        user_goal = input("User goal: ").strip()

        if user_goal.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        if not user_goal:
            continue

        final_answer = run_multi_step_agent(user_goal)

        print("\n===== Final Answer =====")
        print(final_answer)
        print("========================\n")


if __name__ == "__main__":
    main()