import pytest
from bedoner.lang.mecab import Japanese
from bedoner.entity_rulers import create_person_ruler
import bedoner.ner_labels.labels_ontonotes as L
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from collections import namedtuple


TESTS = [("今日は高松隆と海に行った", "高松隆"), ("今日は田中と海に行った", "田中")]


@pytest.mark.parametrize("text,ent", TESTS)
def test_person_entity_ruler(text: str, ent: str):
    nlp = Japanese()
    nlp.add_pipe(create_person_ruler(nlp))

    doc: Doc = nlp(text)
    assert len(doc.ents) == 1
    span: Span = doc.ents[0]
    assert span.text == ent
    assert span.label_ == L.PERSON
