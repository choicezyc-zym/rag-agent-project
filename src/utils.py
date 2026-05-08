import pickle
from pathlib import Path


def save_pickle(obj, file_path):
    """
    保存 Python 对象到 pickle 文件。
    """
    file_path = Path(file_path)

    with open(file_path, "wb") as f:
        pickle.dump(obj, f)


def load_pickle(file_path):
    """
    从 pickle 文件读取 Python 对象。
    """
    file_path = Path(file_path)

    with open(file_path, "rb") as f:
        return pickle.load(f)