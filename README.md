# jazzpy

**jazzpy** is a symbolic jazz composition toolkit built around a custom n-gram pipeline for harmony and rhythm, plus a rule-based melodic layer implemented with `music21`.

The project is intentionally lightweight. It avoids external NLP tooling and uses only the logic implemented inside the package for tokenization, counting, smoothing, sampling, and generation.

## Features

- Harmony generation from custom bigram and trigram models
- Rhythm generation from custom rhythmic n-gram models
- Melody generation constrained by the current harmony
- Roman numeral harmonic representation with `music21`
- Corpus parsing directly from MusicXML files
- Persistent storage of trained statistical models
- Reproducible project structure for GitHub and PyPI
- Command-line entry point for training and composition

## Project structure

```text
jazzpy/
├── corpora/
│   └── jazz/
│       └── xml/
├── data/
│   └── raw/
├── models/
│   └── statistical/
├── examples/
├── src/
│   └── jazzpy/
│       ├── core/
│       ├── generation/
│       ├── io/
│       ├── training/
│       ├── cli.py
│       ├── composer.py
│       ├── config.py
│       └── __init__.py
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
├── MANIFEST.in
└── .gitignore
```

## Installation

### Local development install

```bash
pip install -e .
```


## Quick start

### 1. Put your MusicXML files in the corpus folder

```text
corpora/jazz/xml/
```

### 2. Train the statistical models

```bash
jazzpy train \
  --corpus-dir corpora/jazz/xml \
  --composer jazz \
  --harmonic-max-tokens 25 \
  --rhythmic-max-tokens 20
```

### 3. Generate a new score

```bash
jazzpy compose \
  --output results/generated_score.musicxml \
  --tonic C \
  --mode major
```

## Python API example

```python
from pathlib import Path
from music21 import key

from jazzpy.composer import Composer
from jazzpy.config import JazzPyPaths
from jazzpy.training.parser import CorpusTrainer

paths = JazzPyPaths.project_root(Path.cwd())
trainer = CorpusTrainer(paths=paths)
trainer.extract_raw_data(corpus_dir=paths.corpora_dir / "jazz" / "xml")
trainer.train_models(composer_name="jazz", harmonic_max_tokens=25, rhythmic_max_tokens=20)

composer = Composer(paths=paths)
chords, melody = composer.compose_aba_jazz(tonality=key.Key("C"), mode="major")
score = composer.generate_score(chords=chords, melody=melody, tonality=key.Key("C"))
score.write("musicxml", fp=str(Path("results/generated_score.musicxml")))
```

## Generation pipeline

The default generation flow is:

1. Parse a MusicXML corpus.
2. Extract harmonic and rhythmic raw symbolic sequences.
3. Count unigram, bigram, and trigram statistics.
4. Apply Laplace smoothing.
5. Save trained statistical models.
6. Generate harmony and rhythm independently.
7. Derive melody from rhythm plus harmony.
8. Assemble a two-part score with `music21`.

## Design principles

- Keep the original musical logic intact.
- Avoid unnecessary dependencies.
- Separate training, generation, I/O, and configuration.
- Make the package usable both as a library and as a CLI tool.
- Preserve explicit musical constraints rather than hiding them inside a black-box model.

## Notes

- The package currently assumes a phrase-oriented workflow similar to the original implementation.
- The built-in phrase generator is designed for 4/4 jazz-like material.
- Training data should be structurally consistent and preferably harmonic-annotated if you want the harmony extractor to work well.

## Publications

- Martínez-Rodríguez, B. (2019). *Emulación de estilos musicales mediante modelos de Markov*. EAE.
  [https://hdl.handle.net/20.500.14468/14582]

## Author

Brian Martínez-Rodríguez

GitHub: https://github.com/BrianComposer

Email: info@brianmartinez.music

Web: www.brianmartinez.music

## License

MIT License.
