from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelFileNames:
    raw_data: str
    bigram: str
    trigram: str
    unigram_zero: str
    bigram_zero: str
    unigram: str


class NamingConvention:
    """Centralized naming conventions for persisted statistical assets."""

    @staticmethod
    def normalize_mode(mode: str) -> str:
        value = mode.strip()
        lowered = value.lower()
        aliases = {
            "m": "major",
            "major": "major",
            "minor": "minor",
            "l": "lidian",
            "lidian": "lidian",
            "d": "doric",
            "doric": "doric",
            "stopm": "stopmayor",
            "stopmayor": "stopmayor",
            "stopminor": "stopminor",
            "stopr": "stoprythm",
            "stoprhythm": "stoprythm",
            "r": "rhythm",
            "rhythm": "rhythm",
            "ritmo": "rhythm",
        }
        return aliases.get(lowered, value)

    @classmethod
    def file_names(cls, composer_name: str, mode: str) -> ModelFileNames:
        normalized_mode = cls.normalize_mode(mode)
        cap_composer = composer_name.capitalize()
        cap_mode = normalized_mode.capitalize()
        low_composer = composer_name.lower()
        low_mode = normalized_mode.lower()

        return ModelFileNames(
            raw_data=f"dataRaw{cap_composer}{cap_mode}.txt",
            bigram=f"{low_composer}_{low_mode}_2gram.pkl",
            trigram=f"{low_composer}_{low_mode}_3gram.pkl",
            unigram_zero=f"{low_composer}_{low_mode}_1gramZero.pkl",
            bigram_zero=f"{low_composer}_{low_mode}_2gramZero.pkl",
            unigram=f"{low_composer}_{low_mode}_1gram.pkl",
        )
