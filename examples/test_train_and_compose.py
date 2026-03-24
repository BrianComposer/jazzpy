from pathlib import Path

from music21 import key

from jazzpy.composer import Composer
from jazzpy.config import JazzPyPaths
from jazzpy.training.parser import CorpusTrainer


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    paths = JazzPyPaths.project_root(project_root)

    trainer = CorpusTrainer(paths=paths)
    trainer.extract_raw_data(corpus_dir=paths.corpora_dir / "jazz" / "xml")
    trainer.train_models(composer_name="jazz", harmonic_max_tokens=25, rhythmic_max_tokens=20)

    composer = Composer(paths=paths)
    chords, melody = composer.compose_aba_jazz(tonality=key.Key("C"), mode="major")
    score = composer.generate_score(chords=chords, melody=melody, tonality=key.Key("C"))

    output_path = project_root / "results" / "example_output.musicxml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    score.write("musicxml", fp=str(output_path))
    print(f"Example score written to {output_path}")


if __name__ == "__main__":
    main()
