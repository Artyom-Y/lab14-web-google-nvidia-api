import json
import os
import tempfile
from typing import Dict, Any

DEFAULT_CHATS_FILE = os.getenv("CHATS_FILE", "chats.json")


def _atomic_write(path: str, data: str) -> None:
    dirpath = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=dirpath)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(data)
    os.replace(tmp, path)


def load_chats(path: str = None) -> Dict[str, Any]:
    if path is None:
        path = DEFAULT_CHATS_FILE
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chats(chats: Dict[str, Any], path: str = None) -> None:
    if path is None:
        path = DEFAULT_CHATS_FILE
    _atomic_write(path, json.dumps(chats, ensure_ascii=False, indent=2))


def get_session(session_key: str, path: str = None) -> Dict[str, Any]:
    chats = load_chats(path)
    return chats.get(session_key)


def set_session(session_key: str, session_obj: Dict[str, Any], path: str = None) -> None:
    chats = load_chats(path)
    chats[session_key] = session_obj
    save_chats(chats, path)


def delete_session(session_key: str, path: str = None) -> None:
    chats = load_chats(path)
    if session_key in chats:
        del chats[session_key]
        save_chats(chats, path)


__all__ = ["load_chats", "save_chats", "get_session", "set_session", "delete_session"]
