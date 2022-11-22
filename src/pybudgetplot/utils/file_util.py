"""This module defines logic for file related operations."""
import logging
from pathlib import Path

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def read_bytes(file) -> bytes:
    """Reads file as bytes."""

    file_path = Path(file).absolute().resolve(strict=True)
    return file_path.read_bytes()


def read_str(file, encoding="utf-8", errors="surrogateescape") -> str:
    """Reads file as string."""

    file_bytes = read_bytes(file)
    file_text = file_bytes.decode(encoding=encoding, errors=errors)
    return file_text.replace("\r\n", "\n")


def write_bytes(file, data: bytes):
    """Writes bytes to file, creates the parent dir if missing."""

    file_path = Path(file).absolute().resolve(strict=False)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(data)


def write_str(file, data: str, encoding="utf-8", errors="surrogateescape"):
    """Writes string to file, creates the parent dir if missing."""

    data_bytes = data.encode(encoding=encoding, errors=errors)
    write_bytes(file, data_bytes)
