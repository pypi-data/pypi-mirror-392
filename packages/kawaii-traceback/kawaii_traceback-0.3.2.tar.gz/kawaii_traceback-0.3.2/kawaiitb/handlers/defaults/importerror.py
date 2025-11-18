from typing import Generator

from kawaiitb.kraceback import KTBException
from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc

@KTBException.register
class ImportErrorHandler(ErrorSuggestHandler, priority=1.0):
    """
    ImportError异常处理器

    当导入一个不存在的模块时，会抛出ImportError异常
    ```
>>> # 导入一个不存在的模块
>>> import non_existent_module  # noqa

... Traceback (most recent call last):
...   File "<input>", line 1, in <module>
... ModuleNotFoundError: No module named 'non_existent_module'
    改为:
(1) [ImportError] 无法导入模块 'non_existent_module'
    ```
    """

    def __init__(self, exc_type, exc_value, exc_traceback, **kwargs):
        super().__init__(exc_type, exc_value, exc_traceback, **kwargs)
        self._can_handle = issubclass(exc_type, ImportError)

    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.ImportError.msg": "Cannot import module '{module_name}'",
            },
        }
    
    def handle(self, ktb_exc: KTBException) -> Generator[str, None, None]:
        module_name = self.exc_value.name
        yield self.translate("native.ImportError.msg", module_name=module_name)
