from __future__ import annotations

from pathlib import Path
from typing import Iterable

from music21 import converter, note, roman, stream


class RawDataExtractor:
    """Extract symbolic harmonic and rhythmic sequences from a MusicXML corpus."""

    def get_harmonic_raw_data(
        self,
        works: Iterable[Path],
        mode: str = "harmony",
        test: bool = False,
        print_chords: bool = False,
    ) -> tuple[str, str, dict[str, int], dict[str, int]]:
        major_mode = ""
        minor_mode = ""
        major_chords: dict[str, int] = {}
        minor_chords: dict[str, int] = {}

        for work in works:
            try:
                score = converter.parse(str(work))
                detected_key = score.analyze("key")

                if mode.lower() == "harmony":
                    harmonies = score.parts[0].recurse().getElementsByClass("Harmony")
                    for harmony in harmonies:
                        numeral = roman.romanNumeralFromChord(harmony, detected_key)
                        if test:
                            _ = numeral.figure
                        self._accumulate_roman_figure(
                            numeral.figure,
                            detected_key.mode,
                            major_chords,
                            minor_chords,
                            print_chords=print_chords,
                        )
                        if detected_key.mode == "major":
                            major_mode += f" {numeral.figure}"
                        elif detected_key.mode == "minor":
                            minor_mode += f" {numeral.figure}"
                elif mode.lower() == "chordify":
                    chordified = score.chordify()
                    chords = chordified.recurse().getElementsByClass("Chord")
                    for current_chord in chords:
                        numeral = roman.romanNumeralFromChord(current_chord, detected_key)
                        self._accumulate_roman_figure(
                            numeral.figure,
                            detected_key.mode,
                            major_chords,
                            minor_chords,
                            print_chords=print_chords,
                        )
                        if detected_key.mode == "major":
                            major_mode += f" {numeral.figure}"
                        elif detected_key.mode == "minor":
                            minor_mode += f" {numeral.figure}"
            except Exception as exc:
                print(f"Failed to process harmonic data from {work}: {exc}")
                continue

        return major_mode, minor_mode, major_chords, minor_chords

    def get_rhythmic_raw_data(self, works: Iterable[Path]) -> tuple[str, dict[str, int]]:
        raw_data = ""
        figures: dict[str, int] = {}

        for work in works:
            try:
                score = converter.parse(str(work))
                for measure in score.parts[0].getElementsByClass(classFilterList=[stream.Measure]):
                    for element in measure.elements:
                        try:
                            if getattr(element.duration, "type", None) == "zero":
                                continue
                            token = self._duration_token(element)
                            raw_data += f" {token}"
                            figures[token] = figures.get(token, 0) + 1
                        except Exception:
                            continue
            except Exception as exc:
                print(f"Failed to process rhythmic data from {work}: {exc}")
                continue

        return raw_data, figures

    @staticmethod
    def _accumulate_roman_figure(
        figure: str,
        mode: str,
        major_chords: dict[str, int],
        minor_chords: dict[str, int],
        print_chords: bool = False,
    ) -> None:
        if mode == "major":
            major_chords[figure] = major_chords.get(figure, 0) + 1
        elif mode == "minor":
            minor_chords[figure] = minor_chords.get(figure, 0) + 1
        if print_chords:
            print(figure, end=" ")

    @staticmethod
    def _duration_token(element: note.NotRest) -> str:
        prefix = "R" if element.isRest else "N"
        return f"{prefix}{element.quarterLength}"
