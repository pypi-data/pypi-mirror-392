import os

import pytest

import kawaiitb.kraceback as kraceback
from test.utils.utils import raise_error, KTBTestBase

class TestFramesummary(KTBTestBase, console_output=False):
    """测试Framesummary类"""

    def test_framesummary_at_cwd(self):
        """测试Framesummary类-位于当前工作目录"""
        with pytest.raises(ValueError) as exc_info:
            raise_error(ValueError, "test_framesummary_at_cwd")

        ktb = kraceback.KTBException.from_exception(exc_info.value)
        frame = ktb.stack[1]

        # print()
        # print(f"{frame.filename=}")
        # print(f"{frame.namespace=}")
        # print(f"{frame.abs_filename=}")
        # print(f"{frame.refined_filename=}")

        assert frame.filename.endswith(f"{os.sep}test{os.sep}utils{os.sep}utils.py")
        assert frame.namespace == "."
        assert frame.abs_filename.endswith(f"{os.sep}test{os.sep}utils{os.sep}utils.py")
        assert frame.refined_filename == f"utils{os.sep}utils.py" or frame.refined_filename == f"test{os.sep}utils{os.sep}utils.py"

    def test_framesummary_at_lib(self):
        """测试Framesummary类-位于标准库目录"""
        with pytest.raises(ValueError) as exc_info:
            import base64
            base64.b64decode("SGVsbG8")  # 少个等号

        ktb = kraceback.KTBException.from_exception(exc_info.value)
        frame = ktb.stack[1]

        # print()
        # print(f"{frame.filename=}")
        # print(f"{frame.namespace=}")
        # print(f"{frame.abs_filename=}")
        # print(f"{frame.refined_filename=}")

        assert frame.filename.endswith(f"{os.sep}base64.py")
        assert frame.namespace == "base64"
        assert frame.abs_filename.endswith(f"{os.sep}base64.py")
        assert frame.refined_filename == f"base64.py"

    def test_framesummary_at_sp(self):
        """测试Framesummary类-位于第三方库目录"""
        with pytest.raises(Exception) as exc_info:
            import yaml
            yaml.load("a: :", Loader=yaml.FullLoader)

        ktb = kraceback.KTBException.from_exception(exc_info.value)
        frame = next(frame
                     for frame in ktb.stack
                     if 'site-packages' in frame.filename)
        if frame is None:
            pytest.skip("No third-party library frames found in stack")

        # print()
        # print(f"{frame.filename=}")
        # print(f"{frame.namespace=}")
        # print(f"{frame.abs_filename=}")
        # print(f"{frame.refined_filename=}")

        assert frame.filename.endswith(f"{os.sep}yaml{os.sep}__init__.py")
        assert frame.namespace == "yaml"
        assert frame.abs_filename.endswith(f"{os.sep}yaml{os.sep}__init__.py")
        assert frame.refined_filename == f"yaml{os.sep}__init__.py"

    def test_framesummary_at_sp_c(self):
        """测试Framesummary类-位于第三方库的C扩展模块"""
        with pytest.raises(Exception) as exc_info:
            import numpy as np
            np.random.uniform(low=[1, 2], high=[4, 5, 6], size=(3))

        ktb = kraceback.KTBException.from_exception(exc_info.value)
        frame = ktb.stack[1]

        # print()
        # print(f"{frame.filename=}")
        # print(f"{frame.namespace=}")
        # print(f"{frame.abs_filename=}")
        # print(f"{frame.refined_filename=}")

        assert frame.filename in f"numpy/random/mtrand.pyx", f"numpy\\random\\mtrand.pyx"  # 取决于编译路径
        assert frame.namespace == "numpy"
        assert f"{os.sep}numpy{os.sep}random{os.sep}mtrand" in frame.abs_filename
        assert frame.abs_filename.endswith(".pyd") or frame.abs_filename.endswith(".so")
        assert frame.abs_filename.endswith(frame.refined_filename)
