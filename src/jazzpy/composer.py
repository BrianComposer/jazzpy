from __future__ import annotations

import random
from datetime import datetime

from music21 import instrument, key, stream

from jazzpy.config import JazzPyPaths
from jazzpy.generation.harmony import HarmonyGenerator
from jazzpy.generation.melody import MelodyGenerator
from jazzpy.generation.rhythm import RhythmGenerator
from jazzpy.io.fileio import FileIO
from jazzpy.io.naming import NamingConvention


class Composer:
    """High-level composition orchestrator."""

    def __init__(self, paths: JazzPyPaths) -> None:
        self.paths = paths
        self.paths.ensure_directories()
        self.file_io = FileIO()
        self.harmony = HarmonyGenerator()
        self.rhythm = RhythmGenerator()
        self.melody = MelodyGenerator()

    def generate_score(self, chords, melody, tonality) -> stream.Stream:
        score = stream.Stream()

        melody_part = stream.Part()
        melody_part.append(tonality)
        melody_part.insert(0, instrument.Flute())
        if melody is not None:
            for item in melody:
                melody_part.append(item)
        score.append(melody_part)

        harmony_part = stream.Part()
        harmony_part.append(tonality)
        harmony_part.insert(0, instrument.Piano())
        for current_chord in chords:
            harmony_part.append(current_chord)
        score.append(harmony_part)

        return score

    def compose_phrase(
        self,
        composer_name: str,
        tonality,
        mode: str,
        first_harmony_symbol: str,
        second_harmony_symbol: str,
        first_rhythm_symbol: str,
        second_rhythm_symbol: str,
        cadence: str,
        rhythm_phrase,
        anacrusis: bool,
    ):
        random.seed(datetime.now().microsecond)

        beats_per_measure = 4
        phrase_length = 8
        semiphrase_length = phrase_length // 2
        rhythm_length = beats_per_measure * phrase_length / 4

        duration_chord = "half"
        number_of_chords = self._number_of_chords(semiphrase_length, duration_chord)

        harmonic_names = NamingConvention.file_names(composer_name, mode)
        rhythmic_names = NamingConvention.file_names(composer_name, "rhythm")

        unigram = self.file_io.load_pickle(self.paths.statistical_models_dir / harmonic_names.unigram)
        bigram = self.file_io.load_pickle(self.paths.statistical_models_dir / harmonic_names.bigram)
        trigram = self.file_io.load_pickle(self.paths.statistical_models_dir / harmonic_names.trigram)
        rhythmic_bigram = self.file_io.load_pickle(self.paths.statistical_models_dir / rhythmic_names.bigram)
        rhythmic_trigram = self.file_io.load_pickle(self.paths.statistical_models_dir / rhythmic_names.trigram)
        _ = unigram, rhythmic_bigram

        chords_a1 = self._sample_first_semiphrase(
            trigram=trigram,
            bigram=bigram,
            tonality=tonality,
            first_symbol=first_harmony_symbol,
            number_of_chords=number_of_chords,
            duration_chord=duration_chord,
        )

        chords_a2 = self._sample_second_semiphrase(
            trigram=trigram,
            bigram=bigram,
            tonality=tonality,
            first_symbol=second_harmony_symbol,
            number_of_chords=number_of_chords,
            duration_chord=duration_chord,
            cadence=cadence,
        )

        rhythm_a = self._sample_rhythm(
            trigram=rhythmic_trigram,
            first_symbol=first_rhythm_symbol,
            second_symbol=second_rhythm_symbol,
            total_duration=rhythm_length,
            anacrusis=anacrusis,
            final_note_quarter_length=0.0,
        )
        rhythm_b = self._sample_rhythm(
            trigram=rhythmic_trigram,
            first_symbol=first_rhythm_symbol,
            second_symbol=second_rhythm_symbol,
            total_duration=rhythm_length,
            anacrusis=False,
            final_note_quarter_length=1.0,
        )
        rhythm_c = self._sample_rhythm(
            trigram=rhythmic_trigram,
            first_symbol=first_rhythm_symbol,
            second_symbol=second_rhythm_symbol,
            total_duration=rhythm_length,
            anacrusis=False,
            final_note_quarter_length=1.0,
        )

        complete_rhythm = []
        if rhythm_phrase == "":
            complete_rhythm.extend(rhythm_a[0])
            complete_rhythm.extend(rhythm_b[0])
            complete_rhythm.extend(self.melody.clone_figure(item) for item in rhythm_a[0])
            complete_rhythm.extend(rhythm_c[0])
        else:
            complete_rhythm.extend(self.melody.clone_figure(item) for item in rhythm_phrase)

        complete_chords = list(chords_a1[0]) + list(chords_a2[0])
        generated_melody = self.melody.rhythm_to_melody(complete_rhythm, complete_chords)
        return complete_chords, generated_melody, complete_rhythm

    def compose_aba_jazz(self, tonality, mode: str):
        composer_name = "jazz"
        openings = [
            ["N1/3", "N1/3"],
            ["N1.0", "N1/3"],
            ["N1/3", "N0.5"],
            ["R1.0", "N1/3"],
            ["N0.25", "N0.25"],
            ["R0.5", "N0.5"],
            ["N0.5", "N0.5"],
            ["N1.5", "N0.5"],
            ["N2/3", "N0.5"],
        ]
        harmonic_starts = [
            ["I7", "v"],
            ["i", "iii7"],
            ["i", "v"],
            ["I7", "ii7"],
            ["I7", "ii7"],
            ["i", "v"],
            ["i", "i"],
            ["v", "v7"],
        ]

        opening_a = random.choice(openings)
        opening_b = random.choice(openings)
        harmony_a = random.choice(harmonic_starts)
        harmony_b = random.choice(harmonic_starts)

        section_a1 = self.compose_phrase(
            composer_name=composer_name,
            tonality=tonality,
            mode=mode,
            first_harmony_symbol=harmony_a[0],
            second_harmony_symbol=harmony_a[1],
            first_rhythm_symbol=opening_a[0],
            second_rhythm_symbol=opening_a[1],
            cadence=random.choice(["semicadence", "broken"]),
            rhythm_phrase="",
            anacrusis=True,
        )
        section_b = self.compose_phrase(
            composer_name=composer_name,
            tonality=key.Key("G"),
            mode=mode,
            first_harmony_symbol=harmony_b[0],
            second_harmony_symbol=harmony_b[1],
            first_rhythm_symbol=opening_b[0],
            second_rhythm_symbol=opening_b[1],
            cadence=random.choice(["perfect", "plagale"]),
            rhythm_phrase="",
            anacrusis=True,
        )
        section_a2 = self.compose_phrase(
            composer_name=composer_name,
            tonality=tonality,
            mode=mode,
            first_harmony_symbol=harmony_a[0],
            second_harmony_symbol=harmony_a[1],
            first_rhythm_symbol=opening_a[0],
            second_rhythm_symbol=opening_a[1],
            cadence="perfect",
            rhythm_phrase=section_a1[2],
            anacrusis=True,
        )

        complete_chords = list(section_a1[0]) + list(section_b[0]) + list(section_a2[0])
        complete_notes = list(section_a1[1]) + list(section_b[1]) + list(section_a2[1])
        return complete_chords, complete_notes

    @staticmethod
    def _number_of_chords(semiphrase_length: int, duration_chord: str) -> int:
        mapping = {
            "whole": 1,
            "half": 2,
            "quarter": 4,
            "eight": 8,
        }
        if duration_chord not in mapping:
            raise ValueError(f"Unsupported chord duration: {duration_chord}")
        return mapping[duration_chord] * semiphrase_length

    def _sample_first_semiphrase(self, trigram, bigram, tonality, first_symbol: str, number_of_chords: int, duration_chord: str):
        attempts = 0
        while True:
            result = self.harmony.get_harmony_from_trigram(
                trigram=trigram,
                bigram=bigram,
                tonality=tonality,
                first_symbol=first_symbol,
                number_chords=number_of_chords,
                duration=duration_chord,
            )
            last_symbol = result[1][-1].lower()
            if any(token in last_symbol for token in ["v", "v7", "ii7"]):
                return result
            attempts += 1
            if attempts >= 100:
                return result

    def _sample_second_semiphrase(self, trigram, bigram, tonality, first_symbol: str, number_of_chords: int, duration_chord: str, cadence: str):
        attempts = 0
        while True:
            result = self.harmony.get_harmony_from_trigram(
                trigram=trigram,
                bigram=bigram,
                tonality=tonality,
                first_symbol=first_symbol,
                number_chords=number_of_chords,
                duration=duration_chord,
            )
            if self._cadence_matches(result[1], cadence):
                return result
            attempts += 1
            if attempts >= 100:
                return result

    def _sample_rhythm(self, trigram, first_symbol: str, second_symbol: str, total_duration: float, anacrusis: bool, final_note_quarter_length: float):
        attempts = 0
        while True:
            result = self.rhythm.get_rhythm_from_trigram(
                trigram=trigram,
                first_symbol=first_symbol,
                second_symbol=second_symbol,
                total_duration=total_duration,
                anacrusis=anacrusis,
                final_note_quarter_length=final_note_quarter_length,
            )
            if result is not None:
                return result
            attempts += 1
            if attempts >= 100:
                raise RuntimeError("Unable to generate a valid rhythm after 100 attempts.")

    @staticmethod
    def _cadence_matches(symbols: list[str], cadence: str) -> bool:
        if len(symbols) < 2:
            return False
        penultimate = symbols[-2].lower()
        last = symbols[-1].lower()

        if cadence == "perfect":
            return ("v7" in penultimate or "v" in penultimate) and (last == "i" or last == "i7")
        if cadence == "plagale":
            return ("iv" in penultimate or "iv7" in penultimate) and (last == "i" or last == "i7")
        if cadence == "broken":
            return ("v7" in penultimate or "v" in penultimate) and ("vi7" in last or "ii7" in last)
        if cadence == "semicadence":
            return (
                any(token in penultimate for token in ["i", "i7", "iv", "iv7", "vi"])
                and any(token in last for token in ["v", "v7"])
            )
        return False
