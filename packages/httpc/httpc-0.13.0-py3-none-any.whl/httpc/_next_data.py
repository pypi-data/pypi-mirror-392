# 편의상 "next data"라고 부르나 정식 명칭은 RSC payload임.

from __future__ import annotations

import json
import re
import typing

from ._base import logger

next_f_data = re.compile(r"self\.__next_f\.push\(\[\d+,\s*(.*)\]\)", re.DOTALL)
# HL, I, "$"가 각각 어떤 역할을 하는지 알려면 https://roy-jung.github.io/250323-react-server-components/ 이 코드 참고
line_regex = re.compile(r"^\s*(?P<hexdigit>[0-9a-fA-F]+):(?P<data_prefix>[A-Z]*)(?P<data_raw>.*)")


class NextData(typing.NamedTuple):
    line_no: int
    hexdigit: str
    prefix: str
    value: typing.Any
    parsed: bool


def extract_next_data(scripts: typing.Iterable[str], prefix_to_ignore: typing.Container[str] | None = None, warn_not_parsed: bool = False) -> list[NextData]:
    line: str
    next_data = []
    joined = ""
    for script in scripts:
        matched = next_f_data.match(script)
        if not matched:
            continue
        joined += json.loads(matched[1])

    for line_no, line in enumerate(joined.split("\n")):
        if not line:
            continue
        matched = line_regex.match(line)
        if not matched:
            raise ValueError(f"Line {line_no} does not match the expected format: {line!r}")

        hexdigit = matched["hexdigit"]
        data_prefix = matched["data_prefix"]
        data_raw = matched["data_raw"]
        if prefix_to_ignore and data_prefix in prefix_to_ignore:
            continue
        try:
            json_data = json.loads(data_raw)
        except json.JSONDecodeError:
            if warn_not_parsed:
                logger.warning(f"Failed to parse following data to JSON: {data_raw}")
            json_data = data_raw
            parsed = False
        else:
            parsed = True
        next_data.append(NextData(line_no, hexdigit, data_prefix, json_data, parsed))

    next_data.sort(key=lambda x: int(x.hexdigit, 16))
    return next_data
