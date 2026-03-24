from __future__ import annotations

from pathlib import Path

from jazzpy.config import JazzPyPaths
from jazzpy.core.ngram import NgramModel
from jazzpy.core.smoothing import LaplaceSmoothing
from jazzpy.io.fileio import FileIO
from jazzpy.io.naming import NamingConvention
from jazzpy.training.raw_data import RawDataExtractor


class CorpusTrainer:
    """End-to-end corpus extraction and statistical model training."""

    def __init__(self, paths: JazzPyPaths) -> None:
        self.paths = paths
        self.paths.ensure_directories()
        self.file_io = FileIO()
        self.ngram = NgramModel()
        self.smoothing = LaplaceSmoothing()
        self.extractor = RawDataExtractor()

    def extract_raw_data(self, corpus_dir: Path) -> None:
        works = sorted(corpus_dir.glob("*.xml")) + sorted(corpus_dir.glob("*.musicxml"))
        if not works:
            raise FileNotFoundError(f"No MusicXML files were found in {corpus_dir}")

        major_text, minor_text, major_stop, minor_stop = self.extractor.get_harmonic_raw_data(works)
        rhythmic_text, rhythmic_stop = self.extractor.get_rhythmic_raw_data(works)

        self.file_io.write_text(
            major_text,
            self.paths.raw_dir / NamingConvention.file_names("jazz", "major").raw_data,
        )
        self.file_io.write_text(
            minor_text,
            self.paths.raw_dir / NamingConvention.file_names("jazz", "minor").raw_data,
        )
        self.file_io.write_dict(
            {key: float(value) for key, value in major_stop.items()},
            self.paths.raw_dir / NamingConvention.file_names("jazz", "stopM").raw_data,
        )
        self.file_io.write_dict(
            {key: float(value) for key, value in minor_stop.items()},
            self.paths.raw_dir / NamingConvention.file_names("jazz", "stopminor").raw_data,
        )
        self.file_io.write_text(
            rhythmic_text,
            self.paths.raw_dir / NamingConvention.file_names("jazz", "rhythm").raw_data,
        )
        self.file_io.write_dict(
            {key: float(value) for key, value in rhythmic_stop.items()},
            self.paths.raw_dir / NamingConvention.file_names("jazz", "stopR").raw_data,
        )

    def train_models(self, composer_name: str, harmonic_max_tokens: int, rhythmic_max_tokens: int) -> None:
        self._train_mode(composer_name, mode="major", max_tokens=harmonic_max_tokens)
        self._train_mode(composer_name, mode="rhythm", max_tokens=rhythmic_max_tokens)

    def _train_mode(self, composer_name: str, mode: str, max_tokens: int) -> None:
        names = NamingConvention.file_names(composer_name, mode)

        # --- Load raw data ---
        raw_text = self.file_io.read_text(self.paths.raw_dir / names.raw_data)
        tokens = self.ngram.get_tokens(raw_text)

        # --- Load stop words (frequency dict) ---
        stop_mode = self._infer_stop_mode(mode)
        stop_names = NamingConvention.file_names(composer_name, stop_mode)
        raw_stop_dict = self.file_io.read_dict(self.paths.raw_dir / stop_names.raw_data)

        # --- FIX: apply threshold-based filtering ---
        if raw_stop_dict:
            total = sum(raw_stop_dict.values())

            # umbral configurable (puedes ajustar)
            threshold = 1.1

            stop_words = {
                token for token, count in raw_stop_dict.items()
                if (count / total) > threshold
            }

            tokens = self.ngram.remove_stop_words(tokens, stop_words)

        # --- Reduce vocabulary ---
        tokens = self.ngram.filter_most_frequent_tokens(tokens, max_tokens)

        # --- Safety check (muy importante) ---
        if not tokens:
            raise ValueError(
                f"Token sequence became empty after stop-word filtering in mode '{mode}'. "
                f"Adjust threshold or disable stop-word removal."
            )

        # --- Build n-grams ---
        unigram = self.ngram.get_unigram(tokens)
        bigram = self.ngram.get_bigram(tokens)
        trigram = self.ngram.get_trigram(tokens)

        # --- Smoothing ---
        alpha = 0.0001
        bigram_prob = self.smoothing.calculate_bigram_probability_laplace(unigram, bigram, alpha)
        trigram_prob = self.smoothing.calculate_trigram_probability_laplace(unigram, trigram, alpha)
        unigram_zero = self.smoothing.smoothing_bigram_zero(unigram, bigram, alpha)
        bigram_zero = self.smoothing.smoothing_trigram_zero(unigram, trigram, alpha)

        # --- Save models ---
        model_dir = self.paths.statistical_models_dir
        self.file_io.save_pickle(unigram, model_dir / names.unigram)
        self.file_io.save_pickle(bigram_prob, model_dir / names.bigram)
        self.file_io.save_pickle(trigram_prob, model_dir / names.trigram)
        self.file_io.save_pickle(unigram_zero, model_dir / names.unigram_zero)
        self.file_io.save_pickle(bigram_zero, model_dir / names.bigram_zero)

    @staticmethod
    def _infer_stop_mode(mode: str) -> str:
        lowered = mode.lower()
        if lowered == "major":
            return "stopM"
        if lowered == "minor":
            return "stopminor"
        if lowered == "rhythm":
            return "stopR"
        raise ValueError(f"Unsupported training mode: {mode}")