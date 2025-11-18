from kawaiitb.handlers.defaults.stopiteration import StopIterationHandler
from kawaiitb.handlers.defaults.stopasynciteration import StopAsyncIterationHandler
from kawaiitb.handlers.defaults.overflowerror import OverflowErrorHandler
from kawaiitb.handlers.defaults.zerodivisionerror import ZeroDivisionErrorHandler
from kawaiitb.handlers.defaults.assertionerror import AssertionErrorHandler
from kawaiitb.handlers.defaults.keyboardinterrupt import KeyboardInterruptHandler
from kawaiitb.handlers.defaults.eoferror import EOFErrorHandler
from kawaiitb.handlers.defaults.systemexit import SystemExitHandler
from kawaiitb.handlers.defaults.attributeerror import AttributeErrorHandler
from kawaiitb.handlers.defaults.importerror import ImportErrorHandler



__all__ = [
    "StopIterationHandler",
    "StopAsyncIterationHandler",
    "OverflowErrorHandler",
    "ZeroDivisionErrorHandler",
    "AssertionErrorHandler",
    "KeyboardInterruptHandler",
    "EOFErrorHandler",
    "SystemExitHandler",
    "AttributeErrorHandler",
    "ImportErrorHandler"
]

TODOS = {
    "BaseException": {
        "BaseException": "不设计。这个异常过于抽象，基本没人会单独抛",
        "SystemExit": "不设计。这个异常不应该是被捕获的。",
        "KeyboardInterrupt": "KeyboardInterruptHandler(ErrorSuggestHandler, priority=1.0)",  # Complete
        "GeneratorExit": "不要设计，因为这个异常不会被显示",
        "Exception": {
            "Exception": "不设计。这个异常过于抽象，基本没人会单独抛",
            "StopIteration": "StopIterationHandler(ErrorSuggestHandler, priority=1.0)",  # Complete
            "StopAsyncIteration": "StopAsyncIterationHandler(ErrorSuggestHandler, priority=1.0)",  # Complete
            "ArithmeticError": {
                "ArithmeticError": "不设计。这个异常过于抽象，基本没人会单独抛",
                "FloatingPointError": "不设计。这个异常应当不再出现。",
                "OverflowError": "OverflowErrorHandler(ErrorSuggestHandler, priority=1.0)",  # Complete
                "ZeroDivisionError": "ZeroDivisionErrorHandler(ErrorSuggestHandler, priority=1.0)",  # Complete
            },
            "AssertionError": "AssertionErrorHandler(ErrorSuggestHandler, priority=1.0)",  # Complete
            "AttributeError": "AttributeErrorHandler(ErrorSuggestHandler, priority=1.0)",  # Complete
            "BufferError": "过于过于罕见了，能碰见的基本都是在玩底层的人，没必要给他们讲解，不设计",
            "EOFError": "EOFErrorHandler(ErrorSuggestHandler, priority=1.0)",  # Complete
            "ImportError": {
                "ImportError": "ImportErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "ModuleNotFoundError": "ModuleNotFoundErrorHandler(ErrorSuggestHandler, priority=1.05)",  # TODO
            },
            "LookupError": {
                "LookupError": "不设计。这个异常过于抽象，基本没人会单独抛",
                "IndexError": "IndexErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "KeyError": "KeyErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
            },
            "MemoryError": "MemoryErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
            "NameError": {
                "NameError": "NameErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "UnboundLocalError": "UnboundLocalErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
            },
            "OSError": {
                "OSError": "OSErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                # 这个类别只设计几个常见的，太少见的就不设计了
                "BlockingIOError": "",
                "ChildProcessError": "",
                "ConnectionError": {
                    "ConnectionError": "",
                    "BrokenPipeError": "",
                    "ConnectionAbortedError": "",
                    "ConnectionRefusedError": "",
                    "ConnectionResetError": "",
                },
                "FileExistsError": "FileExistsErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "FileNotFoundError": "FileNotFoundErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "InterruptedError": "",
                "IsADirectoryError": "IsADirectoryErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "NotADirectoryError": "NotADirectoryErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "PermissionError": "PermissionErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "ProcessLookupError": "",
                "TimeoutError": "",
            },
            "ReferenceError": "实在过于罕见，疑似cpy完备化接口产物，不设计",
            "RuntimeError": {
                "RuntimeError": "RuntimeErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "NotImplementedError": "NotImplementedErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "RecursionError": "RecursionErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
            },
            "SyntaxError": {
                "SyntaxError": "SyntaxErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "IndentationError": {
                    "IndentationError": "IndentationErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                    "TabError": "TabErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                },
            },
            "SystemError": "SystemErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
            "TypeError": "TypeErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
            "ValueError": {
                "ValueError": "ValueErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                "UnicodeError": {
                    "UnicodeError": "UnicodeErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                    "UnicodeDecodeError": "UnicodeDecodeErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                    "UnicodeEncodeError": "UnicodeEncodeErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                    "UnicodeTranslateError": "UnicodeTranslateErrorHandler(ErrorSuggestHandler, priority=1.0)",  # TODO
                },
            }
        }
    }
}