"""Copied from Spacy"""
import pytest

from ...utils import check_knp


@pytest.mark.skipif(not check_knp(), reason="knp is not always necessary")
@pytest.mark.parametrize(
    "word,lemma",
    [("新しく", "新しい"), ("赤く", "赤い"), ("すごく", "すごい"), ("いただきました", "いただく"), ("なった", "なる")],
)
def test_mecab_lemmatizer_assigns(knp_tokenizer, word, lemma):
    test_lemma = knp_tokenizer(word)[0].lemma_
    assert test_lemma == lemma
