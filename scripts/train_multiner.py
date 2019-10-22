import os
import logging
from pathlib import Path

import hydra
import torch

from .train import Config, create_data, train
from bedoner.ner_labels import LABELS
from bedoner.ner_labels.utils import make_biluo_labels
from bedoner.models import get_trf_name, trf_ner, trf_ner_layer
from spacy.language import Language

log = logging.getLogger(__name__)


def create_nlp(cfg: Config) -> Language:
    labels = make_biluo_labels(LABELS[cfg.label])
    nlp = trf_ner(lang=cfg.lang, pretrained=cfg.pretrained, labels=labels)
    toplabels = list({k.split("/")[0] for k in labels})
    ner = trf_ner_layer(
        lang=cfg.lang, pretrained=cfg.pretrained, vocab=nlp.vocab, labels=toplabels
    )
    ner.name = ner.name + "2"
    nlp.add_pipe(ner)
    name = get_trf_name(cfg.pretrained)
    nlp.meta["name"] = name.value + "_" + cfg.label
    return nlp


def _main(cfg: Config):
    log.info(cfg.pretty())
    log.info("output dir: {}".format(os.getcwd()))
    train_data, val_data = create_data(cfg)
    nlp = create_nlp(cfg)
    if torch.cuda.is_available():
        log.info("CUDA enabled")
        nlp.to(torch.device("cuda"))
    savedir = Path.cwd() / "models"
    savedir.mkdir()
    train(cfg, nlp, train_data, val_data, savedir)


main = hydra.main(config_path="conf/train.yml")(_main)

if __name__ == "__main__":
    main()
