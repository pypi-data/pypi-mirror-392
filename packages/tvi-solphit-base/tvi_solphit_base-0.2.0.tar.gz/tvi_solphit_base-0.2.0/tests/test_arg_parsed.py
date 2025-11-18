import argparse
from pathlib import Path
from typing import Any
from tvi.solphit.base.arg_parsed import (
    ArgParsed, comma_list, key_value_pair, existing_path
)

def test_comma_list_parses():
    assert comma_list("a,b, c ,") == ["a", "b", "c"]
    assert comma_list("") == []

def test_key_value_pair_parses_and_validates():
    assert key_value_pair("k=v, a = b") == {"k": "v", "a": "b"}
    assert key_value_pair("") == {}
    try:
        key_value_pair("novalue")
        raised = False
    except argparse.ArgumentTypeError:
        raised = True
    assert raised is True

def test_existing_path_ok_and_error(tmp_path: Path):
    p = tmp_path / "x.txt"
    p.write_text("ok")
    assert existing_path(str(p)) == p
    try:
        existing_path(str(tmp_path / "missing.txt"))
        raised = False
    except argparse.ArgumentTypeError:
        raised = True
    assert raised is True

# ---- Base-class pipeline checks ----

class Echo(ArgParsed):
    def __init__(self, *, name: str = "world", repeat: int = 1) -> None:
        self.name = name
        self.repeat = repeat

    @classmethod
    def register_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--name", default="world")
        parser.add_argument("--repeat", type=int, default=1)

    @classmethod
    def validate_args(cls, args: argparse.Namespace) -> None:
        if args.repeat < 1:
            raise argparse.ArgumentTypeError("--repeat must be >= 1")

    def run(self) -> Any:
        return " ".join([self.name] * self.repeat)

def test_argparsed_main_happy_path():
    out = Echo.main(["--name", "Bob", "--repeat", "2"])
    assert out == "Bob Bob"

def test_argparsed_validation_error():
    # Use parse_args to see our custom validation error
    try:
        Echo.parse_args(["--repeat", "0"])
        raised = False
    except argparse.ArgumentTypeError:
        raised = True
    assert raised is True