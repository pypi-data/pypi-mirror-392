from typing import Generator

import astroid
from astroid import nodes

from kawaiitb.kraceback import KTBException
from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc


@KTBException.register
class StopAsyncIterationHandler(ErrorSuggestHandler, priority=1.0):  # 原生
    """
    StopAsyncIteration异常处理器
    ```
>>> async def f():
>>>     for i in range(10):
>>>         yield i
>>>     return "Boom!"
>>>
>>> async for i in f():
>>>     pass

... Traceback (most recent call last):
...   File "main.py", line 139, in <module>
...     async for i in f():
(-) StopAsyncIteration: Boom!

    改为:

(1) [StopAsyncIteration] 异步生成器'f'停止迭代: Boom!
    ```
    """

    def __init__(self, exc_type, exc_value, exc_traceback, **kwargs):
        super().__init__(exc_type, exc_value, exc_traceback, **kwargs)
        self._can_handle = issubclass(exc_type, StopAsyncIteration)
        if not self._can_handle:
            return

        self.return_value = exc_value.value if hasattr(exc_value, 'value') else None

    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.StopAsyncIteration.hint": "Async generator '{generator}' stopped iterating.",
                "native.StopAsyncIteration.hint_with_return": "Async generator '{generator}' stopped: {ret}",
            },
            "zh_hans": {
                "native.StopAsyncIteration.hint": "异步生成器'{generator}'没有更多值了。",
                "native.StopAsyncIteration.hint_with_return": "异步生成器'{generator}'没有更多值了: {ret}",
            }
        }

    def handle(self, ktb_exc) -> Generator[str, None, None]:
        # 从栈帧中获取异步生成器在代码里的名称
        self.generator = "<...>"
        if len(ktb_exc.stack) > 0:
            exc_frame = ktb_exc.stack[0]
            for node in self.parse_ast_from_exc(exc_frame):
                # case: anext(g) -> Call(
                #     func=Name(name=anext),
                #     args=[...])
                if (
                    isinstance(node, nodes.Call) and  # 是函数调用
                    isinstance(node.func, nodes.Name) and  # 是显式函数名
                    node.func.name == 'anext'  # 是anext调用
                ):
                    self.generator = node.args[0].as_string()
                    break

                # case: g.__anext__() -> Call(
                #     func=Attr(
                #         expr=<?>,
                #         attrname=__anext__),
                #     args=[...])
                if (
                    isinstance(node, nodes.Call) and  # 是函数调用
                    isinstance(node.func, nodes.Attribute) and  # 是属性访问
                    node.func.attrname == '__anext__'  # 是__anext__方法调用
                ):
                    # 获取异步生成器表达式字符串
                    self.generator = node.func.expr.as_string()
                    break

                # case: async for i in g: -> AsyncFor(
                #     target=<?>,
                #     iter=<?>,
                #     body=[...])
                if isinstance(node, nodes.AsyncFor):
                    self.generator = node.iter.as_string()
                    break

        if self.return_value is not None:
            hint = rc.translate("native.StopAsyncIteration.hint_with_return",
                             generator=self.generator,
                             ret=self.return_value)
        else:
            hint = rc.translate("native.StopAsyncIteration.hint",
                             generator=self.generator)
        if self.generator:
            yield rc.exc_line("StopAsyncIteration", hint)
        else:
            yield rc.exc_line("StopAsyncIteration", hint)
