"""Local adapters; replace them without changing pipeline or transforms."""

from collections.abc import Iterable, Iterator
from pathlib import Path
from tempfile import NamedTemporaryFile

from pydantic import ValidationError

from .models import DailyTotal, Event


class JsonLinesEventSource:
    def __init__(self, path: Path) -> None:
        self._path = path

    def read(self) -> Iterator[Event]:
        with self._path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    yield Event.model_validate_json(line)
                except ValidationError as error:
                    raise ValueError(
                        f"invalid event at {self._path}:{line_number}"
                    ) from error


class AtomicJsonLinesSink:
    """Replace one complete output atomically, making a retry idempotent."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def write(self, records: Iterable[DailyTotal]) -> int:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._path.parent,
                prefix=f".{self._path.name}.",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                for record in records:
                    handle.write(record.model_dump_json())
                    handle.write("\n")
                    count += 1
            temporary_path.replace(self._path)
            return count
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
