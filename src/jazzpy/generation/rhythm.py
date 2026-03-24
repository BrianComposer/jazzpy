from __future__ import annotations

from music21 import note

from jazzpy.core.ngram import NgramModel


class RhythmGenerator:
    """Rhythmic generation from symbolic tokens."""

    def __init__(self) -> None:
        self.ngram = NgramModel()

    def get_rhythm_from_bigram(
        self,
        bigram: dict[tuple[str, str], float],
        start_symbol: str,
        total_duration: float,
    ) -> list[note.NotRest]:
        note_list: list[note.NotRest] = []
        current_duration = 0.0
        current_symbol = start_symbol

        for item in self.create_note_or_rest(current_symbol):
            note_list.append(item)
            current_duration += item.quarterLength

        while current_duration < total_duration:
            subset = self.ngram.sub_bigram(bigram, current_symbol)
            current_symbol = self.ngram.weighted_choice(subset)
            for item in self.create_note_or_rest(current_symbol):
                note_list.append(item)
                current_duration += item.quarterLength
        return note_list

    def get_rhythm_from_trigram(
        self,
        trigram: dict[tuple[str, str, str], float],
        first_symbol: str,
        second_symbol: str,
        total_duration: float,
        anacrusis: bool,
        final_note_quarter_length: float,
    ) -> tuple[list[note.NotRest], list[str]] | None:
        note_list: list[note.NotRest] = []
        symbol_list: list[str] = []
        current_duration = 0.0
        silence_duration = 0.0
        max_duration = total_duration - final_note_quarter_length
        iteration = 0

        if anacrusis:
            for item in self.create_note_or_rest("R1.0"):
                note_list.append(item)
                current_duration += item.quarterLength
            symbol_list.append("R1.0")

        for symbol in (first_symbol, second_symbol):
            for item in self.create_note_or_rest(symbol):
                note_list.append(item)
                current_duration += item.quarterLength
            symbol_list.append(symbol)

        symbol1 = first_symbol
        symbol2 = second_symbol

        while current_duration < max_duration:
            subset = self.ngram.sub_trigram(trigram, symbol1, symbol2)
            if not subset:
                return None
            symbol3 = self.ngram.weighted_choice(subset)

            if self.check_tuplet_to_beat(current_duration, symbol3) and self.check_silence(silence_duration, symbol3):
                new_items = self.create_note_or_rest(symbol3)
                buffered_duration = current_duration + sum(item.quarterLength for item in new_items)
                if buffered_duration <= max_duration:
                    for item in new_items:
                        note_list.append(item)
                        current_duration += item.quarterLength
                        silence_duration = silence_duration + item.quarterLength if symbol3.startswith("R") else 0.0
                    symbol_list.append(symbol3)
                    symbol1, symbol2 = symbol2, symbol3

            iteration += 1
            if iteration == 50:
                return None

        if final_note_quarter_length > 0:
            symbol = f"N{final_note_quarter_length}"
            final_items = self.create_note_or_rest(symbol)
            for item in final_items:
                note_list.append(item)
                current_duration += item.quarterLength
            symbol_list.append(symbol)

        return note_list, symbol_list

    @staticmethod
    def create_note_or_rest(symbol: str) -> list[note.NotRest]:
        figures: list[note.NotRest] = []
        prefix = symbol[0]
        payload = symbol[1:]

        if "/" in payload:
            numerator_str, denominator_str = payload.split("/")
            numerator = float(numerator_str)
            denominator = float(denominator_str)
            duration = numerator / denominator
            repetitions = int(denominator)
        else:
            duration = float(payload)
            repetitions = 1

        for _ in range(repetitions):
            if prefix == "N":
                figures.append(note.Note("C", quarterLength=duration))
            elif prefix == "R":
                figures.append(note.Rest(quarterLength=duration))
            else:
                raise ValueError(f"Unsupported rhythmic symbol: {symbol}")

        return figures

    @staticmethod
    def check_tuplet_to_beat(accumulated_duration: float, symbol: str) -> bool:
        if "/" not in symbol:
            return True

        payload = symbol.replace("N", "").replace("R", "")
        numerator_str, _ = payload.split("/")
        numerator = float(numerator_str)

        if numerator == 1:
            return accumulated_duration % 1 == 0
        if numerator == 2:
            return accumulated_duration % 2 == 0
        if numerator == 4:
            return accumulated_duration % 4 == 0
        return False

    @staticmethod
    def check_silence(accumulated_silence_duration: float, symbol: str) -> bool:
        if symbol.startswith("R") and accumulated_silence_duration >= 1.5:
            return False
        return True
