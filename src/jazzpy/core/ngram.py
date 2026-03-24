from __future__ import annotations

import random
from collections import Counter
from typing import Iterable


Token = str
Bigram = tuple[str, str]
Trigram = tuple[str, str, str]


class NgramModel:
    """Custom token counting and sampling utilities without external NLP libraries."""

    @staticmethod
    def get_tokens(text: str) -> list[str]:
        return text.split()

    @staticmethod
    def remove_stop_words(tokens: list[str], stop_words: Iterable[str]) -> list[str]:
        stop_set = set(stop_words)
        return [token for token in tokens if token not in stop_set]

    @staticmethod
    def filter_most_frequent_tokens(tokens: list[str], max_number: int) -> list[str]:
        counts = Counter(tokens)
        selected = {token for token, _ in counts.most_common(max_number)}
        return [token for token in tokens if token in selected]

    @staticmethod
    def get_unigram(tokens: list[str]) -> dict[Token, int]:
        return dict(Counter(tokens))

    @staticmethod
    def get_bigram(tokens: list[str]) -> dict[Bigram, int]:
        counts: Counter[Bigram] = Counter()
        for index in range(len(tokens) - 1):
            counts[(tokens[index], tokens[index + 1])] += 1
        return dict(counts)

    @staticmethod
    def get_trigram(tokens: list[str]) -> dict[Trigram, int]:
        counts: Counter[Trigram] = Counter()
        for index in range(len(tokens) - 2):
            counts[(tokens[index], tokens[index + 1], tokens[index + 2])] += 1
        return dict(counts)

    @staticmethod
    def calculate_bigram_probability(
        unigram: dict[Token, int],
        bigram: dict[Bigram, int],
    ) -> dict[Bigram, float]:
        probabilities: dict[Bigram, float] = {}
        for token in unigram:
            subset = NgramModel.sub_bigram(bigram, token)
            total = sum(subset.values())
            for key, value in subset.items():
                probabilities[key] = (value / total) if total else 0.0
        return probabilities

    @staticmethod
    def calculate_trigram_probability(
        unigram: dict[Token, int],
        trigram: dict[Trigram, int],
    ) -> dict[Trigram, float]:
        probabilities: dict[Trigram, float] = {}
        vocabulary = list(unigram.keys())
        for token1 in vocabulary:
            for token2 in vocabulary:
                subset = NgramModel.sub_trigram(trigram, token1, token2)
                total = sum(subset.values())
                for key, value in subset.items():
                    probabilities[key] = (value / total) if total else 0.0
        return probabilities

    @staticmethod
    def sub_bigram(values: dict[Bigram, float | int], token: str) -> dict[Bigram, float | int]:
        return {key: value for key, value in values.items() if key[0] == token}

    @staticmethod
    def sub_trigram(
        values: dict[Trigram, float | int],
        token1: str,
        token2: str,
    ) -> dict[Trigram, float | int]:
        return {key: value for key, value in values.items() if key[0] == token1 and key[1] == token2}

    @staticmethod
    def weighted_choice(subgram: dict[tuple[str, ...], float | int]) -> str:
        if not subgram:
            raise ValueError("Cannot sample from an empty n-gram subset.")

        keys = list(subgram.keys())
        weights = [float(subgram[key]) for key in keys]
        total = sum(weights)

        if total <= 0.0:
            return random.choice(keys)[-1]

        threshold = random.random() * total
        cumulative = 0.0
        for key, weight in zip(keys, weights, strict=False):
            cumulative += weight
            if threshold <= cumulative:
                return key[-1]
        return keys[-1][-1]
