from pathlib import Path
from sentence_transformers import SentenceTransformer

from utils import save_pickle


def load_knowledge(file_path: Path) -> str:
    """
    读取本地知识库文本。
    """
    return file_path.read_text(encoding="utf-8")


def split_text_into_chunks(text: str) -> list[str]:
    """
    将知识库文本切分成 chunks。
    当前版本按空行切分。
    """

    raw_chunks = text.split("\n\n")

    chunks = []
    for chunk in raw_chunks:
        clean_chunk = chunk.strip()

        if clean_chunk:
            chunks.append(clean_chunk)

    return chunks


def build_index():
    """
    构建 RAG 知识库索引：
    1. 读取 knowledge.txt
    2. 切分 chunks
    3. 生成 embeddings
    4. 保存 chunks.pkl 和 chunk_embeddings.pkl
    """

    project_root = Path(__file__).resolve().parent.parent

    data_dir = project_root / "data"
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)

    knowledge_file = data_dir / "knowledge.txt"

    print("正在读取知识库...")
    text = load_knowledge(knowledge_file)

    print("正在切分文本 chunks...")
    chunks = split_text_into_chunks(text)

    print(f"共生成 {len(chunks)} 个 chunks。")

    print("正在加载 embedding 模型...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("正在生成 chunk embeddings...")
    chunk_embeddings = model.encode(chunks, convert_to_numpy=True)

    chunks_file = output_dir / "chunks.pkl"
    embeddings_file = output_dir / "chunk_embeddings.pkl"

    save_pickle(chunks, chunks_file)
    save_pickle(chunk_embeddings, embeddings_file)

    print("索引构建完成。")
    print(f"chunks 已保存到: {chunks_file}")
    print(f"chunk embeddings 已保存到: {embeddings_file}")


if __name__ == "__main__":
    build_index()