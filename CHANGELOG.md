# v0.3

milestone: https://github.com/PKSHATechnology/bedore-ner/milestone/1?closed=1

##  New features and improvements

- BERTベースのモデルを[新たに6種類リリース](https://github.com/PKSHATechnology/bedore-ner/releases/tag/v0.3.0.dev2)
  - mecab ner (ene, irex)
  - juman ner (ene, irex)
  - mecab, juman pretrained model
- BERT modelについて, 埋め込みベクトル`vector`およびコサイン類似度`similarity`機能を追加
  - 使い方: [docs/usage/pipelines.md#BERT](./docs/usage/pipelines.md#BERT)
- mecab, jumanの依存を外しました (#44)
  - これらに依存する機能を使いたい場合，個別にインストールする必要があります．
- gold dataの分割スクリプトを追加 (参考: https://github.com/PKSHATechnology/bedore-ner/blob/version%2Fv0.3/docs/usage/cli.md)
- model packagingのversionup scriptを追加 [scripts/versionup-package](scripts/versionup-package)(#60)
- model package用のテストスクリプトを追加([scripts/test-package.sh](./scripts/test-package.sh)) (#9)
- NERのラベルづけがoverlapする際に有用なutil `pipelines.utils.merge_entities`を追加 (#63)
 
## Bug fixes

- trf nerに全角スペースが入力エラーにならないようにしました (#15)
- mecabについて，全角スペースを半角スペースと同様に扱うようにしました (#39)

## Documentation and examples

- [docs](./docs)ディレクトリにドキュメントをいくつか追加．
  - 概要: [docs/README.md](./docs/README.md)

## Refactor

- `pipelines.date_ner`をregex_rulerに統合(#61)
- scripts directoryを整理
- removed MatcherRuler (#62)
  - spacyの`EntityRuler`を使いましょう．

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