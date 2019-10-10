# v0.2

- change dependency
  - pytorch-transformers -> transformers
  - spacy-pytorch-transformers - > pytorch-transformers
- gpu support

```
nlp.to(torch.device("cuda"))
```

- python3.6 conpatibility
- training script: scripts/train.py

# v0.1.1

- mecabについて，urlを1トークンとして扱うようにした (#42)
- regex_ruler の追加 (#43)
- postcoder ruler の追加 (#43)
- matcher_ruler の追加 (#45)
- person_ner, date_ner について，LABELをexport
- `bedoner.__version__` の追加

# v0.1

- mecab, juman, knp Language について，スペースの取り扱いを改善
  - tokenにスペースは含めないが，`doc.text`には含まれる