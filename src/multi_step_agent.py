import json
import os
import re
from datetime import datetime

from llm import ask_llm
from tools import calculator_tool, file_reader_tool
from rag_tool import rag_tool


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")
MULTI_STEP_HISTORY_PATH = os.path.join(OUTPUT_DIR, "multi_step_history.jsonl")


TOOLS = {
    "calculator": calculator_tool,
    "file_reader": file_reader_tool,
    "rag": rag_tool,
    "llm": ask_llm,
}


TOOL_SCHEMAS = {
    "calculator": {
        "description": "Use this tool when the task requires mathematical calculation.",
        "required": {
            "expression": str
        }
    },
    "file_reader": {
        "description": "Use this tool when the user asks to read a local text file.",
        "required": {
            "path": str
        }
    },
    "rag": {
        "description": "Use this tool when the user asks questions that should be answered from the local knowledge base.",
        "required": {
            "query": str
        }
    },
    "llm": {
        "description": "Use this tool for general language tasks that do not require calculator, file reading, or RAG.",
        "required": {
            "prompt": str
        }
    },
    "final": {
        "description": "Use this tool when enough information has been collected and the task can be answered.",
        "required": {
            "answer": str
        }
    }
}


def save_history_record(user_goal, history, final_answer):
    """
    Save one multi-step agent execution record to outputs/multi_step_history.jsonl.
    The path is based on the project root, not the current working directory.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    record = {
        "timestamp": datetime.now().isoformat(),
        "user_goal": user_goal,
        "history": history,
        "final_answer": final_answer
    }

    with open(MULTI_STEP_HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def extract_json(text):
    """
    Extract a JSON object from LLM output.
    Handles plain JSON and ```json code blocks.
    """
    if not text:
        return None

    cleaned = text.strip()

    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return None

    json_text = match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return None


def validate_plan(plan):
    """
    Validate whether the LLM-generated tool call follows the required schema.
    """
    if not isinstance(plan, dict):
        return False, "Plan must be a JSON object."

    tool = plan.get("tool")
    arguments = plan.get("arguments")

    if not tool:
        return False, "Missing required field: tool."

    if tool not in TOOL_SCHEMAS:
        available_tools = ", ".join(TOOL_SCHEMAS.keys())
        return False, f"Unknown tool: {tool}. Available tools: {available_tools}."

    if not isinstance(arguments, dict):
        return False, "Missing or invalid field: arguments. It must be a JSON object."

    required_args = TOOL_SCHEMAS[tool]["required"]

    for arg_name, arg_type in required_args.items():
        if arg_name not in arguments:
            return False, f"Missing required argument: {arg_name}."

        if not isinstance(arguments[arg_name], arg_type):
            return False, f"Argument '{arg_name}' must be {arg_type.__name__}."

        if isinstance(arguments[arg_name], str) and not arguments[arg_name].strip():
            return False, f"Argument '{arg_name}' cannot be empty."

    return True, "OK"


def run_tool(tool_name, arguments):
    """
    Run a tool using structured arguments.
    """
    try:
        if tool_name == "calculator":
            return calculator_tool(arguments["expression"])

        if tool_name == "file_reader":
            return file_reader_tool(arguments["path"])

        if tool_name == "rag":
            return rag_tool(arguments["query"])

        if tool_name == "llm":
            return ask_llm(arguments["prompt"])

        return f"Error: unknown tool '{tool_name}'."

    except Exception as e:
        return f"Error while running tool '{tool_name}': {e}"


def build_tool_schema_text():
    """
    Convert tool schemas into prompt-friendly text.
    """
    lines = []

    for tool_name, schema in TOOL_SCHEMAS.items():
        required = schema["required"]
        arg_lines = []

        for arg_name, arg_type in required.items():
            arg_lines.append(f"- {arg_name}: {arg_type.__name__}")

        lines.append(
            f"Tool: {tool_name}\n"
            f"Description: {schema['description']}\n"
            f"Required arguments:\n" + "\n".join(arg_lines)
        )

    return "\n\n".join(lines)


def build_agent_prompt(user_goal, history):
    """
    Build the main planning prompt for the multi-step agent.
    """
    tool_schema_text = build_tool_schema_text()

    history_text = json.dumps(history, ensure_ascii=False, indent=2)

    prompt = f"""
You are a local multi-step AI Agent.

Your job:
- Understand the user's goal.
- Choose exactly one tool for the next step.
- Output valid JSON only.
- Do not use markdown.
- Do not add explanations outside JSON.

User goal:
{user_goal}

Execution history:
{history_text}

Available tools and schemas:
{tool_schema_text}

Important rules:
1. Output exactly one JSON object.
2. Use the field "tool" to choose one tool.
3. Use the field "arguments" to provide structured arguments.
4. Do not use the old "input" field.
5. Choose only one tool per step.
6. If the task requires calculation, use "calculator".
7. If the task requires reading a local file, use "file_reader".
8. If the task requires local knowledge base information, use "rag".
9. If the task is general language work and does not require tools, use "llm".
10. If the history already contains enough information to answer the user, use "final".
11. When using "final", the answer must be in arguments.answer.
12. The final answer must be based on the history and tool results.
13. Do not invent unsupported information.
14. Do not use the llm tool to summarize previous tool results. If the answer can be written from history, use final directly.

Required output format:
{{
  "thought": "Briefly explain why this next step is needed.",
  "tool": "calculator | file_reader | rag | llm | final",
  "arguments": {{
    "argument_name": "argument_value"
  }}
}}

Examples:

Calculator:
{{
  "thought": "The user asks for a calculation, so I should use the calculator tool.",
  "tool": "calculator",
  "arguments": {{
    "expression": "23 * 17"
  }}
}}

File reader:
{{
  "thought": "The user asks to read a local file, so I should use the file_reader tool.",
  "tool": "file_reader",
  "arguments": {{
    "path": "data/knowledge.txt"
  }}
}}

RAG:
{{
  "thought": "The user asks a knowledge-base question, so I should use the RAG tool.",
  "tool": "rag",
  "arguments": {{
    "query": "what is RAG?"
  }}
}}

Final:
{{
  "thought": "The history contains enough information to answer the user.",
  "tool": "final",
  "arguments": {{
    "answer": "RAG means Retrieval-Augmented Generation. It retrieves relevant information from a knowledge base before generating an answer."
  }}
}}
""".strip()

    return prompt


def build_retry_prompt(original_prompt, invalid_output, error_message):
    """
    Build a retry prompt when validation fails.
    """
    retry_prompt = f"""
Your previous tool call was invalid.

Validation error:
{error_message}

Your previous output:
{invalid_output}

You must fix the tool call.

Return valid JSON only.
Do not use markdown.
Do not add explanations outside JSON.
Do not use the old "input" field.
Use "arguments" with the correct required fields.

Original task and rules:
{original_prompt}
""".strip()

    return retry_prompt


def get_valid_plan(prompt, max_retries=2):
    """
    Ask the LLM for a tool call plan.
    If parsing or validation fails, retry a limited number of times.
    """
    current_prompt = prompt
    last_error = ""

    for attempt in range(max_retries + 1):
        raw_output = ask_llm(current_prompt)

        print(f"\n--- LLM Raw Output Attempt {attempt + 1} ---")
        print(raw_output)

        plan = extract_json(raw_output)

        if plan is None:
            last_error = "Failed to parse JSON."
            current_prompt = build_retry_prompt(
                original_prompt=prompt,
                invalid_output=raw_output,
                error_message=last_error
            )
            continue

        is_valid, validation_message = validate_plan(plan)

        if is_valid:
            return plan, raw_output, None

        last_error = validation_message
        current_prompt = build_retry_prompt(
            original_prompt=prompt,
            invalid_output=raw_output,
            error_message=last_error
        )

    return None, None, last_error


def run_multi_step_agent(user_goal, max_steps=5, max_retries=2):
    """
    Command-line version of the multi-step agent.
    Returns final_answer.
    """
    history = []

    for step in range(1, max_steps + 1):
        prompt = build_agent_prompt(user_goal, history)

        plan, raw_output, error = get_valid_plan(prompt, max_retries=max_retries)

        if plan is None:
            final_answer = f"Agent failed to generate a valid tool call. Error: {error}"
            save_history_record(user_goal, history, final_answer)
            return final_answer

        thought = plan.get("thought", "")
        tool_name = plan.get("tool", "")
        arguments = plan.get("arguments", {})

        print(f"\nStep {step}")
        print(f"Thought: {thought}")
        print(f"Tool: {tool_name}")
        print(f"Arguments: {arguments}")

        if tool_name == "final":
            final_answer = arguments["answer"].strip()
            save_history_record(user_goal, history, final_answer)
            return final_answer

        tool_result = run_tool(tool_name, arguments)

        print(f"Result: {tool_result}")

        history.append({
            "step": step,
            "thought": thought,
            "tool": tool_name,
            "arguments": arguments,
            "result": str(tool_result)[:2000]
        })

    final_answer = "Agent reached max_steps before completing the task."
    save_history_record(user_goal, history, final_answer)
    return final_answer


def run_multi_step_agent_with_history(user_goal, max_steps=5, max_retries=2):
    """
    Streamlit version of the multi-step agent.
    Returns:
    - final_answer
    - history
    """
    history = []

    for step in range(1, max_steps + 1):
        prompt = build_agent_prompt(user_goal, history)

        plan, raw_output, error = get_valid_plan(prompt, max_retries=max_retries)

        if plan is None:
            final_answer = f"Agent failed to generate a valid tool call. Error: {error}"
            save_history_record(user_goal, history, final_answer)
            return final_answer, history

        thought = plan.get("thought", "")
        tool_name = plan.get("tool", "")
        arguments = plan.get("arguments", {})

        print(f"\nStep {step}")
        print(f"Thought: {thought}")
        print(f"Tool: {tool_name}")
        print(f"Arguments: {arguments}")

        if tool_name == "final":
            final_answer = arguments["answer"].strip()
            save_history_record(user_goal, history, final_answer)
            return final_answer, history

        tool_result = run_tool(tool_name, arguments)

        print(f"Result: {tool_result}")

        history.append({
            "step": step,
            "thought": thought,
            "tool": tool_name,
            "arguments": arguments,
            "result": str(tool_result)[:2000]
        })

    final_answer = "Agent reached max_steps before completing the task."
    save_history_record(user_goal, history, final_answer)
    return final_answer, history


def main():
    print("Local RAG + Multi-step Agent V2")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_goal = input("User goal: ").strip()

        if user_goal.lower() in ["exit", "quit"]:
            break

        if not user_goal:
            continue

        final_answer = run_multi_step_agent(user_goal)

        print("\nFinal Answer:")
        print(final_answer)
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()