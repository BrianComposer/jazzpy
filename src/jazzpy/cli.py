from __future__ import annotations

import argparse
from pathlib import Path

from music21 import key

from jazzpy.composer import Composer
from jazzpy.config import JazzPyPaths
from jazzpy.training.parser import CorpusTrainer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jazzpy", description="Train and generate symbolic jazz material.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Extract raw data and train statistical models.")
    train_parser.add_argument("--corpus-dir", type=Path, required=True, help="Directory containing MusicXML files.")
    train_parser.add_argument("--composer", default="jazz", help="Logical name of the corpus/composer.")
    train_parser.add_argument("--harmonic-max-tokens", type=int, default=25)
    train_parser.add_argument("--rhythmic-max-tokens", type=int, default=20)
    train_parser.add_argument("--project-root", type=Path, default=Path.cwd())

    compose_parser = subparsers.add_parser("compose", help="Generate a new score from trained models.")
    compose_parser.add_argument("--output", type=Path, required=True, help="Output MusicXML path.")
    compose_parser.add_argument("--tonic", default="C", help="Tonic name for the generated score.")
    compose_parser.add_argument("--mode", default="major", choices=["major", "minor"])
    compose_parser.add_argument("--project-root", type=Path, default=Path.cwd())

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    paths = JazzPyPaths.project_root(args.project_root)
    paths.ensure_directories()

    if args.command == "train":
        trainer = CorpusTrainer(paths=paths)
        trainer.extract_raw_data(corpus_dir=args.corpus_dir)
        trainer.train_models(
            composer_name=args.composer,
            harmonic_max_tokens=args.harmonic_max_tokens,
            rhythmic_max_tokens=args.rhythmic_max_tokens,
        )
        print("Training completed successfully.")
        return

    if args.command == "compose":
        composer = Composer(paths=paths)
        tonal_center = key.Key(args.tonic)
        chords, melody = composer.compose_aba_jazz(tonality=tonal_center, mode=args.mode)
        score = composer.generate_score(chords=chords, melody=melody, tonality=tonal_center)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        score.write("musicxml", fp=str(args.output))
        print(f"Score written to {args.output}")
        return

    raise ValueError(f"Unsupported command: {args.command}")
