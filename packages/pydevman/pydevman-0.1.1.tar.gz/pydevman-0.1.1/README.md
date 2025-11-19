# PY DEV MAN

开发者的 python 工具集

## 如何安装

```sh
pip install pydevman
# 测试命令
dev echo hello
# 查看所有子应用
dev --help
# 查看某个子应用的所有命令
dev json --help
# 查看某个子应用某个命令的使用方法
dev json parse --help
```

## 子应用 ECHO

此应用主要用于测试使用

## 子应用 JSON

此应用主要和 json 相关

```sh
# 将剪贴板中的内容递归解析，并输出到剪贴板
dev json parse
```

## 子应用 FILE
