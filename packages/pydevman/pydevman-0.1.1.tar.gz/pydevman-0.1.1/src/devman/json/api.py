import json
import re
from datetime import datetime
from typing import Union

from devman.json.core import parse_str, recursive_parse


def api_json_dump_obj_to_str(obj: Union[dict, list]):
    return json.dumps(obj, indent=2, ensure_ascii=False)


def api_parse_str_to_json(
    arg: str, recursive: bool
) -> Union[dict, list, str, int, float]:
    # 递归解析
    if recursive:
        return recursive_parse(arg)
    # 正常解析
    return parse_str(arg)


def get_possible_datetime_from_str(line: str) -> datetime:
    raise NotImplementedError("Not Finish.")
    dt_pat = re.compile(r"(\d{4}-?\d{2}-?\d{2}\s?\d{2}:?\d{2}:?\d{2}(\.\d{3})?)")
    return dt_pat


def get_possible_json_from_str(line: str) -> dict:
    raise NotImplementedError("Not Finish.")
    json_pat = re.compile(r"(?<!#)(\[?{.*}\]?)(?!#)")
    return json_pat


def parse_lines(lines: list[str]) -> list:
    raise NotImplementedError("Not Finish.")
    res = []
    for idx, line in enumerate(lines):
        get_possible_datetime_from_str(line)
        get_possible_json_from_str(line)
    return res
