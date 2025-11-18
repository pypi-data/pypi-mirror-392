import io

import pytest

import kawaiitb
from kawaiitb import kraceback
from test.utils.utils import KTBTestBase

class TestExceptionFromLibs(KTBTestBase, console_output=False, packing_handler=kawaiitb.ErrorSuggestHandler):
    def test_from_std_lib(self):
        """测试从stdlib引发的错误，这里尝试错误地解码SGVsbG8为base64"""
        with pytest.raises(Exception) as excinfo:
            import base64
            base64.b64decode("SGVsbG8")

        stream = io.StringIO()
        kraceback.print_exception(excinfo.value, file=stream)
        fulltb = stream.getvalue()
        self.try_print_exc(excinfo.value)
        assert "[base64" in fulltb

    def test_from_third_party_lib(self):
        """测试从third party lib引发的错误，此处使用numpy计算维度不符的数组"""
        kawaiitb.set_config({
            "config.file.include_abspath": False,
        }, "neko_zh")
        with pytest.raises(Exception) as excinfo:
            import numpy as np
            np.random.uniform(low=[1, 2], high=[4, 5, 6], size=(3))

        stream = io.StringIO()
        kraceback.print_exception(excinfo.value, file=stream)
        fulltb = stream.getvalue()
        self.try_print_exc(excinfo.value)
        assert "[numpy" in fulltb
        assert ".pyx" in fulltb.lower()
        assert "/numpy" not in fulltb.lower() and "\\numpy" not in fulltb.lower()

    def test_from_third_party_lib_infull_path(self):
        """测试从third party lib引发的错误。但是错误信息中包含了完整的路径"""
        kawaiitb.set_config({
            "config.file.include_abspath": True,
        }, "neko_zh")
        with pytest.raises(Exception) as excinfo:
            import numpy as np
            np.random.uniform(low=[1, 2], high=[4, 5, 6], size=(3))

        stream = io.StringIO()
        kraceback.print_exception(excinfo.value, file=stream)
        fulltb = stream.getvalue()
        self.try_print_exc(excinfo.value)
        assert "[numpy" in fulltb
        assert ".pyd" in fulltb.lower() or ".so" in fulltb.lower()
        assert "/numpy" in fulltb.lower() or "\\numpy" in fulltb.lower()

