# Kawaii Traceback

[![PyPI Version](https://img.shields.io/pypi/v/kawaii-traceback)](https://pypi.org/project/kawaii-traceback/)
[![Python Versions](https://img.shields.io/pypi/pyversions/kawaii-traceback)](https://pypi.org/project/kawaii-traceback/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

一个可爱的Python异常美化工具，提供更友好的错误提示和多语言支持

## ✨ 特性

- 可爱的异常输出格式
- 智能错误建议（拼写检查、导入提示、Traceback简化等）及可扩展性
- 高度的多语言可扩展性
- 高度可定制的提示信息（甚至可以对自定义场景自定义提示）
- 兼容标准Python traceback模块

## 📦 安装

```bash
pip install kawaii-traceback
```

## 🚀 快速开始

```python
import kawaiitb.autoload  # noqa

# 现在所有异常都会以可爱的方式显示
1 / 0
```

## 🌍 多语言支持

“语言”实际上是广义语言的扩展，你可以通过自定义新的语言来自定义提示的风格

```python
# 加载中文提示
import kawaiitb

kawaiitb.load('zh_hans')

# 或者加载猫娘版提示
kawaiitb.load('neko_zh')
```

## 🛠 配置

创建 `mytb.json` 配置文件：

```json
{
  "translate_keys": {
    "my_neko": {
      "extend": "zh_hans",
      "native.ZeroDivisionError.msg": "{divisor}变成零了喵！不能除以零喵不能除以零喵！",
      "native.AttributeError.premsg": "{type_} 类型的 '{obj}' 没有属性 '{name}' 喵！"
    }
  },
  "default_lang": "my_neko"
}
```
然后使用 `kawaiitb.load(file='mytb.json')` 加载配置。

## 🤝 贡献

欢迎提交Issue和PR！请确保：
1. 开发新功能前请先创建Issue
2. 代码需与已有风格一致
3. 添加相应的测试用例

## 📜 许可证

本项目基于MIT许可证。请查看[LICENSE](LICENSE)文件以获取更多信息。
