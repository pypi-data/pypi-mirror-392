import sys
from typing import Generator

from kawaiitb.kraceback import KTBException
from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc
from kawaiitb.utils.fromtraceback import compute_suggestion_error

__all__ = [
    # 所有原生处理中含有新增的处理逻辑的处理器。优先级均为1.1。
    "SyntaxErrorSuggestHandler",
    "ImportErrorSuggestHandler",
    "NameAttributeErrorSuggestHandler",
]

@KTBException.register
class SyntaxErrorSuggestHandler(ErrorSuggestHandler, priority=1.1):
    """
    本处理器模仿原生的语法错误处理器，为语法错误添加额外的锚点指示
    """

    def __init__(self, exc_type, exc_value, exc_traceback, *, limit=None,
                 lookup_lines=True, capture_locals=False, compact=False,
                 max_group_width=15, max_group_depth=10, _seen=None):
        super().__init__(exc_type, exc_value, exc_traceback)
        if exc_type and issubclass(exc_type, SyntaxError):
            exc_value: SyntaxError
            self.filename = exc_value.filename
            lno = exc_value.lineno
            self.lineno = str(lno) if lno is not None else None
            end_lno = exc_value.end_lineno
            self.end_lineno = str(end_lno) if end_lno is not None else None
            self.text = exc_value.text
            self.offset = exc_value.offset
            self.end_offset = exc_value.end_offset
            self.msg = exc_value.msg

    @classmethod
    def translation_keys(cls):
        return {}  # 翻译键均由默认配置提供，不需要额外的翻译键

    def can_handle(self, ktb_exc) -> bool:
        return issubclass(ktb_exc.exc_type, SyntaxError)

    def handle(self, ktb_exc) -> Generator[str, None, None]:
        r"""
        (-) Traceback (most recent call last):
        (-)   File "C:\Users\BPuffer\Desktop\kawaii-traceback\main.py", line 139:8, in <module>
        (-)     exec("what can i say?")
        (1)   File "<string>", line 1
        (2)     what can i say?
        (3)          ^^^
        (4) SyntaxError: invalid syntax (<string>, line 1)
        """
        if self.lineno is not None:
            # part (1)
            yield rc.translate("frame.location.without_name",
                               file=self.filename or "<string>",  # repr转义
                               lineno=self.lineno, )

        text = self.text
        if text is not None:
            rtext = text.rstrip('\n')
            ltext = rtext.lstrip(' \n\f')
            spaces = len(rtext) - len(ltext)
            # part (2)
            yield rc.translate("frame.location.linetext",
                               line=ltext)

            if self.offset is not None:
                offset = self.offset
                end_offset = self.end_offset if self.end_offset not in {None, 0} else offset
                if offset == end_offset or end_offset == -1:
                    end_offset = offset + 1

                colno = offset - 1 - spaces
                end_colno = end_offset - 1 - spaces
                if colno >= 0:
                    # part (3)
                    # caretspace = ((c if c.isspace() else ' ') for c in ltext[:colno])
                    # yield '    {}{}'.format("".join(caretspace), ('^' * (end_colno - colno) + "\n"))
                    anchor_len = end_colno - colno
                    yield rc.anchors('    ' + ' ' * colno, 0, 0, anchor_len, anchor_len, crlf=True)

        msg = self.msg or "<no detail available>"
        # part (4)
        yield from super().handle(ktb_exc)


@KTBException.register
class ImportErrorSuggestHandler(ErrorSuggestHandler, priority=1.1):
    """
    本处理器模仿原生的ImportError的拼写错误检测
    为导入中的拼写错误添加额外的正确拼写提示
    """

    def __init__(self, exc_type, exc_value, exc_traceback, *, limit=None,
                 lookup_lines=True, capture_locals=False, compact=False,
                 max_group_width=15, max_group_depth=10, _seen=None):
        super().__init__(exc_type, exc_value, exc_traceback)

        self._can_handle = issubclass(exc_type, ImportError) and getattr(exc_value, "name_from", None) is not None

        self.suggestion = None
        if self._can_handle:
            self.wrong_name = getattr(exc_value, "name_from")
            self.suggestion = compute_suggestion_error(exc_value, exc_traceback, self.wrong_name)

    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.import_error_suggestion.hint": "Did you mean '{suggestion}'?",
            },
            "zh_hans": {
                "native.import_error_suggestion.hint": "你可能是想导入'{suggestion}'",
            }
        }

    def handle(self, ktb_exc) -> Generator[str, None, None]:
        yield from super().handle(ktb_exc)
        if self.suggestion:
            yield rc.translate("native.import_error_suggestion.hint", suggestion=self.suggestion)


# @KTBException.register  # 正在考虑完全移除，正在尝试使用更通用的处理器 NameError和AttributeError 的Handler替代
class NameAttributeErrorSuggestHandler(ErrorSuggestHandler, priority=1.1):
    """
    本处理器模仿原生的NameError的拼写错误检测
    为NameError的拼写错误添加额外的正确拼写提示
    并为存在于标准库和第三方库中的名字添加额外的提示
    """

    def __init__(self, exc_type, exc_value, exc_traceback, *, limit=None,
                 lookup_lines=True, capture_locals=False, compact=False,
                 max_group_width=15, max_group_depth=10, _seen=None):
        super().__init__(exc_type, exc_value, exc_traceback)

        self._can_handle = (issubclass(exc_type, (NameError, AttributeError)) and
                            getattr(exc_value, "name", None) is not None)

        if self._can_handle:
            self.wrong_name = getattr(exc_value, "name")
            self.suggestion = compute_suggestion_error(exc_value, exc_traceback, self.wrong_name)
            self.is_stdlib = self.wrong_name in sys.stdlib_module_names

            self.is_3rd_party = False
            import importlib.metadata
            try:
                importlib.metadata.distribution(self.wrong_name)
                self.is_3rd_party = True
            except importlib.metadata.PackageNotFoundError:
                pass

            self.is_lib = self.is_stdlib or self.is_3rd_party

    def can_handle(self, ktb_exc) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.nameattr_error_suggestion.typo": "Did you mean '{suggestion}'?",
                "native.nameattr_error_suggestion.forget_import": "You may forget to import '{wrong_name}'",
                "native.nameattr_error_suggestion.or_forget_import": "or you may forget to import '{wrong_name}'",
            },
            "zh_hans": {
                "native.nameattr_error_suggestion.typo": "你是不是想输入'{suggestion}'？",
                "native.nameattr_error_suggestion.forget_import": "你可能忘记导入'{wrong_name}'了",
                "native.nameattr_error_suggestion.or_forget_import": "或者你可能忘记导入'{wrong_name}'了",
            }
        }

    def handle(self, ktb_exc) -> Generator[str, None, None]:
        yield from super().handle(ktb_exc)
        if self.suggestion:
            yield rc.translate("native.nameattr_error_suggestion.typo", suggestion=self.suggestion)

        if issubclass(ktb_exc.exc_type, NameError) and self.is_stdlib:
            if self.suggestion:
                yield rc.translate("native.nameattr_error_suggestion.or_forget_import", wrong_name=self.wrong_name)
            else:
                yield rc.translate("native.nameattr_error_suggestion.forget_import", wrong_name=self.wrong_name)
