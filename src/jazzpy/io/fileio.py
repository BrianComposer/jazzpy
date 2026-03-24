from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any


class FileIO:
    """Simple file and pickle persistence helpers."""

    @staticmethod
    def save_pickle(obj: Any, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as handle:
            pickle.dump(obj, handle, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_pickle(path: Path) -> Any:
        with path.open("rb") as handle:
            return pickle.load(handle)

    @staticmethod
    def write_text(text: str, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    @staticmethod
    def read_text(path: Path) -> str:
        return path.read_text(encoding="utf-8")

    @staticmethod
    def write_lines(lines: list[str], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def read_lines(path: Path) -> list[str]:
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]

    @staticmethod
    def write_dict(values: dict[str, float], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for key, value in values.items():
                handle.write(f"{key} {value}\n")

    @staticmethod
    def read_dict(path: Path) -> dict[str, float]:
        output: dict[str, float] = {}
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                parts = line.strip().split(" ")
                if len(parts) >= 2:
                    output[parts[0]] = float(parts[1])
        return output
