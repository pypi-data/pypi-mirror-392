import logging

import typer
from rich.console import Console
from typing_extensions import Annotated

from devman.args import ARG_DST, ARG_FORCE_COVER_DST, ARG_QUIET, ARG_SRC, ARG_VERBOSE
from devman.helper.interactive import from_clipboard_or_file, to_clipboard_or_file
from devman.json.api import api_json_dump_obj_to_str, api_parse_str_to_json
from devman.log import config_log

app = typer.Typer()
console = Console()

ARG_RECURSIVE = Annotated[
    bool, typer.Option(help="是否递归去转义", show_default="默认递归")
]


@app.command("parse", help="解析字符串为 json(默认递归去转义)")
def recursive_parse_json(
    src: ARG_SRC = None,
    dst: ARG_DST = None,
    recursive: ARG_RECURSIVE = True,
    force: ARG_FORCE_COVER_DST = False,
    verbose: ARG_VERBOSE = False,
    quiet: ARG_QUIET = False,
):
    console.quiet = quiet
    if verbose:
        console.rule("解析 json 字符串")
        console.print("开启详细输出")
        config_log(logging.DEBUG)
    dump_content = None
    try:
        origin_content = from_clipboard_or_file(src)
        parsed_content = api_parse_str_to_json(origin_content, recursive)
        dump_content = api_json_dump_obj_to_str(parsed_content)
        to_clipboard_or_file(dst, dump_content, force, quiet)
    except AssertionError as e:
        console.print("断言错误", e)
    except Exception as e:
        console.print("未知异常", e)
        console.print("使用 -v 详细输出")
    console.print(dump_content)


if __name__ == "__main__":
    app()
