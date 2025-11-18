from typing import Generator

import astroid
from astroid import nodes

from kawaiitb.kraceback import KTBException
from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc


@KTBException.register
class StopIterationHandler(ErrorSuggestHandler, priority=1.0):  # 原生
    """
    StopIteration异常处理器
    ```
>>> def f():
>>>     for i in range(10):
>>>         yield i
>>>     return "Boom!"
>>>
>>> g = f()
>>> while True:
>>>     next(g)

... Traceback (most recent call last):
...   File "main.py", line 139, in <module>
...     next(g)
(-) StopIteration: Boom!

    改为:

(1) [StopIteration] 生成器'g'停止迭代: Boom!
    ```
    """

    def __init__(self, exc_type, exc_value, exc_traceback, **kwargs):
        super().__init__(exc_type, exc_value, exc_traceback, **kwargs)
        self._can_handle = issubclass(exc_type, StopIteration)
        if not self._can_handle:
            return

        # Python 3.7 之后，对于使用return 关键字的生成器，抛出的StopIteration异常会包含 return 的值。
        self.return_value = exc_value.value if hasattr(exc_value, 'value') else None


    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.StopIteration.hint": "Generator '{generator}' stopped iterating.",
                "native.StopIteration.hint_with_return": "Generator '{generator}' stopped: {ret}",
            },
            "zh_hans": {
                "native.StopIteration.hint": "生成器'{generator}'没有更多值了。",
                "native.StopIteration.hint_with_return": "生成器'{generator}'没有更多值了: {ret}",
            }
        }

    def handle(self, ktb_exc: KTBException) -> Generator[str, None, None]:
        # 从栈帧中获取生成器在代码里的名称
        self.generator = "<...>"
        if len(ktb_exc.stack) > 0:
            exc_frame = ktb_exc.stack[0]
            for node in self.parse_ast_from_exc(exc_frame):
                # case: next(g) -> Call(
                #     func=Name(name=next),
                #     args=[...])
                if (
                        isinstance(node, nodes.Call) and  # 是函数调用
                        isinstance(node.func, nodes.Name) and  # 是显式函数名
                        node.func.name == 'next'  # 是next调用
                ):
                    self.generator = node.args[0].as_string()
                    break

                # case: g.__next__() -> Call(
                #     func=Attr(
                #         expr=<?>,
                #         attrname=__next__),
                #     args=[...])
                if (
                    isinstance(node, nodes.Call) and  # 是函数调用
                    isinstance(node.func, nodes.Attribute) and  # 是属性访问
                    node.func.attrname == '__next__'  # 是__next__方法调用
                ):
                    # 获取生成器表达式字符串
                    self.generator = node.func.expr.as_string()
                    break

        if self.return_value is not None:
            hint = rc.translate("native.StopIteration.hint_with_return", generator=self.generator, ret=self.return_value)
        else:
            hint = rc.translate("native.StopIteration.hint", generator=self.generator)
        yield rc.exc_line("StopIteration", hint)
