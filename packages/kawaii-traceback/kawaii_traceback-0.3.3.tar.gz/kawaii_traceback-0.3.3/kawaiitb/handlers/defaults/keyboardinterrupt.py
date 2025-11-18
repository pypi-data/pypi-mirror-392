from typing import Generator

from kawaiitb.kraceback import KTBException
from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc


@KTBException.register
class KeyboardInterruptHandler(ErrorSuggestHandler, priority=1.0):
    """
    KeyboardInterrupt异常处理器

    当用户按下Ctrl+C时，会抛出KeyboardInterrupt异常
    ```
>>> # 用户按下Ctrl+C

...
... Traceback (most recent call last):
...   File "<input>", line 1, in <module>
(-) KeyboardInterrupt
    改为:
(1) [KeyboardInterrupt] 手动终止了程序
    ```
    """

    def __init__(self, exc_type, exc_value, exc_traceback, **kwargs):
        super().__init__(exc_type, exc_value, exc_traceback, **kwargs)
        self._can_handle = issubclass(exc_type, KeyboardInterrupt)

    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.KeyboardInterrupt.msg": "Program interrupted by user",
            },
            "zh_hans": {
                "native.KeyboardInterrupt.msg": "手动终止了程序",
                "native.KeyboardInterrupt.msg_extra": "手动终止了程序：{extra}",
            }
        }

    def handle(self, ktb_exc) -> Generator[str, None, None]:
        if not str(ktb_exc).strip():
            yield rc.exc_line("KeyboardInterrupt", rc.translate("native.KeyboardInterrupt.msg"))
        else:
            yield rc.exc_line("KeyboardInterrupt", rc.translate("native.KeyboardInterrupt.msg_extra", extra=str(ktb_exc)))
