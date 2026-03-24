from __future__ import annotations

from music21 import chord, note, roman

from jazzpy.core.ngram import NgramModel


class HarmonyGenerator:
    """Harmony generation and simple voice-leading utilities."""

    def __init__(self) -> None:
        self.ngram = NgramModel()

    @staticmethod
    def get_chord_pitches(symbol: str, tonality) -> list:
        return list(roman.RomanNumeral(symbol, tonality).pitches)

    def get_harmony_from_bigram(
        self,
        bigram: dict[tuple[str, str], float],
        tonality,
        first_symbol: str,
        number_chords: int,
        duration: str,
    ) -> tuple[list[chord.Chord], list[str]]:
        chord_list: list[chord.Chord] = []
        symbol_list: list[str] = []

        current_symbol = first_symbol
        for _ in range(number_chords):
            current_chord = chord.Chord(self.get_chord_pitches(current_symbol, tonality))
            current_chord.duration.type = duration
            chord_list.append(current_chord)
            symbol_list.append(current_symbol)
            subset = self.ngram.sub_bigram(bigram, current_symbol)
            if subset:
                current_symbol = self.ngram.weighted_choice(subset)
        return chord_list, symbol_list

    def get_harmony_from_trigram(
        self,
        trigram: dict[tuple[str, str, str], float],
        bigram: dict[tuple[str, str], float],
        tonality,
        first_symbol: str,
        number_chords: int,
        duration: str,
    ) -> tuple[list[chord.Chord], list[str]]:
        chord_list: list[chord.Chord] = []
        symbol_list: list[str] = []

        chord_1 = chord.Chord(self.get_chord_pitches(first_symbol, tonality))
        chord_1.duration.type = duration
        chord_list.append(chord_1)
        symbol_list.append(first_symbol)

        second_subset = self.ngram.sub_bigram(bigram, first_symbol)
        second_symbol = self.ngram.weighted_choice(second_subset) if second_subset else first_symbol
        chord_2 = chord.Chord(self.get_chord_pitches(second_symbol, tonality))
        chord_2.duration.type = duration
        chord_list.append(chord_2)
        symbol_list.append(second_symbol)

        symbol1 = first_symbol
        symbol2 = second_symbol

        for _ in range(max(0, number_chords - 2)):
            subset = self.ngram.sub_trigram(trigram, symbol1, symbol2)
            symbol3 = self.ngram.weighted_choice(subset) if subset else symbol2
            chord_3 = chord.Chord(self.get_chord_pitches(symbol3, tonality))
            chord_3.duration.type = duration
            chord_list.append(chord_3)
            symbol_list.append(symbol3)
            symbol1 = symbol2
            symbol2 = symbol3

        return chord_list, symbol_list

    def voice_leading(self, chords: list[chord.Chord]) -> None:
        for current_chord in chords:
            self._normalize_to_four_voices(current_chord)

        for index in range(1, len(chords)):
            current = chords[index]
            previous = chords[index - 1]
            best_octaves = [pitch.octave for pitch in current.pitches]
            found = False
            minimum_distance = float("inf")

            for o0 in range(1, 9):
                current.pitches[0].octave = o0
                for o1 in range(1, 9):
                    current.pitches[1].octave = o1
                    for o2 in range(1, 9):
                        current.pitches[2].octave = o2
                        for o3 in range(1, 9):
                            current.pitches[3].octave = o3
                            distance = self.distance_chord_dense(current, previous)
                            if distance < minimum_distance:
                                if (
                                    self.check_voice_tessitures(current)
                                    and self.check_voice_disposition(current)
                                    and self.check_parallel_movement(previous, current)
                                    and self.check_voice_crossings(current)
                                ):
                                    minimum_distance = distance
                                    best_octaves = [o0, o1, o2, o3]
                                    found = True

            if not found:
                print(f"No valid disposition was found for chord {index}: {current}")

            for pitch, octave in zip(current.pitches, best_octaves, strict=False):
                pitch.octave = octave

    @staticmethod
    def _normalize_to_four_voices(current_chord: chord.Chord) -> None:
        if len(current_chord.pitches) == 2:
            n1 = note.Note()
            n1.pitch = current_chord.pitches[1]
            n2 = note.Note()
            n2.pitch = current_chord.root()
            current_chord.add(n1)
            current_chord.add(n2)
        elif len(current_chord.pitches) == 3:
            bass = note.Note(str(current_chord.root()))
            bass.octave -= 1
            current_chord.add(bass)
        elif len(current_chord.pitches) == 5:
            current_chord.remove(current_chord.fifth)
        elif len(current_chord.pitches) > 5:
            print(f"Chord with more than five notes found: {current_chord}")

    @staticmethod
    def distance_chord(chord1: chord.Chord, chord2: chord.Chord) -> float:
        return sum(abs(chord1.pitches[i].ps - chord2.pitches[i].ps) for i in range(1, 4))

    @staticmethod
    def distance_chord_dense(chord1: chord.Chord, chord2: chord.Chord) -> float:
        return sum(
            abs(chord1.pitches[i].ps - chord2.pitches[j].ps)
            for i in range(4)
            for j in range(4)
        )

    @staticmethod
    def check_voice_tessitures(current_chord: chord.Chord) -> bool:
        return (
            40 < current_chord.pitches[0].ps <= 60
            and 48 < current_chord.pitches[1].ps <= 69
            and 52 < current_chord.pitches[2].ps <= 76
            and 64 < current_chord.pitches[3].ps <= 81
        )

    @staticmethod
    def check_voice_crossings(current_chord: chord.Chord) -> bool:
        return (
            current_chord.pitches[0].ps < current_chord.pitches[1].ps
            < current_chord.pitches[2].ps
            < current_chord.pitches[3].ps
        )

    @staticmethod
    def check_voice_disposition(current_chord: chord.Chord) -> bool:
        return (
            abs(current_chord.pitches[1].ps - current_chord.pitches[2].ps) <= 12
            and abs(current_chord.pitches[2].ps - current_chord.pitches[3].ps) <= 12
        )

    @staticmethod
    def check_parallel_movement(chord1: chord.Chord, chord2: chord.Chord) -> bool:
        movements = [chord2.pitches[i].ps - chord1.pitches[i].ps for i in range(4)]
        if all(value > 0 for value in movements) or all(value < 0 for value in movements):
            return False
        return True
