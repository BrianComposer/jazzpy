from __future__ import annotations

from .ngram import NgramModel


class LaplaceSmoothing:
    """Laplace smoothing utilities for custom n-gram models."""

    @staticmethod
    def smoothing_bigram_zero(
        unigram: dict[str, int],
        bigram: dict[tuple[str, str], int],
        alpha: float,
    ) -> dict[str, float]:
        smoothed: dict[str, float] = {}
        vocabulary = list(unigram.keys())
        denominator_size = float(len(vocabulary))
        for token1 in vocabulary:
            total = 0.0
            for token2 in vocabulary:
                total += bigram.get((token1, token2), 0)
            smoothed[token1] = alpha / (total + alpha * denominator_size)
        return smoothed

    @staticmethod
    def smoothing_trigram_zero(
        unigram: dict[str, int],
        trigram: dict[tuple[str, str, str], int],
        alpha: float,
    ) -> dict[tuple[str, str], float]:
        smoothed: dict[tuple[str, str], float] = {}
        vocabulary = list(unigram.keys())
        denominator_size = float(len(vocabulary))
        for token1 in vocabulary:
            for token2 in vocabulary:
                total = 0.0
                for token3 in vocabulary:
                    total += trigram.get((token1, token2, token3), 0)
                smoothed[(token1, token2)] = alpha / (total + alpha * denominator_size)
        return smoothed

    @staticmethod
    def calculate_bigram_probability_laplace(
        unigram: dict[str, int],
        bigram: dict[tuple[str, str], int],
        alpha: float,
    ) -> dict[tuple[str, str], float]:
        probabilities: dict[tuple[str, str], float] = {}
        vocabulary_size = len(unigram)
        for token in unigram:
            subset = NgramModel.sub_bigram(bigram, token)
            total = sum(float(value) for value in subset.values())
            for key, value in subset.items():
                probabilities[key] = (float(value) + alpha) / (total + alpha * vocabulary_size)
        return probabilities

    @staticmethod
    def calculate_trigram_probability_laplace(
        unigram: dict[str, int],
        trigram: dict[tuple[str, str, str], int],
        alpha: float,
    ) -> dict[tuple[str, str, str], float]:
        probabilities: dict[tuple[str, str, str], float] = {}
        vocabulary = list(unigram.keys())
        vocabulary_size = len(vocabulary)
        for token1 in vocabulary:
            for token2 in vocabulary:
                subset = NgramModel.sub_trigram(trigram, token1, token2)
                total = sum(float(value) for value in subset.values())
                for key, value in subset.items():
                    probabilities[key] = (float(value) + alpha) / (total + alpha * vocabulary_size)
        return probabilities
