from typing import Generator

from kawaiitb.kraceback import KTBException
from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc
from kawaiitb.utils import safe_string


@KTBException.register
class EOFErrorHandler(ErrorSuggestHandler, priority=1.0):
    r"""
    EOFError异常处理器
    ```
>>> import sys
>>> from io import StringIO
>>> sys.stdin = StringIO("")
>>> input()

... Traceback (most recent call last):
...   File "<input>", line 1, in <module>
(-) EOFError
    改为:
(1) [EOFError] 输入结束
    ```
    """
    def __init__(self, exc_type, exc_value, exc_traceback, **kwargs):
        super().__init__(exc_type, exc_value, exc_traceback, **kwargs)
        self._can_handle = issubclass(exc_type, EOFError)
        if self._can_handle:
            self.err_msg_key = {
                "EOF when reading a line": "native.EOFError.when_reading_line",
            }.get(safe_string(exc_value, '<exception>'), exc_value or "native.EOFError.msg")

    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.EOFError.when_reading_line": "EOF when reading a line",
                "native.EOFError.msg": "get stop signal, data reading ended",
            },
            "zh_hans": {
                "native.EOFError.when_reading_line": "读取一行时接收到了停止信号",
                "native.EOFError.msg": "接收到了停止信号，数据读取结束",
            }
        }

    def handle(self, ktb_exc) -> Generator[str, None, None]:
        self.err_msg = rc.translate(self.err_msg_key)
        yield rc.exc_line("EOFError", self.err_msg)
