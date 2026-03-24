from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class JazzPyPaths:
    root: Path
    src_dir: Path
    corpora_dir: Path
    data_dir: Path
    raw_dir: Path
    models_dir: Path
    statistical_models_dir: Path

    @classmethod
    def project_root(cls, root: Path) -> "JazzPyPaths":
        root = root.resolve()
        return cls(
            root=root,
            src_dir=root / "src",
            corpora_dir=root / "corpora",
            data_dir=root / "data",
            raw_dir=root / "data" / "raw",
            models_dir=root / "models",
            statistical_models_dir=root / "models" / "statistical",
        )

    def ensure_directories(self) -> None:
        self.corpora_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.statistical_models_dir.mkdir(parents=True, exist_ok=True)
