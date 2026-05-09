# RAG Agent Project

A local **RAG + Multi-step AI Agent Web App** built with Python, Ollama, Qwen2.5, Sentence Transformers, Streamlit, and JSON tool calling.

This project combines three core ideas:

```text
RAG provides local knowledge.
Agent selects and uses tools.
Streamlit provides a simple web interface.
```

The system can answer questions using a local knowledge base, call tools such as a calculator or file reader, and show each Agent execution step in a web UI.

---

## Project Goal

The goal of this project is to understand how a local RAG system can be combined with an AI Agent and upgraded into a simple web application.

The project started as a command-line RAG Agent. It was later upgraded into a basic multi-step Agent and then into a Streamlit web app.

Core idea:

```text
LLM plans.
Python executes.
History stores observations.
Final stops the loop.
```

---

## Main Features

- Local knowledge base question answering
- Text chunking and embedding generation
- Semantic retrieval with cosine similarity
- RAG pipeline wrapped as a callable tool
- JSON-based tool calling
- Python tool execution
- Single-step Agent
- Multi-step Agent loop
- Tool execution history tracking
- Streamlit web interface
- Example task buttons
- Final answer display
- Agent step-by-step execution display
- Page session history
- Local LLM inference with Ollama and Qwen2.5

---

## Tech Stack

```text
Python
Ollama
Qwen2.5:7B
Sentence Transformers
scikit-learn
Streamlit
JSON tool calling
JSONL logging
pickle
```

---

## Project Structure

```text
rag_agent_project/
│
├── data/
│   └── knowledge.txt
│
├── outputs/
│   ├── chunks.pkl
│   ├── chunk_embeddings.pkl
│   ├── agent_history.jsonl
│   └── multi_step_history.jsonl
│
├── src/
│   ├── app.py
│   ├── build_index.py
│   ├── rag_tool.py
│   ├── tools.py
│   ├── llm.py
│   ├── agent.py
│   ├── multi_step_agent.py
│   └── utils.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## File Description

### `data/knowledge.txt`

The local knowledge base used by the RAG system.

---

### `src/build_index.py`

Builds the RAG index.

Workflow:

```text
Read knowledge.txt
↓
Split text into chunks
↓
Generate embeddings
↓
Save chunks and embeddings to outputs/
```

Generated files:

```text
outputs/chunks.pkl
outputs/chunk_embeddings.pkl
```

---

### `src/rag_tool.py`

Defines the RAG tool.

The RAG tool:

```text
Loads local chunks and embeddings
↓
Converts the user query into an embedding
↓
Computes cosine similarity
↓
Retrieves relevant chunks
↓
Sends retrieved context to Qwen2.5
↓
Generates an answer based on local knowledge
```

The embedding model and RAG index use lazy loading, so they are loaded only once during runtime.

---

### `src/tools.py`

Defines basic tools that the Agent can call.

Current tools:

```text
calculator_tool
file_reader_tool
```

The calculator tool handles simple mathematical expressions. The file reader tool reads local text files.

---

### `src/llm.py`

Wraps the local LLM call.

It uses Ollama to call Qwen2.5 locally.

---

### `src/agent.py`

The single-step Agent.

Workflow:

```text
User input
↓
LLM generates a JSON tool call plan
↓
Python parses the JSON
↓
Python executes one selected tool
↓
Tool result is returned
↓
Execution history is saved
```

Supported tools:

```text
calculator
file_reader
rag
llm
```

---

### `src/multi_step_agent.py`

The multi-step Agent.

It can complete a task through multiple rounds of planning, tool execution, observation, and final answer generation.

Workflow:

```text
User goal
↓
LLM generates the next JSON tool plan
↓
Python parses and executes the selected tool
↓
Tool result is saved into history
↓
LLM uses history to decide the next step
↓
The loop stops when tool = final
```

Key components:

```text
Tool registry
JSON tool plan
History
max_steps
final stop signal
```

The `final` signal is not a real tool. It tells the Agent loop to stop and return the final answer.

---

### `src/app.py`

The Streamlit web app.

It provides a simple web interface for the multi-step RAG Agent.

The web app supports:

- User task input
- Example task buttons
- Max step control
- Final answer display
- Agent execution step display
- Tool input and tool result display
- Page session history
- Clear page history button

---

### `src/utils.py`

Utility functions for saving and loading pickle files.

---

## Supported Tools

### 1. Calculator Tool

Used for mathematical calculation.

Example:

```text
calculate 23 * 17 and explain the result
```

Expected tool:

```text
calculator
```

---

### 2. File Reader Tool

Used for reading local text files.

Example:

```text
read data/knowledge.txt and summarize the difference between RAG and Agent
```

Expected tool:

```text
file_reader
```

---

### 3. RAG Tool

Used for answering questions based on the local knowledge base.

Example:

```text
what is RAG? Use the local knowledge base to answer.
```

Expected tool:

```text
rag
```

---

### 4. LLM Tool

Used for general questions that do not require local knowledge retrieval.

Example:

```text
Give me one sentence to encourage AI learning.
```

Expected tool:

```text
llm
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/choicezyc-zym/rag-agent-project.git
cd rag-agent-project
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install and run Ollama

Make sure Ollama is installed and running locally.

### 4. Pull Qwen2.5

```bash
ollama pull qwen2.5:7b
```

---

## Requirements

The `requirements.txt` file should include:

```txt
sentence-transformers
scikit-learn
requests
numpy
streamlit
```

---

## How to Run

### Step 1: Build the RAG index

Run this command from the project root:

```bash
python src/build_index.py
```

This will generate:

```text
outputs/chunks.pkl
outputs/chunk_embeddings.pkl
```

---

### Step 2: Run the single-step Agent

```bash
python src/agent.py
```

---

### Step 3: Run the multi-step Agent in command line

```bash
python src/multi_step_agent.py
```

---

### Step 4: Run the Streamlit Web App

```bash
streamlit run src/app.py
```

Then open the local Streamlit URL in your browser.

The web app allows you to enter a task, run the Agent, view the final answer, and inspect each tool execution step.

---

## Example Tasks

### Calculator

```text
calculate 23 * 17 and explain the result
```

Expected behavior:

```text
Step 1 | Tool: calculator
Final Answer: 23 * 17 = 391
```

---

### RAG Question Answering

```text
what is RAG? Use the local knowledge base to answer.
```

Expected behavior:

```text
Step 1 | Tool: rag
Final Answer: Answer based on retrieved local knowledge
```

---

### File Reading and Summarization

```text
read data/knowledge.txt and summarize the difference between RAG and Agent
```

Expected behavior:

```text
Step 1 | Tool: file_reader
Final Answer: Summary based on the file content
```

---

## Streamlit Web App

The web app turns the command-line Agent into a simple product-style interface.

It includes:

```text
Input box
Run Agent button
Example buttons
Max steps slider
Final answer area
Agent execution steps
Page run history
Clear history button
```

This makes the project easier to demonstrate and closer to a real AI application.

---

## Execution History

Single-step Agent history is saved in:

```text
outputs/agent_history.jsonl
```

Multi-step Agent history is saved in:

```text
outputs/multi_step_history.jsonl
```

Each record can be used for:

- Debugging
- Checking tool selection
- Reviewing Agent behavior
- Analyzing execution results

---

## What I Learned

Through this project, I learned:

- How to combine RAG and Agent systems
- How to wrap a RAG pipeline as a callable tool
- How to use an LLM for tool planning
- How to use JSON as a structured tool call format
- How to let Python execute tools based on LLM-generated plans
- How to use Sentence Transformers for semantic retrieval
- How to use cosine similarity for chunk retrieval
- How to call Qwen2.5 locally with Ollama
- How to log Agent execution history using JSONL
- How to build a basic multi-step Agent loop
- How to use history, `max_steps`, and `final` to control multi-step execution
- How to build a simple Streamlit web interface for an AI Agent

---

## Difference From Previous Projects

### Compared with `mini_rag_project`

`mini_rag_project` focuses on local knowledge-based question answering.

```text
User question
↓
Retrieve relevant chunks
↓
Generate answer with LLM
```

### Compared with `mini_agent_project`

`mini_agent_project` focuses on basic tool calling.

```text
User task
↓
LLM selects a tool
↓
Python executes the tool
```

### This Project

`rag_agent_project` combines both ideas and adds a web interface.

```text
User task
↓
Agent selects calculator / file_reader / rag / llm
↓
Python executes the selected tool
↓
History stores the result
↓
Streamlit displays final answer and execution steps
```

The key improvement is:

```text
RAG becomes one of the Agent's tools, and the Agent workflow can be displayed in a web app.
```

---

## Limitations

Current limitations:

- The knowledge base is still small
- The Agent only supports a few tools
- JSON parsing fallback is simple
- The multi-step Agent is still basic
- Final answer formatting may sometimes need improvement
- No vector database integration yet
- No deployed online version yet

---

## Future Improvements

Possible future improvements:

- Improve JSON retry and self-correction
- Add more tools such as time, todo, web search, or database query
- Replace pickle files with a vector database such as FAISS or Chroma
- Add conversation memory
- Improve tool routing accuracy
- Support larger local knowledge bases
- Improve multi-step planning for more complex tasks
- Add file upload support in the Streamlit app
- Deploy the web app online

---

## Final Summary

This project is a local RAG + Multi-step AI Agent Web App.

It combines semantic retrieval, local LLM generation, JSON tool calling, Python tool execution, execution logging, multi-step Agent planning, and a Streamlit web interface.

The main idea is:

```text
The Agent decides what to do.
The RAG tool provides local knowledge.
Python executes the selected tool.
History stores previous tool results.
Streamlit displays the workflow.
Final stops the multi-step loop.
```

This project helped me understand how modern AI applications combine models, knowledge bases, tools, memory, logging, and user interfaces into one system.
