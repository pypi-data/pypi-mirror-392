from typing import Generator

from astroid import nodes

from kawaiitb.kraceback import KTBException
from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc
from kawaiitb.utils import safe_string


@KTBException.register
class AssertionErrorHandler(ErrorSuggestHandler, priority=1.0):
    """
    AssertionError异常处理器
    ```
>>> a, b = 1, 2
>>> assert a == b

... Traceback (most recent call last):
...   File "<input>", line 1, in <module>
(-) AssertionError
    改为:
(1) [AssertionError] 断言 a == b, 但是 a=1, b=2.
    ```
    """
    def __init__(self, exc_type, exc_value, exc_traceback, **kwargs):
        super().__init__(exc_type, exc_value, exc_traceback, **kwargs)
        self._can_handle = issubclass(exc_type, AssertionError)
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback

    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.AssertionError.msg": "Assertion {assertion} failed.",
                "native.AssertionError.msg_with_values": "Assertion {assertion}, but {values}."
            },
            "zh_hans": {
                "native.AssertionError.msg": "断言 {assertion} 失败。",
                "native.AssertionError.msg_with_values": "断言 {assertion}, 但是 {values}."
            }
        }

    def handle(self, ktb_exc: KTBException) -> Generator[str, None, None]:
        # 如果有信息，直接返回信息
        if (self.exc_value is not None and safe_string(self.exc_value, "") != ""
            or len(ktb_exc.stack) == 0):
            yield rc.exc_line("AssertionError", safe_string(self.exc_value, "<exception>"))
            return

        # 从栈帧中获取断言的表达式字符串
        assert_expr = None
        assert_exprs: set[str] = set()
        exc_frame = ktb_exc.stack[0]
        for node in self.parse_ast_from_exc(exc_frame, parse_line=True):
            if not isinstance(node, nodes.Assert):
                continue
            expr = node.test
            assert_expr = expr.as_string()
            if not assert_expr:
                continue
            # 收集断言表达式中的变量名
            if isinstance(expr, nodes.Compare):
                # 比较表达式: a == b, a > b > c 等
                assert_exprs.add(expr.left.as_string())
                for _, right in expr.ops:
                    assert_exprs.add(right.as_string())
                    # TODO: 支持递归的表达式
                    # 问题: 如何判断递归下的表达式是用户所需要看到的
                    # 阻力: 断言表达式通常大道至简, 甚至第二层嵌套都很少看到, 实用型存疑
            elif isinstance(expr, nodes.BoolOp):
                # 布尔运算: a and b and c 等
                assert_exprs.add(expr.as_string())
                for value in expr.values:
                    if isinstance(value, nodes.Name):
                        assert_exprs.add(value.as_string())
            elif isinstance(expr, nodes.Name):
                # 简单变量: assert a
                assert_exprs.add(expr.as_string())
            elif isinstance(expr, nodes.Call):
                # 函数调用: assert a()
                # 如果函数以"is""not""has"开头, 则取得所有函数参数, 否则只取整个表达式的值
                if isinstance(expr.func, nodes.Name):
                    func_name = expr.func.as_string().split(".")[-1]
                    if func_name.startswith(("is", "not", "has")):
                        [
                            assert_exprs.add(arg.as_string())
                            for arg in expr.args
                            if isinstance(arg, (nodes.Name, nodes.Expr))
                        ]
                        # for arg in expr.args:
                        #     assert_exprs.add(arg.as_string())
                    else:
                        assert_exprs.add(expr.as_string())
            elif isinstance(expr, (nodes.BinOp, nodes.UnaryOp)):
                # 一二元运算等直接求值, 这些变量的最终值不是布尔, 用户只需要这个值.
                for operand in [expr.left, expr.right]:
                    if isinstance(operand, nodes.Name):
                        assert_exprs.add(operand.as_string())
            break

        if assert_expr is None:
            yield rc.exc_line("AssertionError", rc.translate("native.AssertionError.msg", assertion="<Unknown Expression>"))
            return

        # 获取变量的实际值
        values = []
        frame = self.exc_traceback.tb_frame
        globals_dict = frame.f_globals
        locals_dict = frame.f_locals

        for expr_str in assert_exprs:
            try:
                evaluated = eval(expr_str, globals_dict, locals_dict)
                # 此处使用eval是因为原表达式一定已经求值成功了，才会报AssertionError
                values.append(f"{expr_str}={evaluated!r}")
            except Exception:
                # 理论上不会进入这个分支, 但安全起见.
                yield f"[KawaiiTB Error] strange error when eval {expr_str}"

        values_str = ", ".join(values)
        if len(values_str) > 50:
            values_str = values_str[:50] + "..."

        if values:
            yield rc.exc_line(
                "AssertionError",
                rc.translate("native.AssertionError.msg_with_values",
                             assertion=assert_expr,
                             values=", ".join(values)))
        else:
            yield rc.exc_line(
                "AssertionError",
                rc.translate(
                    "native.AssertionError.msg",
                    assertion=assert_expr
                )
            )
