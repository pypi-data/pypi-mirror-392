from pathlib import Path
from tvi.solphit.base.jsonl import write_jsonl, read_jsonl

def test_jsonl_roundtrip(tmp_path: Path):
    path = tmp_path / "data.jsonl"
    records = [
        {"id": 1, "txt": "hello"},
        {"id": 2, "txt": "world 🌍"},
    ]
    write_jsonl(path, records)
    got = list(read_jsonl(path))
    assert got == records