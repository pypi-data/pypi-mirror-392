# tvi-solphit-base

Shared utilities for the SolphIT stack. Clean, well‑named helpers for logging, CLI parsing, filesystem, JSONL, discovery, and timing.

## Install (development)

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
# or with tests if you add extras: python -m pip install -e .[test]
```

## Quick start

```python
from tvi.solphit.base.logging import SolphitLogger
log = SolphitLogger.get_logger("demo")
log.info("hello")
```

More examples:

- [Logging / `SolphitLogger`](docs/logging-SolphitLogger.md)
- [Argument parsing base (`ArgParsed`)](docs/arg_parsed.md)
- [Custom arg types](docs/arg_types.md)
- [Filesystem: `atomic_write_text`](docs/fs-atomic_write_text.md)
- [JSONL helpers](docs/jsonl.md)
- [File discovery](docs/discovery-find_files.md)
- [Timing utilities](docs/timing.md)

## Environment variables (logging)

- `TVI_SOLPHIT_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL`
- `TVI_SOLPHIT_LOG_DEST=stdout|file`
- `TVI_SOLPHIT_LOG_FILE=solphit.log`
- `TVI_SOLPHIT_LOG_FORMAT="%(asctime)s | %(levelname)s | %(name)s | %(message)s"`

## Testing

```bash
pytest
# or verbose with logs: pytest -s
```

## Versioning

This project follows [Semantic Versioning](https://semver.org/). See [CHANGELOG.md](CHANGELOG.md) for release notes.

## License

MIT. See [LICENSE](LICENSE).
