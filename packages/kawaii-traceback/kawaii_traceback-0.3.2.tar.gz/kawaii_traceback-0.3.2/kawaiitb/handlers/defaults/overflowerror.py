from typing import Generator

from kawaiitb.kraceback import KTBException
from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc
from kawaiitb.utils import safe_string


@KTBException.register
class OverflowErrorHandler(ErrorSuggestHandler, priority=1.0):
    """
    OverflowError异常处理器
    ```
>>> import math
>>> math.exp(1000)

... Traceback (most recent call last):
...   File "<input>", line 1, in <module>
(-) OverflowError: math range error

    改为:

(1) [OverflowError] 溢出错误: 数学范围错误
    ```
    """

    def __init__(self, exc_type, exc_value, exc_traceback, **kwargs):
        super().__init__(exc_type, exc_value, exc_traceback, **kwargs)
        self._can_handle = issubclass(exc_type, OverflowError)
        if self._can_handle:
            self.orig_msg = ""
            self.err_msg_key = {
                "math range error": "native.OverflowError.msg.math_range_error",  # 数学范围错误
            }.get(safe_string(exc_value, '<exception>'))
            if not self.err_msg_key:
                self.err_msg_key = "native.OverflowError.msg.novalue"
                self.orig_msg = safe_string(exc_value, '<exception>')


    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.OverflowError.msg.novalue": "A value is too large for the given type",
                "native.OverflowError.msg.math_range_error": "math range error",
            },
            "zh_hans": {
                "native.OverflowError.msg.novalue": "数值超出了其类型所能表示的范围",
                "native.OverflowError.msg.math_range_error": "数学范围错误",
            }
        }

    def handle(self, ktb_exc) -> Generator[str, None, None]:
        if self.orig_msg:
            yield rc.exc_line("OverflowError", self.orig_msg)
        else:
            yield rc.exc_line("OverflowError", rc.translate(self.err_msg_key))
