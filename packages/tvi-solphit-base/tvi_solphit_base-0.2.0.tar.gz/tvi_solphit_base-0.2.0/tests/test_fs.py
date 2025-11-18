from pathlib import Path
from tvi.solphit.base.fs import atomic_write_text

def test_atomic_write_text_overwrite(tmp_path: Path):
    target = tmp_path / "out.txt"
    target.write_text("old")
    # First write
    atomic_write_text(target, "new1")
    assert target.read_text() == "new1"
    # Second write — should cleanly replace, no partials left behind
    atomic_write_text(target, "new2")
    assert target.read_text() == "new2"

def test_atomic_write_text_creates_parents(tmp_path: Path):
    target = tmp_path / "nested" / "dir" / "file.txt"
    atomic_write_text(target, "hello")
    assert target.exists()
    assert target.read_text() == "hello"