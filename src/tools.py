from pathlib import Path


def calculator_tool(expression: str) -> str:
    """
    计算器工具。
    只允许基础数学表达式，避免执行危险代码。
    """

    try:
        allowed_chars = "0123456789+-*/(). %"

        for char in expression:
            if char not in allowed_chars:
                return f"计算失败：表达式包含不允许的字符：{char}"

        result = eval(expression)

        return f"计算结果：{expression} = {result}"

    except Exception as e:
        return f"计算失败：{e}"


def file_reader_tool(file_path: str) -> str:
    """
    文件读取工具。
    用于读取本地 txt 文件内容。
    """

    try:
        path = Path(file_path)

        if not path.is_absolute():
            project_root = Path(__file__).resolve().parent.parent
            path = project_root / file_path

        if not path.exists():
            return f"文件读取失败：文件不存在：{file_path}"

        if not path.is_file():
            return f"文件读取失败：这不是一个文件：{file_path}"

        content = path.read_text(encoding="utf-8")

        return f"文件内容：\n{content}"

    except Exception as e:
        return f"文件读取失败：{e}"


if __name__ == "__main__":
    print(calculator_tool("23 * 17"))
    print(file_reader_tool("data/knowledge.txt"))