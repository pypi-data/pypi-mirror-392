from typing import Generator

import astroid
from astroid import nodes

from kawaiitb.kraceback import KTBException
from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc
from kawaiitb.utils import safe_string


@KTBException.register
class ZeroDivisionErrorHandler(ErrorSuggestHandler, priority=1.0):
    """
    ZeroDivisionError异常处理器
    ```
>>> 1 / (1 - 1)

... Traceback (most recent call last):
...   File "<input>", line 1, in <module>
(-) ZeroDivisionError: division by zero

    改为:

(1) [ZeroDivisionError] 除以零 - '(1 - 1)'的值为0
    ```
    """
    def __init__(self, exc_type, exc_value, exc_traceback, **kwargs):
        super().__init__(exc_type, exc_value, exc_traceback, **kwargs)
        self._can_handle = issubclass(exc_type, ZeroDivisionError)
        self.exc_value = exc_value
        self.stack = exc_traceback

    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.ZeroDivisionError.msg_plain": "division by zero",
                "native.ZeroDivisionError.msg": "division by zero - '{divisor}' evaluates to 0",
                "native.ZeroDivisionError.easter_eggs":["KawaiiTraceback has been installed successfully!",
                                                         "Congratulations! You have successfully installed KawaiiTraceback!",
                                                         "You can't divide by zero! QwQ",
                                                         "Tips: TracebackException is the only Exception that cannot be raised.",
                                                         "1/0 = ∞ (in the Riemann sphere)"]
            },
            "zh_hans": {
                "native.ZeroDivisionError.msg_plain": "除以零",
                "native.ZeroDivisionError.msg": "除以零 - '{divisor}'的值为0",
                "native.ZeroDivisionError.easter_eggs": ["KawaiiTraceback安装成功!",
                                                         "恭喜你发现了Python的隐藏特性：无限能量生成器！",
                                                         "不可以除以零啦喵~(´•ω•̥`)",
                                                         "冷知识：TracebackException是唯一一个不能raise的Exception",
                                                         "1/0 = ∞ (在黎曼球面上成立)"]
            }
        }

    def handle(self, ktb_exc) -> Generator[str, None, None]:
        # 一般ZeroDivisionError的错误信息都是division by zero, 或者没有。这两种情况都可以直接用翻译
        for node in self.parse_ast_from_exc(ktb_exc.stack[0]):
            # case: 1 / 0 -> BinOp(
            #     left=Num(n=1),
            #     op=Div(),
            #     right=Num(n=0))
            if (
                isinstance(node, nodes.BinOp) and node.op == '/' and  # 是转浮点除
                isinstance(node.left, nodes.Const) and node.left.value == 1 and  # 被除数是1  # noqa
                isinstance(node.right, nodes.Const) and node.right.value == 0  # 除数是0
            ):
                # 输入1/0触发彩蛋
                import random
                egg = random.choice(rc.translate("native.ZeroDivisionError.easter_eggs"))
                yield rc.exc_line("KawaiiTB", egg)
                break
            elif(
                isinstance(node, nodes.BinOp) and node.op in ('/', '//')  # 是除法
            ):
                # 这就够了。不需要太麻烦的匹配，二元操作的错误帧定位本身就很精准了
                if self.exc_value is None or \
                        safe_string(self.exc_value, "") == "division by zero" or \
                        safe_string(self.exc_value, "") == "float division by zero":
                    hint = rc.translate("native.ZeroDivisionError.msg", divisor=node.right.as_string())
                else:
                    hint = self.exc_value
                yield rc.exc_line("ZeroDivisionError", hint)
                break
        else:
            yield rc.exc_line("ZeroDivisionError", rc.translate("native.ZeroDivisionError.msg_plain"))
