import streamlit as st

from multi_step_agent import run_multi_step_agent_with_history


st.set_page_config(
    page_title="Personal AI Knowledge Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("Personal AI Knowledge Assistant")
st.caption("Local RAG + Multi-step AI Agent powered by Ollama, Qwen2.5 and Python tools.")

st.write("Workflow: LLM plans → Python executes tools → History stores observations → Final answer stops the loop")

with st.sidebar:
    st.header("Available Tools")
    st.write("- calculator")
    st.write("- file_reader")
    st.write("- rag")
    st.write("- llm")

    st.header("Example Tasks")
    st.write("1. calculate 23 * 17 and explain the result")
    st.write("2. what is RAG? Use the local knowledge base to answer.")
    st.write("3. read data/knowledge.txt and summarize the difference between RAG and Agent")

st.divider()

user_goal = st.text_area(
    label="Enter your question or task:",
    placeholder="Example: what is RAG? Use the local knowledge base to answer.",
    height=120
)

max_steps = st.slider(
    label="Max agent steps",
    min_value=1,
    max_value=10,
    value=5
)

run_button = st.button("Run Agent", type="primary")

if run_button:
    if not user_goal.strip():
        st.warning("Please enter a question or task first.")
    else:
        with st.spinner("Agent is planning and using tools..."):
            final_answer, history = run_multi_step_agent_with_history(
                user_goal=user_goal,
                max_steps=max_steps
            )

        st.subheader("Final Answer")
        st.write(final_answer)

        st.divider()

        st.subheader("Agent Execution Steps")

        if not history:
            st.info("No tool execution steps were recorded. The Agent may have answered directly.")
        else:
            for item in history:
                step = item.get("step", "")
                tool = item.get("tool", "")
                thought = item.get("thought", "")
                tool_input = item.get("input", "")
                result = item.get("result", "")

                with st.expander(f"Step {step} | Tool: {tool}", expanded=True):
                    st.markdown("**Thought**")
                    st.write(thought)

                    st.markdown("**Tool Input**")
                    st.code(str(tool_input), language="text")

                    st.markdown("**Tool Result**")
                    st.code(str(result), language="text")