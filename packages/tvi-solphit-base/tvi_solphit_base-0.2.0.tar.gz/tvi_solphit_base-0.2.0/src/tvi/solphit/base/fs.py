from __future__ import annotations
from pathlib import Path
import os, tempfile, shutil

def atomic_write_text(target: Path, data: str, encoding="utf-8") -> Path:
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=target.parent, encoding=encoding) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, target)   # atomic on POSIX
    return target