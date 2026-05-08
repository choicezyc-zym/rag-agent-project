from pathlib import Path
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from utils import load_pickle


_embedding_model = None
_chunks = None
_chunk_embeddings = None


def load_rag_resources():
    """
    懒加载 RAG 资源。
    第一次调用时加载 embedding 模型、chunks 和 chunk_embeddings。
    后续调用会复用，避免每次重复加载模型。
    """

    global _embedding_model, _chunks, _chunk_embeddings

    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    if _chunks is None or _chunk_embeddings is None:
        project_root = Path(__file__).resolve().parent.parent
        output_dir = project_root / "outputs"

        _chunks = load_pickle(output_dir / "chunks.pkl")
        _chunk_embeddings = load_pickle(output_dir / "chunk_embeddings.pkl")

    return _embedding_model, _chunks, _chunk_embeddings


def retrieve_top_k(
    query: str,
    model,
    chunk_embeddings,
    chunks,
    top_k: int = 3,
    min_score: float = 0.15,
    relative_threshold: float = 0.55
):
    """
    根据用户 query 检索最相关的文本 chunks。
    """

    query_embedding = model.encode([query], convert_to_numpy=True)
    scores = cosine_similarity(query_embedding, chunk_embeddings).flatten()

    ranked_indices = scores.argsort()[::-1][:top_k]

    best_score = scores[ranked_indices[0]]
    dynamic_threshold = max(min_score, best_score * relative_threshold)

    results = []

    for idx in ranked_indices:
        if scores[idx] >= dynamic_threshold:
            results.append((chunks[idx], scores[idx]))

    return results


def generate_rag_answer(query: str, retrieved_chunks: list[tuple[str, float]]) -> str:
    """
    使用本地 Qwen2.5，根据检索到的 chunks 生成答案。
    """

    context_lines = []

    for i, (chunk, score) in enumerate(retrieved_chunks, start=1):
        context_lines.append(f"资料 {i}：\n{chunk}")

    context = "\n\n".join(context_lines)

    prompt = f"""
你是一个严谨的 RAG 问答助手。

请你只根据下面提供的资料回答用户问题。
如果资料中没有答案，请直接说：资料中没有找到相关信息。
不要编造，不要使用资料之外的知识。

【资料】
{context}

【用户问题】
{query}

【回答要求】
1. 用中文回答。
2. 回答要清楚、简洁。
3. 只基于资料内容回答。
4. 如果资料不足，要明确说明资料不足。
5. 不要在答案中重复输出完整资料原文。

【最终答案】
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        },
        timeout=120
    )

    response.raise_for_status()
    result = response.json()

    llm_answer = result["response"].strip()

    source_lines = []

    for i, (chunk, score) in enumerate(retrieved_chunks, start=1):
        source_lines.append(
            f"[{i}] score={score:.4f}\n{chunk}"
        )

    sources = "\n\n".join(source_lines)

    final_answer = (
        f"{llm_answer}\n\n"
        f"参考来源：\n"
        f"{sources}"
    )

    return final_answer


def rag_tool(query: str) -> str:
    """
    RAG 工具函数。
    Agent 会调用这个函数回答本地知识库相关问题。
    """

    try:
        model, chunks, chunk_embeddings = load_rag_resources()

        retrieved_chunks = retrieve_top_k(
            query=query,
            model=model,
            chunk_embeddings=chunk_embeddings,
            chunks=chunks,
            top_k=3,
            min_score=0.15,
            relative_threshold=0.55
        )

        if not retrieved_chunks:
            return "资料中没有找到相关信息。"

        answer = generate_rag_answer(query, retrieved_chunks)

        return answer

    except Exception as e:
        return f"RAG 工具调用失败：{e}"


if __name__ == "__main__":
    print(rag_tool("what is RAG?"))