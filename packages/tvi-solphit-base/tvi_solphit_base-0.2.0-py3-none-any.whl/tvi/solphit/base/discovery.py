from __future__ import annotations
from pathlib import Path
from typing import Iterable, Iterator

def find_files(root: Path, includes: Iterable[str]=("**/*",), excludes: Iterable[str]=()) -> Iterator[Path]:
    root = Path(root)
    seen = set()
    for pat in includes:
        for p in root.glob(pat):
            if p.is_file():
                seen.add(p.resolve())
    for pat in excludes:
        for p in root.glob(pat):
            seen.discard(p.resolve())
    for p in sorted(seen):
        yield Path(p)