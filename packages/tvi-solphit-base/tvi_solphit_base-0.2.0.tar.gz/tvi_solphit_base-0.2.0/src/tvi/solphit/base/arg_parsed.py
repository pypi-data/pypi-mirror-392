from __future__ import annotations

import argparse
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type, TypeVar, Sequence, Optional, Any, Dict, List

T = TypeVar("T", bound="ArgParsed")


# ---------- Custom / complex types ----------

def comma_list(value: str) -> List[str]:
    """
    Convert a comma-separated string into a list of trimmed strings.

    "a,b, c" -> ["a", "b", "c"]
    """
    return [part.strip() for part in value.split(",") if part.strip()]


def key_value_pair(value: str) -> Dict[str, str]:
    """
    Convert 'k1=v1,k2=v2' into a dict {'k1': 'v1', 'k2': 'v2'}.

    Raises argparse.ArgumentTypeError on bad input.
    """
    result: Dict[str, str] = {}

    if not value:
        return result

    parts = [p.strip() for p in value.split(",") if p.strip()]
    for part in parts:
        if "=" not in part:
            raise argparse.ArgumentTypeError(
                f"Invalid key=value pair: '{part}'. Expected format 'key=value'."
            )
        key, val = part.split("=", 1)
        key = key.strip()
        val = val.strip()
        if not key:
            raise argparse.ArgumentTypeError(
                f"Empty key in pair: '{part}'. Expected format 'key=value'."
            )
        result[key] = val
    return result


def existing_path(value: str) -> Path:
    """
    Convert to Path and ensure it exists, otherwise raise a parse error.
    """
    p = Path(value)
    if not p.exists():
        raise argparse.ArgumentTypeError(f"Path does not exist: {value}")
    return p


# ---------- Core base class ----------

class ArgParsed(ABC):
    """
    Base class for CLI-driven components with a clean, extensible argument setup.

    Typical usage:

        class MyJob(ArgParsed):
            def __init__(self, name: str, repeat: int = 1):
                self.name = name
                self.repeat = repeat

            @classmethod
            def register_arguments(cls, parser: argparse.ArgumentParser) -> None:
                parser.add_argument("--name", default="world")
                parser.add_argument("--repeat", type=int, default=1)

            def run(self) -> None:
                for _ in range(self.repeat):
                    print(f"Hello {self.name}")

        if __name__ == "__main__":
            MyJob.main()
    """

    # ------ Hooks for subclasses ------

    @classmethod
    def register_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """
        Subclasses override this to define their arguments.

        Example:
            parser.add_argument("--foo", help="Foo value")
        """
        # Default: no arguments
        pass

    @classmethod
    def validate_args(cls, args: argparse.Namespace) -> None:
        """
        Subclasses can override to perform cross-argument validation.

        Raise argparse.ArgumentTypeError or ValueError on invalid combinations.
        """
        # Default: no validation
        pass

    @classmethod
    def from_args(cls: Type[T], args: argparse.Namespace) -> T:
        """
        Subclasses can override this to map parsed args → instance.

        Default assumes constructor parameters match arg names (1:1 mapping).
        """
        kwargs = vars(args).copy()
        # If you add global args (e.g. log-level) you can strip them here.
        return cls(**kwargs)  # type: ignore[arg-type]

    @abstractmethod
    def run(self) -> Any:
        """
        Subclasses implement their main behavior here.
        """
        raise NotImplementedError

    # ------ Core entrypoint helpers ------

    @classmethod
    def build_parser(
        cls,
        *,
        description: Optional[str] = None,
        prog: Optional[str] = None,
        add_help: bool = True,
        formatter_class: Type[argparse.HelpFormatter] = argparse.ArgumentDefaultsHelpFormatter,
    ) -> argparse.ArgumentParser:
        """
        Build the parser and let subclasses register their own arguments.
        """
        parser = argparse.ArgumentParser(
            prog=prog,
            description=description or (cls.__doc__ or None),
            add_help=add_help,
            formatter_class=formatter_class,
        )
        cls.register_arguments(parser)
        return parser

    @classmethod
    def parse_args(
        cls,
        argv: Optional[Sequence[str]] = None,
        **parser_kwargs: Any,
    ) -> argparse.Namespace:
        """
        Create parser, register subclass args, and parse argv.
        """
        parser = cls.build_parser(**parser_kwargs)
        args = parser.parse_args(argv)
        # Run optional validation hook
        cls.validate_args(args)
        return args

    @classmethod
    def main(
        cls: Type[T],
        argv: Optional[Sequence[str]] = None,
        *,
        instantiate_only: bool = False,
        **parser_kwargs: Any,
    ) -> Any:
        """
        Full pipeline:
        - build parser
        - parse args
        - validate args
        - instantiate class
        - run() (unless instantiate_only=True)

        Returns:
            - instance.run() result, or the instance itself if instantiate_only=True
        """
        args = cls.parse_args(argv, **parser_kwargs)
        instance = cls.from_args(args)

        if instantiate_only:
            return instance

        return instance.run()