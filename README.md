# RAG Agent Project

A local RAG + AI Agent system built with Python, Ollama, Qwen2.5, Sentence Transformers, and JSON tool calling.

This project combines a local Retrieval-Augmented Generation system with an AI Agent.  
The Agent can decide whether to use a calculator, read a local file, call a RAG tool, or use a general LLM response.

The project also includes a basic multi-step Agent version.  
The multi-step Agent can plan, execute tools, save tool results into history, and continue until it outputs a final answer.

---

## Project Goal

The goal of this project is to understand how RAG and Agent systems can be combined.

The core idea is:

```text
RAG is a knowledge tool.
Agent is the controller.
```

In this project, the RAG system is wrapped as a tool called `rag_tool`, and the Agent can decide when to call it.

The upgraded multi-step Agent adds another idea:

```text
LLM plans.
Python executes.
History stores observations.
Final stops the loop.
```

---

## Core Idea

### Single-step Agent Workflow

```text
User Input
    ↓
Qwen2.5 generates a JSON tool call plan
    ↓
Python parses the JSON plan
    ↓
Python calls the selected tool
    ↓
Tool returns the result
    ↓
Agent saves execution history
```

### Multi-step Agent Workflow

```text
User Goal
    ↓
Qwen2.5 generates the next JSON tool plan
    ↓
Python parses and executes the selected tool
    ↓
Tool result is saved into history
    ↓
Qwen2.5 uses history to decide the next step
    ↓
The loop stops when tool = "final"
```

The most important concept is:

```text
LLM plans, Python executes.
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

This is the local knowledge base.

The RAG tool retrieves relevant information from this file and uses it to answer user questions.

---

### `src/build_index.py`

This file builds the RAG index.

It performs the following steps:

```text
Read knowledge.txt
    ↓
Split text into chunks
    ↓
Generate embeddings for each chunk
    ↓
Save chunks.pkl and chunk_embeddings.pkl
```

The generated index files are saved in the `outputs/` folder.

---

### `src/rag_tool.py`

This file defines the RAG tool.

The main function is:

```python
rag_tool(query)
```

It performs:

```text
Load chunks and embeddings
    ↓
Convert user query into embedding
    ↓
Compute cosine similarity
    ↓
Retrieve relevant chunks
    ↓
Send retrieved context to Qwen2.5
    ↓
Generate an answer based on local knowledge
```

It also includes lazy loading, so the embedding model and index are loaded only once during runtime.

---

### `src/tools.py`

This file defines basic tools that the Agent can call.

Current tools:

```text
calculator_tool
file_reader_tool
```

- `calculator_tool` is used for mathematical calculations.
- `file_reader_tool` is used for reading local txt files.

---

### `src/llm.py`

This file wraps the local LLM call.

It uses Ollama to call Qwen2.5 locally:

```python
ask_llm(prompt)
```

This keeps the LLM API logic separate from the Agent logic.

---

### `src/agent.py`

This is the single-step Agent program.

It receives user input, asks Qwen2.5 to generate a JSON tool call plan, parses the plan, calls the selected tool, and saves the execution history.

Supported tools:

```text
calculator
file_reader
rag
llm
```

---

### `src/multi_step_agent.py`

This is the multi-step Agent program.

It can complete a task through multiple rounds of planning, tool execution, observation, and final answer generation.

It uses:

```text
tool registry
JSON tool plan
history
max_steps
final stop signal
```

The basic workflow is:

```text
Plan → Act → Observe → Reflect → Final Answer
```

Supported tools:

```text
calculator
file_reader
rag
llm
final
```

Note: `final` is not a real tool. It is a stop signal used to end the multi-step loop.

---

### `src/utils.py`

This file contains utility functions for saving and loading pickle files.

---

## Supported Tools

### 1. Calculator Tool

Used for mathematical calculation.

Example:

```text
calculate 23 * 17
```

Expected tool call plan:

```json
{
  "tool": "calculator",
  "input": "23 * 17"
}
```

---

### 2. File Reader Tool

Used for reading local txt files.

Example:

```text
read data/knowledge.txt
```

Expected tool call plan:

```json
{
  "tool": "file_reader",
  "input": "data/knowledge.txt"
}
```

---

### 3. RAG Tool

Used for answering questions based on the local knowledge base.

Example:

```text
what is RAG?
```

Expected tool call plan:

```json
{
  "tool": "rag",
  "input": "what is RAG?"
}
```

---

### 4. LLM Tool

Used for general questions that do not require local knowledge retrieval.

Example:

```text
Give me one sentence to encourage AI learning.
```

Expected tool call plan:

```json
{
  "tool": "llm",
  "input": "Give me one sentence to encourage AI learning."
}
```

---

### 5. Final Signal

Used only in the multi-step Agent.

It means the task is complete and the loop should stop.

Example:

```json
{
  "thought": "I have enough information to answer.",
  "tool": "final",
  "input": "RAG retrieves information before generating an answer, while an Agent uses tools to complete tasks."
}
```

---

## Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and run Ollama

Make sure Ollama is installed and running locally.

### 3. Pull Qwen2.5 model

```bash
ollama pull qwen2.5:7b
```

---

## Requirements

```txt
sentence-transformers
scikit-learn
requests
numpy
```

---

## How to Run

### Step 1: Build the RAG index

Run this command first:

```bash
python src/build_index.py
```

This will generate:

```text
outputs/chunks.pkl
outputs/chunk_embeddings.pkl
```

---

### Step 2: Start the single-step Agent

```bash
python src/agent.py
```

---

### Step 3: Start the multi-step Agent

```bash
python src/multi_step_agent.py
```

---

## Example Usage

### Example 1: Calculator

Input:

```text
calculate 23 * 17
```

Output:

```text
工具调用计划：
{
  "tool": "calculator",
  "input": "23 * 17"
}

执行结果：
计算结果：23 * 17 = 391
```

---

### Example 2: File Reading

Input:

```text
read data/knowledge.txt
```

Output:

```text
工具调用计划：
{
  "tool": "file_reader",
  "input": "data/knowledge.txt"
}

执行结果：
文件内容：
...
```

---

### Example 3: RAG Question Answering

Input:

```text
what is Transformer?
```

Output:

```text
工具调用计划：
{
  "tool": "rag",
  "input": "what is Transformer?"
}

执行结果：
Transformer is based on self-attention...
参考来源：
[1] score=...
```

---

### Example 4: General LLM Response

Input:

```text
Give me one sentence to encourage AI learning.
```

Output:

```text
工具调用计划：
{
  "tool": "llm",
  "input": "Give me one sentence to encourage AI learning."
}

执行结果：
...
```

---

### Example 5: Multi-step Agent

Input:

```text
read data/knowledge.txt and summarize the difference between RAG and Agent
```

Possible workflow:

```text
Step 1:
The Agent calls file_reader to read data/knowledge.txt.

Step 2:
The Agent uses the file content in history and outputs a final answer.
```

Final answer example:

```text
RAG retrieves relevant information from a knowledge base before generating an answer. An AI Agent uses tools to complete tasks, focusing on planning and acting.
```

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

Each record is useful for:

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

---

## Difference From Previous Projects

### Compared with `mini_rag_project`

`mini_rag_project` focuses on local knowledge-based question answering.

```text
User Question
    ↓
Retrieve relevant chunks
    ↓
Generate answer with LLM
```

### Compared with `mini_agent_project`

`mini_agent_project` focuses on basic tool calling.

```text
User Task
    ↓
LLM selects a tool
    ↓
Python executes the tool
```

### This Project

`rag_agent_project` combines both ideas.

```text
User Task
    ↓
Agent selects calculator / file_reader / rag / llm
    ↓
Python executes the selected tool
```

The key improvement is:

```text
RAG becomes one of the Agent's tools.
```

The upgraded version also includes a basic multi-step Agent:

```text
User Goal
    ↓
Agent plans the next step
    ↓
Python executes the selected tool
    ↓
Result is saved into history
    ↓
Agent continues until final
```

---

## Limitations

This is a minimal local RAG Agent system.

Current limitations:

- The knowledge base is small
- The Agent only supports a few tools
- JSON parsing fallback is simple
- The multi-step Agent is still basic
- Final answer formatting may sometimes need improvement
- No web interface yet
- No database or vector database integration yet

---

## Future Improvements

Possible future improvements:

- Improve JSON retry and self-correction
- Add more tools such as time, todo, web search, or database query
- Add Streamlit or FastAPI interface
- Replace pickle files with a vector database
- Add conversation memory
- Improve tool routing accuracy
- Support larger local knowledge bases
- Improve multi-step planning for more complex tasks

---

## Final Summary

This project is a local RAG + AI Agent system.

It combines semantic retrieval, local LLM generation, JSON tool calling, Python tool execution, execution logging, and a basic multi-step Agent loop.

The main idea is:

```text
The Agent decides what to do.
The RAG tool provides local knowledge.
Python executes the selected tool.
History stores previous tool results.
Final stops the multi-step loop.
```

This project helped me understand how modern AI applications can combine models, knowledge bases, tools, and engineering workflows.
