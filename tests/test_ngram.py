from jazzpy.core.ngram import NgramModel


def test_bigram_counting() -> None:
    tokens = ["I", "V", "I", "ii"]
    counts = NgramModel.get_bigram(tokens)
    assert counts[("I", "V")] == 1
    assert counts[("V", "I")] == 1
    assert counts[("I", "ii")] == 1
