from pathlib import Path
from tvi.solphit.base.discovery import find_files

def test_find_files_include_exclude(tmp_path: Path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    fa = tmp_path / "a" / "x.txt"
    fb = tmp_path / "a" / "y.log"
    fc = tmp_path / "b" / "z.txt"
    fa.write_text("x")
    fb.write_text("y")
    fc.write_text("z")

    # include all txt, exclude a/y.log (by pattern) and anything under b (to test exclusion)
    includes = ["**/*.txt", "**/*.log"]
    excludes = ["**/y.log", "b/*"]

    found = set(find_files(tmp_path, includes=includes, excludes=excludes))
    assert fa in found
    assert fc not in found           # excluded via "b/*"
    assert (tmp_path / "a" / "y.log") not in found  # excluded explicitly