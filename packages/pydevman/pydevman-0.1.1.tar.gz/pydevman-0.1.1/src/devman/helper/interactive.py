import logging
from pathlib import Path

import pyperclip
from rich.console import Console

from devman.common import assert_path_exist_and_is_file

log = logging.getLogger(__name__)
console = Console()


def confirm() -> bool:
    while True:
        flag = input("是否继续(y/n)...").strip().lower()  # 获取用户输入并处理为小写
        if flag.startswith("y"):  # 如果以'y'开头
            log.info("继续执行...")
            return True
        elif flag.startswith("n"):  # 如果以'n'开头
            log.info("退出程序...")
            return False
        log.info("无效输入，请输入'y'或'n'。")  # 提示用户输入无效，继续询问


def from_clipboard_or_file(src: Path) -> str:
    if src is None:
        return pyperclip.paste()
    assert_path_exist_and_is_file(src)
    return src.read_text()


def to_clipboard_or_file(dst: Path, content: str, force: bool, quiet=False) -> bool:
    # 写入剪贴板
    console.quiet = quiet
    if dst is None:
        pyperclip.copy(content)
        console.print("已复制到剪贴板")
        return
    # dst 非空,路径
    if dst.exists() and force:
        dst.write_text(content)
        console.print(f"已写入文件 {dst.name}")
    else:
        console.print(f"目标文件 {dst.name} 已存在，使用 -f 强制输出")
