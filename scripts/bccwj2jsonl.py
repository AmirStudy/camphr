import json
import xml.etree.ElementTree as ET
from collections import namedtuple
from pathlib import Path
from typing import *

import fire
import regex as re
from tqdm import tqdm

__dir__ = Path(__file__).parent
with open(__dir__/"ene2irexmap.json") as f:
    IREXMAP=json.load(f)

r = re.compile("<(?P<tag>[a-zA-Z-_]+)>(?P<body>.*?)</[a-zA-Z-_]+>")
rtag = re.compile("</?[a-zA-Z-_]+>")

Entry = namedtuple("Entry", ["text", "label"])


def convert(xml_string: str, mapping: Optional[Dict[str, str]] = None) -> Entry:
    offset = 0
    spans = []
    for t in r.finditer(xml_string):
        i = t.start()
        tag, body = t.groups()
        start = i - offset
        end = start + len(body)
        offset += 2 * len(tag) + 5
        if mapping:
            tag = IREXMAP.get(tag, "")
        if tag:
            spans.append((start, end, tag))
    notag = rtag.sub("", xml_string)
    return Entry(notag, {"entities": spans})


def check_conversion(item: Entry, xml_text, is_tag_removed=False) -> bool:
    text, label = item
    entities: List[Tuple[int, int, str]] = label["entities"]
    if not is_tag_removed:
        for (i, j, _), item in zip(entities, r.finditer(xml_text)):
            if text[i:j] != item.groups()[1]:
                return False

    try:
        a = ET.fromstring(f"<a>{xml_text}</a>")
    except:
        return False
    expected = ET.tostring(a, method="text", encoding="utf-8").decode()
    return expected == text


def preprocess(text: str) -> str:
    return text.replace("\u3000", "-")


def proc(
    xml_file: Union[Path, str], output_jsonl: Union[Path, str] = "", tag_mapping=""
) -> Tuple[int, List[Any]]:
    xml_file = Path(xml_file)
    failed = []
    if not output_jsonl:
        output_jsonl = xml_file.parent / (xml_file.stem + ".jsonl")
    else:
        output_jsonl = Path(output_jsonl)
    count = 0
    with xml_file.open() as f, output_jsonl.open("w") as fw:
        flag = False
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            if not flag:
                if line == "<TEXT>":
                    flag = True
                continue
            if line == "</TEXT>":
                break
            line = preprocess(line)
            for sent in line.split("。"):
                sent += "。"
                if tag_mapping == "irex":
                    ent = convert(sent, mapping=IREXMAP)
                else:
                    ent = convert(sent)
                if not check_conversion(ent, sent, is_tag_removed=tag_mapping != ""):
                    failed.append(f"{xml_file} {i} failed")
                    continue
                fw.write(json.dumps(ent, ensure_ascii=False) + "\n")
                count += 1
    return count, failed


def main(
    xml_dir: Union[str, Path],
    jsonl_dir: Union[str, Path],
    tag_mapping="",
    failed_log="log.txt",
):
    xml_dir = Path(xml_dir)
    jsonl_dir = Path(jsonl_dir)
    assert xml_dir.exists()
    fcount = 0
    itemcount = 0
    with open(failed_log, "w") as fw:
        for xml in tqdm(xml_dir.glob("**/*.xml")):
            outputpath = jsonl_dir / (str(xml).lstrip(str(xml_dir)) + ".jsonl")
            outputpath.parent.mkdir(exist_ok=True, parents=True)
            c, failed = proc(xml, outputpath, tag_mapping=tag_mapping)
            fw.write("\n".join(failed))
            itemcount += c
            fcount += 1
    print(f"{fcount} files, {itemcount} items parsed.")


if __name__ == "__main__":
    fire.Fire()
