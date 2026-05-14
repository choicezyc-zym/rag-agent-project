# Local RAG + Multi-step AI Agent Web App

A local AI application that combines **Retrieval-Augmented Generation (RAG)**, **multi-step AI Agent tool calling**, **FastAPI backend service**, **Streamlit frontend**, **structured tool arguments**, **validation**, **retry logic**, **execution history**, **request logging**, and **automatic evaluation**.

This project uses a local LLM through **Ollama + Qwen2.5**, and Python executes tools in a controlled way.

---

## Project Overview

This project started as a local RAG command-line system and was gradually upgraded into a more realistic AI application.

Current version:

```text
Local RAG
+
Multi-step AI Agent
+
FastAPI Backend
+
Streamlit Frontend
+
API Quality Tests
```

Core idea:

```text
LLM plans.
Python executes.
RAG provides local knowledge.
Tools provide actions.
History stores observations.
Evaluation checks reliability.
FastAPI exposes the Agent as a backend service.
Streamlit provides a user interface.
```

The system can:

- Answer questions based on a local knowledge base
- Retrieve relevant chunks using semantic search
- Call tools such as calculator, file reader, RAG, and general LLM response
- Run multi-step Agent workflows
- Return final answers with execution history
- Serve the Agent through an HTTP API
- Display results through a Streamlit frontend
- Track request IDs, latency, and API logs
- Run automatic evaluation and API quality tests

---

## V3 Highlights: FastAPI Backend + API-based Frontend

In V3, the project was upgraded from a local Streamlit demo into a more realistic frontend-backend architecture.

### New Features

- FastAPI backend for serving the AI Agent as an HTTP API
- `/health` endpoint for service status checking
- `/agent/run` endpoint for running the multi-step Agent
- Streamlit frontend that calls the FastAPI backend through HTTP requests
- Request ID tracking for each API call
- API request logging in JSONL format
- Latency tracking for each Agent request
- API smoke test client
- API quality tests for tool selection and final answer keywords

### V3 Architecture

```text
User
↓
Streamlit Frontend: src/app_api.py
↓ HTTP POST
FastAPI Backend: src/api.py
↓
Multi-step Agent: src/multi_step_agent.py
↓
Tool Calling
├── calculator
├── file_reader
├── rag
└── llm
↓
Final Answer + Execution History
↓
API Response with request_id, meta, latency, and status
↓
JSONL API Logs
```

---

## Main Features

### RAG Features

- Local knowledge base question answering
- Text chunking
- Sentence embedding generation
- Semantic retrieval with cosine similarity
- Dynamic chunk filtering
- RAG pipeline wrapped as a callable tool
- Source-style retrieved context output
- Lazy loading for embedding model and RAG index

### Agent Features

- JSON-based tool calling
- Structured tool arguments
- Tool schema
- Tool registry
- Python tool execution
- Single-step Agent
- Multi-step Agent loop
- Validation for tool call plans
- Retry logic for invalid tool calls
- Final stop signal
- Tool execution history tracking
- JSONL history logging

### Web / API Features

- Streamlit web interface
- API-based Streamlit frontend
- FastAPI backend
- `/health` endpoint
- `/agent/run` endpoint
- Request ID tracking
- Latency tracking
- API request logging
- API smoke test client
- API quality tests

### Evaluation Features

- Evaluation script for Agent behavior
- Test cases stored in JSON
- Tool selection accuracy check
- Final answer keyword check
- Final success rate check
- Error case tracking
- API quality tests for backend behavior

---

## Tech Stack

```text
Python
Ollama
Qwen2.5:7B
Sentence Transformers
scikit-learn
FastAPI
Uvicorn
Streamlit
Requests
Pydantic
JSON tool calling
JSONL logging
pickle
Git / GitHub
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
│   ├── multi_step_history.jsonl
│   └── api_requests.jsonl
│
├── src/
│   ├── api.py
│   ├── app.py
│   ├── app_api.py
│   ├── agent.py
│   ├── build_index.py
│   ├── llm.py
│   ├── multi_step_agent.py
│   ├── rag_tool.py
│   ├── test_api_client.py
│   ├── tools.py
│   └── utils.py
│
├── tests/
│   └── eval_cases.json
│
├── run_eval.py
├── README.md
├── requirements.txt
└── .gitignore
```

---

## File Description

### `data/knowledge.txt`

The local knowledge base used by the RAG system.

It contains basic AI knowledge such as RAG, Agent, Transformer, CNN, and related concepts.

---

### `src/build_index.py`

Builds the local RAG index.

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

Workflow:

```text
Load local chunks and embeddings
↓
Convert user query into an embedding
↓
Compute cosine similarity
↓
Retrieve relevant chunks
↓
Send retrieved context to Qwen2.5
↓
Generate an answer based on local knowledge
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

The calculator tool handles simple mathematical expressions.

The file reader tool reads local text files such as `data/knowledge.txt`.

---

### `src/llm.py`

Wraps the local LLM call.

It uses Ollama to call Qwen2.5 locally.

This keeps the LLM call logic separate from Agent logic.

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
Python validates the plan
↓
Python executes the selected tool
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
Tool schema
Structured arguments
Validation
Retry
History
max_steps
final stop signal
```

The `final` signal is not a real tool. It tells the Agent loop to stop and return the final answer.

---

### `src/api.py`

The FastAPI backend.

It exposes the Agent as an HTTP API.

Main endpoints:

```text
GET  /health
POST /agent/run
```

The API returns:

```text
request_id
final_answer
history
meta
```

It also records API requests in:

```text
outputs/api_requests.jsonl
```

Each API log includes:

```text
request_id
timestamp
task
max_steps
max_retries
final_answer
history
latency_ms
status
error
```

---

### `src/app.py`

The original Streamlit web app.

It directly calls the local multi-step Agent from Python.

---

### `src/app_api.py`

The API-based Streamlit frontend.

It sends HTTP requests to the FastAPI backend instead of directly calling the Agent.

Workflow:

```text
User enters task in Streamlit
↓
Streamlit sends POST request to /agent/run
↓
FastAPI runs the Agent
↓
Streamlit receives final answer and execution history
↓
Streamlit displays result, metadata, and tool steps
```

---

### `src/test_api_client.py`

A test client for the FastAPI backend.

It checks:

```text
/health endpoint
/agent/run endpoint
tool selection
final answer keywords
request_id
history
meta
```

Expected result:

```text
All API quality tests passed.
```

---

### `run_eval.py`

Runs automatic evaluation for the Agent.

It evaluates:

```text
tool selection accuracy
keyword pass rate
final success rate
average steps
error cases
```

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

Expected behavior:

```text
23 * 17 = 391
```

---

### 2. File Reader Tool

Used for reading local text files.

Example:

```text
read data/knowledge.txt and summarize the difference between RAG and Agent
```

Expected tool flow:

```text
file_reader
↓
llm
```

Expected behavior:

```text
The Agent reads the file first, then summarizes the difference based on the file content.
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

Expected behavior:

```text
The Agent retrieves relevant local knowledge and answers based on it.
```

---

### 4. LLM Tool

Used for general language tasks that do not require local knowledge retrieval, file reading, or calculation.

Example:

```text
Rewrite this sentence in a more professional tone: I made an AI project.
```

Expected tool:

```text
llm
```

---

## API Endpoints

### `GET /health`

Checks whether the API service is running.

Example response:

```json
{
  "status": "ok",
  "service": "rag_agent_api",
  "version": "1.1.0"
}
```

---

### `POST /agent/run`

Runs the local RAG + multi-step AI Agent.

Example request:

```json
{
  "task": "what is RAG? Use the local knowledge base to answer.",
  "max_steps": 5,
  "max_retries": 2
}
```

Example response:

```json
{
  "request_id": "example-request-id",
  "final_answer": "RAG means Retrieval-Augmented Generation...",
  "history": [
    {
      "step": 1,
      "thought": "The user asks for an explanation of RAG based on local knowledge.",
      "tool": "rag",
      "arguments": {
        "query": "what is RAG?"
      },
      "result": "Retrieved answer with local knowledge context."
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-05-14T18:24:56",
    "max_steps": 5,
    "max_retries": 2,
    "step_count": 1,
    "latency_ms": 19922.93,
    "status": "success"
  }
}
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/choicezyc-zym/rag-agent-project.git
cd rag-agent-project
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and run Ollama

Make sure Ollama is installed and running locally.

### 5. Pull Qwen2.5

```bash
ollama pull qwen2.5:7b
```

---

## Requirements

The `requirements.txt` file should include packages such as:

```txt
fastapi
uvicorn
streamlit
requests
sentence-transformers
scikit-learn
numpy
pydantic
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

### Step 2: Run the original Streamlit app

```bash
python -m streamlit run src/app.py
```

This version directly calls the Agent from Python.

---

### Step 3: Run the FastAPI backend

```bash
python -m uvicorn src.api:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

You can test `/health` and `/agent/run` from the FastAPI documentation page.

---

### Step 4: Run the API-based Streamlit frontend

Open a second terminal and keep the FastAPI backend running.

Then run:

```bash
python -m streamlit run src/app_api.py
```

This version calls the FastAPI backend through HTTP requests.

---

### Step 5: Run API quality tests

Make sure the FastAPI backend is running first.

Then run:

```bash
python src/test_api_client.py
```

Expected result:

```text
All API quality tests passed.
```

---

### Step 6: Run Agent evaluation

```bash
python run_eval.py
```

Expected result example:

```text
Evaluation Summary
Total cases: 6
Passed cases: 6
Tool selection accuracy: 1.0
Keyword pass rate: 1.0
Final success rate: 1.0
Error cases: 0
```

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
Step 2 | Tool: llm
Final Answer: Summary based on file content
```

---

### LLM Rewrite

```text
Rewrite this sentence in a more professional tone: I made an AI project.
```

Expected behavior:

```text
Step 1 | Tool: llm
Final Answer: A more professional rewritten sentence
```

---

## Evaluation

This project includes automatic evaluation for the multi-step Agent.

The evaluation checks:

- Whether the Agent selects the expected first tool
- Whether the final answer contains expected keywords
- Whether the Agent can complete the task successfully
- Whether there are execution errors
- How many steps the Agent uses on average

Evaluation cases are stored in:

```text
tests/eval_cases.json
```

Run evaluation:

```bash
python run_eval.py
```

Current evaluation result:

```text
Total cases: 6
Passed cases: 6
Tool selection accuracy: 1.0
Keyword pass rate: 1.0
Final success rate: 1.0
Error cases: 0
```

---

## API Quality Tests

The project also includes API-level tests in:

```text
src/test_api_client.py
```

The API quality tests check:

- `/health` endpoint availability
- `/agent/run` endpoint availability
- Expected tools in execution history
- Expected keywords in final answer
- `request_id` exists
- `history` exists
- `meta` exists

Run:

```bash
python src/test_api_client.py
```

Expected result:

```text
All API quality tests passed.
```

---

## Execution History and Logging

Single-step Agent history is saved in:

```text
outputs/agent_history.jsonl
```

Multi-step Agent history is saved in:

```text
outputs/multi_step_history.jsonl
```

API request logs are saved in:

```text
outputs/api_requests.jsonl
```

These logs are useful for:

- Debugging
- Checking tool selection
- Reviewing Agent behavior
- Tracking latency
- Analyzing failed requests
- Improving evaluation cases

---

## What I Learned

Through this project, I learned:

- How to combine RAG and Agent systems
- How to wrap a RAG pipeline as a callable tool
- How to use an LLM for tool planning
- How to use JSON as a structured tool call format
- How to design structured tool arguments
- How to validate tool call plans
- How to retry invalid tool calls
- How to let Python execute tools based on LLM-generated plans
- How to use Sentence Transformers for semantic retrieval
- How to use cosine similarity for chunk retrieval
- How to call Qwen2.5 locally with Ollama
- How to log Agent execution history using JSONL
- How to build a multi-step Agent loop
- How to use history, `max_steps`, and `final` to control multi-step execution
- How to build a Streamlit web interface for an AI Agent
- How to expose an AI Agent through a FastAPI backend
- How to connect a frontend to a backend through HTTP requests
- How to track request IDs and latency
- How to write API quality tests for an AI application

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

`rag_agent_project` combines both ideas and upgrades them into a more complete local AI application.

```text
User task
↓
FastAPI receives request
↓
Agent selects calculator / file_reader / rag / llm
↓
Python validates and executes the selected tool
↓
History stores the result
↓
Agent returns final answer
↓
Streamlit displays final answer, metadata, and execution steps
```

The key improvement is:

```text
RAG becomes one of the Agent's tools.
The Agent supports multi-step tool use.
The system is exposed through a FastAPI backend.
The frontend communicates with the backend through HTTP requests.
Evaluation and API quality tests check reliability.
```

---

## Limitations

Current limitations:

- The knowledge base is still small
- The Agent only supports a few tools
- JSON parsing fallback is still relatively simple
- The multi-step Agent can handle simple workflows but not very complex planning
- Final answer formatting may sometimes need improvement
- No vector database integration yet
- No user authentication yet
- No online deployment yet
- No production monitoring dashboard yet

---

## Future Improvements

Possible future improvements:

- Add more tools such as time, todo, web search, or database query
- Replace pickle files with a vector database such as FAISS, Chroma, or Qdrant
- Add file upload support in the Streamlit app
- Add conversation memory
- Improve tool routing accuracy
- Add stronger reflection or self-checking before final answers
- Support larger local knowledge bases
- Improve multi-step planning for more complex tasks
- Add Docker support
- Add online deployment
- Add CI tests with GitHub Actions
- Add authentication for API access

---

## Interview Explanation

A short explanation of this project:

```text
I built a local RAG + multi-step AI Agent application.

The system uses a local LLM to generate structured tool-calling plans, while Python validates and executes the selected tools. It supports calculator, file reading, RAG retrieval, and general LLM response.

I also upgraded the project with a FastAPI backend and a Streamlit frontend. The Agent can be called through an HTTP API, and each request returns a final answer, execution history, request ID, latency, and status metadata.

To improve reliability, I added validation, retry logic, execution logging, evaluation cases, and API quality tests that check both tool selection and final answer keywords.
```

Chinese version:

```text
我做了一个本地 RAG + 多步 AI Agent 应用。

系统由本地大模型负责生成结构化工具调用计划，Python 负责校验和执行工具。它支持计算器、文件读取、本地知识库检索和普通 LLM 回答。

后来我把项目升级成 FastAPI 后端 + Streamlit 前端结构。Agent 可以通过 HTTP API 调用，每次请求都会返回最终答案、执行历史、request_id、延迟和状态信息。

为了提高可靠性，我还加入了参数校验、失败重试、执行日志、自动评估测试集和 API quality tests，用来检查工具选择和最终答案质量。
```

---

## Final Summary

This project is a local RAG + multi-step AI Agent web application with a FastAPI backend and Streamlit frontend.

It combines semantic retrieval, local LLM generation, structured JSON tool calling, Python tool execution, validation, retry logic, execution logging, API request logging, evaluation, API quality testing, and a product-style frontend.

The main idea is:

```text
The Agent decides what to do.
The RAG tool provides local knowledge.
Python validates and executes the selected tool.
History stores previous tool results.
FastAPI exposes the Agent as a backend service.
Streamlit displays the workflow.
Evaluation checks reliability.
Final stops the multi-step loop.
```

This project helped me understand how modern AI applications combine models, knowledge bases, tools, APIs, logging, evaluation, and user interfaces into one system.
