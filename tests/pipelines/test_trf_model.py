import pytest
import torch
import numpy as np

from spacy.language import Language
from spacy_transformers.util import ATTRS
from spacy.tokens import Doc

from bedoner.models import bert_model


@pytest.fixture(scope="module", params=["mecab", "juman"], ids=["mecab", "juman"])
def nlp(request, bert_dir):
    return bert_model(lang=request.param, pretrained=bert_dir)


TESTCASES = ["今日はいい天気です", "今日は　いい天気です"]


@pytest.mark.parametrize("text", TESTCASES)
def test_forward(nlp, text):
    doc = nlp(text)
    assert doc._.trf_last_hidden_state is not None


@pytest.mark.parametrize("text", TESTCASES)
@pytest.mark.skipif(not torch.cuda.is_available(), reason="cuda test")
def test_forward_cuda(nlp, text):
    assert nlp.to(torch.device("cuda"))
    doc = nlp(text)
    assert doc._.trf_last_hidden_state is not None


@pytest.mark.parametrize("text", TESTCASES)
def test_token_vector(nlp: Language, text: str):
    doc: Doc = nlp(text)
    tensor: torch.Tensor = doc._.get(ATTRS.last_hidden_state).get()
    for token, a in zip(doc, doc._.get(ATTRS.alignment)):
        assert torch.allclose(token.vector, tensor[a].sum(0))


@pytest.mark.parametrize("text", TESTCASES)
def test_span_vector(nlp: Language, text: str):
    doc: Doc = nlp(text)
    assert torch.allclose(doc.vector, doc[:].vector)


@pytest.mark.parametrize(
    "text1,text2", [("今日はいい天気だった", "明日は晴れるかな"), ("今日はいい天気だった", "私は自然言語処理マスター")]
)
def test_doc_similarlity(nlp, text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    assert doc1.similarity(doc2)
    assert np.isclose(doc1.similarity(doc2), doc2.similarity(doc1))


@pytest.mark.parametrize(
    "tokens", [["今日は", "いい", "天気", "だ"], ["EXILE", "と", "海", "に", "行っ", "た"]]
)
def test_xlnet_model(xlnet_wp, xlnet_model, tokens):
    doc = Doc(xlnet_wp.vocab, tokens, spaces=[False] * len(tokens))
    doc = xlnet_wp(doc)
    doc = xlnet_model(doc)
    assert doc._.get(ATTRS.last_hidden_state).get() is not None
