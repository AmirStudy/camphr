import json
import tempfile

import pytest
import spacy
import torch
from spacy.gold import GoldParse
from spacy.language import Language

from bedoner.models import trf_ner
from bedoner.ner_labels.labels_ene import ALL_LABELS as enes
from bedoner.ner_labels.labels_irex import ALL_LABELS as irexes
from bedoner.ner_labels.utils import make_biluo_labels


label_types = ["ene", "irex"]


@pytest.fixture(scope="module", params=label_types)
def label_type(request):
    return request.param


@pytest.fixture(scope="module")
def labels(label_type):
    if label_type == "ene":
        return make_biluo_labels(enes)
    elif label_type == "irex":
        return make_biluo_labels(irexes)
    else:
        raise ValueError


@pytest.fixture(scope="module", params=["mecab", "juman", "sentencepiece"])
def nlp(labels, request, trf_dir):
    lang = request.param
    if lang == "sentencepiece" and "xlnet" not in trf_dir:
        pytest.skip()
    _nlp = trf_ner(lang=lang, labels=["-"] + labels, pretrained=trf_dir)
    assert _nlp.meta["lang"] == lang
    return _nlp


TESTCASE_ENE = [
    (
        "ＥＸＩＬＥのＡＴＳＵＳＨＩと中島美嘉が１４日ニューヨーク入り",
        {
            "entities": [
                (0, 5, "SHOW_ORGANIZATION"),
                (6, 13, "PERSON"),
                (14, 18, "PERSON"),
                (19, 22, "DATE"),
                (22, 28, "CITY"),
            ]
        },
    ),
    (
        "夏休み真っただ中の8月26日の夕方。",
        {"entities": [(0, 3, "DATE"), (9, 14, "DATE"), (15, 17, "TIME")]},
    ),
    ("。", {"entities": []}),
    (" おはよう", {"entities": []}),
    ("　おはよう", {"entities": []}),
]


@pytest.mark.parametrize("text,gold", TESTCASE_ENE)
def test_call(nlp: Language, text, gold, label_type):
    if label_type == "irex":
        pytest.skip()
    nlp(text)


def test_pipe(nlp: Language):
    list(nlp.pipe(["今日はいい天気なので外で遊びたい", "明日は晴れ"]))


@pytest.mark.parametrize("text,gold", TESTCASE_ENE)
def test_update(nlp: Language, text, gold, label_type):
    if label_type == "irex":
        pytest.skip()
    assert nlp.device.type == "cpu"
    doc = nlp(text)
    gold = GoldParse(doc, **gold)

    optim = nlp.resume_training()
    assert nlp.device.type == "cpu"
    doc = nlp.make_doc(text)
    assert doc._.loss is None
    nlp.update([doc], [gold], optim)
    assert doc._.loss


def test_update_batch(nlp: Language, label_type):
    if label_type == "irex":
        pytest.skip()
    texts, golds = zip(*TESTCASE_ENE)
    optim = nlp.resume_training()
    nlp.update(texts, golds, optim)


def test_evaluate(nlp: Language, label_type):
    if label_type == "irex":
        pytest.skip()
    nlp.evaluate(TESTCASE_ENE)


def test_save_and_load(nlp: Language, label_type):
    if label_type == "irex":
        pytest.skip()
    with tempfile.TemporaryDirectory() as d:
        nlp.to_disk(d)
        nlp = spacy.load(d)
        nlp(TESTCASE_ENE[0][0])


TESTCASE2 = ["資生堂の香水-禅とオードパルファンＺＥＮの違いを教えて下さい。また今でも製造されてますか？"]


@pytest.fixture
def cuda():
    return torch.device("cuda")


@pytest.mark.skipif(not torch.cuda.is_available(), reason="cuda test")
@pytest.mark.parametrize("text,gold", TESTCASE_ENE)
def test_call_cuda(nlp: Language, text, gold, cuda, label_type):
    if label_type == "irex":
        pytest.skip()
    nlp.to(cuda)
    nlp(text)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="cuda test")
@pytest.mark.parametrize("text,gold", TESTCASE_ENE)
def test_update_cuda(nlp: Language, text, gold, cuda, label_type):
    if label_type == "irex":
        pytest.skip()
    nlp.to(cuda)
    doc = nlp(text)
    gold = GoldParse(doc, **gold)

    optim = nlp.resume_training()
    doc = nlp.make_doc(text)
    assert doc._.loss is None
    nlp.update([doc], [gold], optim)
    assert doc._.loss


@pytest.mark.skipif(not torch.cuda.is_available(), reason="cuda test")
def test_update_batch_cuda(nlp: Language, cuda, label_type):
    if label_type == "irex":
        pytest.skip()
    nlp.to(cuda)
    texts, golds = zip(*TESTCASE_ENE)
    optim = nlp.resume_training()
    nlp.update(texts, golds, optim)


@pytest.fixture(
    scope="module",
    params=["ner/ner-ene.json", "ner/ner-irex.json", "ner/ner-ene2.json"],
)
def example_gold(request, DATADIR, label_type):
    fname = request.param
    if label_type in fname:
        with (DATADIR / fname).open() as f:
            d = json.load(f)
        return d
    else:
        pytest.skip()


@pytest.fixture(scope="module", params=["ner/ner-irex-long.json"])
def example_long(request, DATADIR, label_type, trf_name):
    fname = request.param
    if trf_name == "bert" and label_type in fname:
        with (DATADIR / fname).open() as f:
            d = json.load(f)
        return d
    else:
        pytest.skip()


def test_example_batch(nlp: Language, example_gold):
    texts, golds = zip(*example_gold)
    optim = nlp.resume_training()
    nlp.update(texts, golds, optim)


def test_example_batch_eval(nlp: Language, example_gold):
    nlp.evaluate(example_gold)


def test_long_input(nlp: Language, example_long):
    texts, golds = zip(*example_long)
    optim = nlp.resume_training()
    with pytest.raises(ValueError):
        nlp.update(texts, golds, optim)
