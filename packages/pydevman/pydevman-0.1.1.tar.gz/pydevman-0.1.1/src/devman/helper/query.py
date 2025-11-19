from pathlib import Path
from typing import Callable

import inquirer

from devman.helper.cache import JsonCache

cache = JsonCache(Path(".cache", "cache.json"))


def query_list(func: str, name: str, msg: str, validate: Callable = None):
    choices = cache.arg_get_list(func, name)
    if choices:
        res = inquirer.list_input(msg, choices=choices, other=True)
    else:
        res = inquirer.text(msg)
    # if validate and validate(res):
    if validate is None or validate(res):
        cache.arg_upsert(func, name, res)
    return res


def query_check(func: str, name: str, msg: str):
    choices = cache.arg_get_list(func, name)
    res = inquirer.checkbox(msg, choices=choices, other=True)
    cache.arg_upsert_list(func, name, res)
    return res
