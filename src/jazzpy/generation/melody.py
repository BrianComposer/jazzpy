from __future__ import annotations

import random

from music21 import chord, note


class MelodyGenerator:
    """Melodic realization from rhythm and harmony."""

    def rhythm_to_melody(
        self,
        rhythms: list[note.NotRest],
        chords: list[chord.Chord],
    ) -> list[note.NotRest]:
        chord_boundaries: list[float] = []
        accumulated = 0.0
        previous_pitch_ps = 0.0

        for current_chord in chords:
            accumulated += current_chord.quarterLength
            chord_boundaries.append(accumulated)

        accumulated = 0.0
        for figure in rhythms:
            chord_index = self._chord_index_for_time(accumulated, chord_boundaries)
            if isinstance(figure, note.Note):
                figure.pitch = self.select_closest_note(previous_pitch_ps, chords[chord_index])
                previous_pitch_ps = figure.pitch.ps
            accumulated += figure.quarterLength

        return rhythms

    @staticmethod
    def clone_figure(figure):
        if isinstance(figure, chord.Chord):
            cloned = chord.Chord()
            for pitch in figure.pitches:
                cloned.add(str(pitch))
            cloned.duration.quarterLength = figure.quarterLength
            return cloned
        if isinstance(figure, note.Note):
            return note.Note(str(figure.pitch), quarterLength=figure.quarterLength)
        if isinstance(figure, note.Rest):
            return note.Rest(quarterLength=figure.quarterLength)
        raise TypeError(f"Unsupported figure type: {type(figure)!r}")

    @staticmethod
    def _chord_index_for_time(current_time: float, chord_boundaries: list[float]) -> int:
        for index, boundary in enumerate(chord_boundaries):
            if current_time < boundary:
                return index
        return len(chord_boundaries) - 1

    @staticmethod
    def select_closest_note(previous_pitch_ps: float, current_chord: chord.Chord):
        if previous_pitch_ps == 0:
            return random.choice(current_chord.pitches)

        best_candidate = None
        second_best_candidate = None
        best_distance = float("inf")
        second_distance = float("inf")

        for pitch in current_chord.pitches:
            base_note = note.Note(str(pitch))
            for octave in [3, 4, 5, 6]:
                base_note.pitch.octave = octave
                distance = abs(previous_pitch_ps - base_note.pitch.ps)
                if base_note.pitch.ps < 60 or base_note.pitch.ps >= 82:
                    continue
                if distance == 0:
                    continue
                if distance < best_distance:
                    second_best_candidate = best_candidate
                    second_distance = best_distance
                    best_candidate = note.Note(str(base_note.pitch))
                    best_distance = distance
                elif distance < second_distance and (best_candidate is None or base_note.pitch.ps != best_candidate.pitch.ps):
                    second_best_candidate = note.Note(str(base_note.pitch))
                    second_distance = distance

        if best_candidate is None:
            return random.choice(current_chord.pitches)
        if second_best_candidate is None:
            return best_candidate.pitch
        return random.choice([best_candidate.pitch, second_best_candidate.pitch])
