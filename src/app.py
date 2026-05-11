import streamlit as st
import json
from multi_step_agent import run_multi_step_agent_with_history


st.set_page_config(
    page_title="Personal AI Knowledge Assistant",
    page_icon="🤖",
    layout="wide"
)


if "runs" not in st.session_state:
    st.session_state["runs"] = []

if "user_goal" not in st.session_state:
    st.session_state["user_goal"] = ""


EXAMPLES = {
    "Calculation": "calculate 23 * 17 and explain the result",
    "RAG Question": "what is RAG? Use the local knowledge base to answer.",
    "File Reading": "read data/knowledge.txt and summarize the difference between RAG and Agent",
}


with st.sidebar:
    st.title("Agent Control Panel")

    st.markdown("### Available Tools")
    st.write("- calculator")
    st.write("- file_reader")
    st.write("- rag")
    st.write("- llm")

    st.markdown("### Example Tasks")

    for label, example in EXAMPLES.items():
        if st.button(label):
            st.session_state["user_goal"] = example

    st.markdown("### Settings")

    max_steps = st.slider(
        label="Max agent steps",
        min_value=1,
        max_value=10,
        value=5
    )

    if st.button("Clear Page History"):
        st.session_state["runs"] = []
        st.session_state["user_goal"] = ""
        st.rerun()


st.title("Personal AI Knowledge Assistant")

st.caption(
    "A local RAG + Multi-step AI Agent Web App powered by Ollama, Qwen2.5, Streamlit, and Python tools."
)

st.info(
    "Core workflow: LLM plans → Python executes tools → History stores observations → Final answer stops the loop"
)

st.divider()


user_goal = st.text_area(
    label="Enter your question or task:",
    key="user_goal",
    placeholder="Example: what is RAG? Use the local knowledge base to answer.",
    height=120
)

run_button = st.button("Run Agent", type="primary")


if run_button:
    if not st.session_state["user_goal"].strip():
        st.warning("Please enter a question or task first.")
    else:
        with st.spinner("Agent is planning and using tools..."):
            final_answer, history = run_multi_step_agent_with_history(
                user_goal=st.session_state["user_goal"],
                max_steps=max_steps
            )

        st.session_state["runs"].insert(
            0,
            {
                "user_goal": st.session_state["user_goal"],
                "final_answer": final_answer,
                "history": history
            }
        )


if st.session_state["runs"]:
    latest_run = st.session_state["runs"][0]

    st.subheader("Latest Final Answer")
    st.write(latest_run["final_answer"])

    st.subheader("Latest Agent Execution Steps")

    latest_history = latest_run["history"]

    if not latest_history:
        st.info("No tool execution steps were recorded. The Agent may have answered directly.")
    else:
        for item in latest_history:
            step = item.get("step", "")
            tool = item.get("tool", "")
            thought = item.get("thought", "")
            arguments = item.get("arguments", {})
            result = item.get("result", "")

            with st.expander(f"Step {step} | Tool: {tool}", expanded=True):
                st.markdown("**Thought**")
                st.write(thought)

                st.markdown("**Tool Argument**")
                st.code(json.dumps(arguments, ensure_ascii=False, indent=2), language="json")

                st.markdown("**Tool Result**")
                st.code(str(result), language="text")

    st.divider()

    st.subheader("Page Run History")

    for index, run in enumerate(st.session_state["runs"], start=1):
        with st.expander(f"Run {index}: {run['user_goal'][:80]}"):
            st.markdown("**User Goal**")
            st.write(run["user_goal"])

            st.markdown("**Final Answer**")
            st.write(run["final_answer"])

            st.markdown("**Tools Used**")
            tools_used = [item.get("tool", "") for item in run["history"]]

            if tools_used:
                st.write(" → ".join(tools_used))
            else:
                st.write("No tools recorded.")
else:
    st.subheader("How to use")
    st.write("1. Enter a task in the text box.")
    st.write("2. Click Run Agent.")
    st.write("3. Check the final answer and each tool execution step.")
    st.write("4. Use the sidebar examples to quickly test calculator, RAG, and file_reader.")