from typing import Generator, Any

from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc


class SystemExitHandler(ErrorSuggestHandler, priority=1.0):
    """
    SystemExit异常处理器
>>> exit(114514)

... Traceback (most recent call last):
...   File "<input>", line 1, in <module>
(-) SystemExit: 114514
    改为:
(1) [SystemExit] 程序退出: 114514
    """

    def __init__(self, exc_type, exc_value, exc_traceback, **kwargs):
        super().__init__(exc_type, exc_value, exc_traceback, **kwargs)
        self._can_handle = issubclass(exc_type, SystemExit)
        self.value = None
        if self._can_handle:
            self.value = exc_value

    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    def translation_keys(cls) -> dict[str, dict[str, Any]]:
        return {
            "default": {
                "native.systemexit_handler.novalue": "Program exit.",
                "native.systemexit_handler.exit_code": "{value}",
            },
            "zh_hans": {
                "native.systemexit_handler.novalue": "程序退出",
                "native.systemexit_handler.exit_code": "程序退出: {value}",
            }
        }

    def handle(self, ktb_exc) -> Generator[str, None, None]:
        yield from super().handle(ktb_exc)
        if self.value:
            yield rc.translate("native.systemexit_handler.exit_code", value=self.value)
        else:
            yield rc.translate("native.systemexit_handler.novalue")