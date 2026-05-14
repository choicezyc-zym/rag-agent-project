import json
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/agent/run"


st.set_page_config(
    page_title="Local RAG Agent Web App",
    page_icon="🤖",
    layout="wide"
)


st.title("🤖 Local RAG + Multi-step AI Agent")
st.caption("Streamlit frontend calling FastAPI backend")


if "api_history" not in st.session_state:
    st.session_state.api_history = []


with st.sidebar:
    st.header("Settings")

    max_steps = st.slider(
        "Max Agent Steps",
        min_value=1,
        max_value=10,
        value=5
    )

    max_retries = st.slider(
        "Max Retries",
        min_value=0,
        max_value=5,
        value=2
    )

    st.divider()

    st.header("Example Tasks")

    example_calc = "calculate 23 * 17 and explain the result"
    example_rag = "what is RAG? Use the local knowledge base to answer."
    example_file = "read data/knowledge.txt and summarize the difference between RAG and Agent"
    example_llm = "Rewrite this sentence in a more professional tone: I made an AI project."

    if st.button("Calculation Example"):
        st.session_state.current_task = example_calc

    if st.button("RAG Example"):
        st.session_state.current_task = example_rag

    if st.button("File Reading Example"):
        st.session_state.current_task = example_file

    if st.button("LLM Rewrite Example"):
        st.session_state.current_task = example_llm

    st.divider()

    if st.button("Clear Page History"):
        st.session_state.api_history = []
        st.success("Page history cleared.")


default_task = st.session_state.get("current_task", "")

task = st.text_area(
    "Enter your task",
    value=default_task,
    height=120,
    placeholder="Example: what is RAG? Use the local knowledge base to answer."
)


run_button = st.button("Run Agent", type="primary")


def call_agent_api(user_task, max_steps_value, max_retries_value):
    payload = {
        "task": user_task,
        "max_steps": max_steps_value,
        "max_retries": max_retries_value
    }

    response = requests.post(API_URL, json=payload, timeout=120)

    response.raise_for_status()

    return response.json()


if run_button:
    if not task.strip():
        st.warning("Please enter a task.")
    else:
        with st.spinner("Calling FastAPI backend and running Agent..."):
            try:
                result = call_agent_api(
                    user_task=task,
                    max_steps_value=max_steps,
                    max_retries_value=max_retries
                )

                st.session_state.api_history.append({
                    "task": task,
                    "result": result
                })

                st.success("Agent finished successfully.")

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to FastAPI backend. "
                    "Please make sure the API server is running at http://127.0.0.1:8000"
                )

            except requests.exceptions.Timeout:
                st.error("The API request timed out. The Agent may be taking too long.")

            except requests.exceptions.HTTPError as e:
                st.error(f"API returned an error: {e}")

            except Exception as e:
                st.error(f"Unexpected error: {e}")


if st.session_state.api_history:
    latest = st.session_state.api_history[-1]
    latest_result = latest["result"]

    st.divider()

    st.subheader("Final Answer")
    st.write(latest_result.get("final_answer", ""))

    st.subheader("Meta")
    st.json(latest_result.get("meta", {}))

    st.subheader("Agent Execution Steps")

    history = latest_result.get("history", [])

    if not history:
        st.info("No tool execution history returned.")
    else:
        for item in history:
            step = item.get("step", "")
            tool = item.get("tool", "")
            thought = item.get("thought", "")
            arguments = item.get("arguments", {})
            tool_result = item.get("result", "")

            with st.expander(f"Step {step} | Tool: {tool}", expanded=True):
                st.markdown("**Thought**")
                st.write(thought)

                st.markdown("**Tool Arguments**")
                st.code(
                    json.dumps(arguments, ensure_ascii=False, indent=2),
                    language="json"
                )

                st.markdown("**Tool Result**")
                st.code(str(tool_result), language="text")

    st.divider()

    st.subheader("Page Run History")

    for index, record in enumerate(reversed(st.session_state.api_history), start=1):
        with st.expander(f"Run {index}: {record['task'][:80]}"):
            st.markdown("**Task**")
            st.write(record["task"])

            st.markdown("**Final Answer**")
            st.write(record["result"].get("final_answer", ""))