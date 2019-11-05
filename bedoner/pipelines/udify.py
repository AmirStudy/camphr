"""Pipe of '75 Languages, 1 Model: Parsing Universal Dependencies Universally' (https://arxiv.org/abs/1904.02099)"""
from typing import Dict, Iterable

import spacy
import spacy.language
from allennlp.common.util import import_submodules
from spacy.tokens import Doc, Token

from bedoner.vendor.udify.models.udify_model import OUTPUTS as UdifyOUTPUTS

from .allennlp_base import AllennlpPipe
from .utils import set_heads

spacy.language.ENABLE_PIPELINE_ANALYSIS = True

import_submodules("bedoner.vendor.udify")


@spacy.component(
    "udify", assigns=["token.lemma", "token.dep", "token.pos", "token.head"]
)
class Udify(AllennlpPipe):
    def set_annotations(self, docs: Iterable[Doc], outputs: Dict):
        for doc, output in zip(docs, outputs):
            deps = output[UdifyOUTPUTS.predicted_dependencies]
            heads = output[UdifyOUTPUTS.predicted_heads]
            uposes = output[UdifyOUTPUTS.upos]
            lemmas = output[UdifyOUTPUTS.lemmas]
            words = output[UdifyOUTPUTS.words]
            _doc_tokens = [token.text for token in doc]
            if not words == [token.text for token in doc]:
                raise ValueError(
                    "Internal error has occured."
                    f"Input text: {doc.text}\n"
                    f"Input tokens: {_doc_tokens}\n"
                    f"Model words: {words}"
                )

            for token, dep, upos, lemma in zip(doc, deps, uposes, lemmas):
                token: Token = token
                token.dep_ = dep
                token.lemma_ = lemma
                token.pos_ = upos
            doc = set_heads(doc, heads)
            doc.is_parsed = True
