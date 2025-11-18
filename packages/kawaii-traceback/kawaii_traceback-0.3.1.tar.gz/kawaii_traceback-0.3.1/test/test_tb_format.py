import asyncio

import pytest

import kawaiitb
from kawaiitb.kraceback import ENV
from test.utils.utils import KTBTestBase, setup_test


class TestExceptionFormatting(KTBTestBase, console_output=False):
    def test_recursive_exception(self):
        """测试递归异常深度溢出"""
        setup_test()
        try:
            f = lambda x: f(x + 1)
            f(1)
        except Exception as e:
            tb = "".join(kawaiitb.traceback.format_exception(e))
            self.try_print_exc(e)
            assert "* 这一帧重复了" in tb

    @staticmethod
    async def task():
        r"""
Traceback (most recent call last):
  File "C:\Users\BPuffer\Desktop\kawaii-traceback\test\test_tb_format.py", line 127, in test_***
    asyncio.run(self.task())
  File "C:\Program Files\Python312\Lib\asyncio\runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "C:\Program Files\Python312\Lib\asyncio\runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\Python312\Lib\asyncio\base_events.py", line 686, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "C:\Users\BPuffer\Desktop\kawaii-traceback\test\test_tb_format.py", line 125, in task
    raise Exception("test")
Exception: test
        """
        await asyncio.sleep(0)
        raise Exception("test")

    def test_foldup_default(self):
        """测试tb压缩默认行为"""
        import asyncio
        kawaiitb.set_config({
            "config.stack.foldup_topframe": False,
            "config.stack.foldup_threshold": 1,
            "config.stack.foldup_tailframe": False,
        }, "neko_zh")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(self.task())

        tb = "".join(kawaiitb.traceback.format_exception(excinfo.value))
        self.try_print_exc(excinfo.value)

        assert r"asyncio.run(self.task())" in tb
        assert r"runner.run(main)" in tb
        assert "| 压缩了 1 个来自模块 asyncio 的帧" in tb
        assert r"future.result()" in tb
        assert r'raise Exception("test")' in tb

    @pytest.mark.skip(reason="暂时没有例子……")
    def test_foldup_threshold(self):
        """测试tb压缩，压缩阈值为2"""
        ...

    def test_foldup_folduptop(self):
        """测试tb压缩，压缩同一模块的头部"""
        import asyncio
        kawaiitb.set_config({
            "config.stack.foldup_topframe": True,
            "config.stack.foldup_threshold": 1,
            "config.stack.foldup_tailframe": False,
        }, "neko_zh")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(self.task())

        tb = "".join(kawaiitb.traceback.format_exception(excinfo.value))
        self.try_print_exc(excinfo.value)

        assert r"asyncio.run(self.task())" in tb
        assert r"runner.run(main)" not in tb
        assert "| 压缩了 2 个来自模块 asyncio 的帧" in tb
        assert r"future.result()" in tb
        assert r'raise Exception("test")' in tb

    def test_foldup_folduptail(self):
        """测试tb压缩，压缩同一模块的尾部"""
        import asyncio
        kawaiitb.set_config({
            "config.stack.foldup_topframe": False,
            "config.stack.foldup_threshold": 1,
            "config.stack.foldup_tailframe": True,
        }, "neko_zh")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(self.task())

        tb = "".join(kawaiitb.traceback.format_exception(excinfo.value))
        self.try_print_exc(excinfo.value)

        assert r"asyncio.run(self.task())" in tb
        assert r"runner.run(main)" in tb
        assert "| 压缩了 2 个来自模块 asyncio 的帧" in tb
        assert r"future.result()" not in tb
        assert r'raise Exception("test")' in tb

    def test_foldup_both(self):
        """测试tb压缩，压缩同一模块的首尾"""
        import asyncio
        kawaiitb.set_config({
            "config.stack.foldup_topframe": True,
            "config.stack.foldup_threshold": 1,
            "config.stack.foldup_tailframe": True,
        }, "neko_zh")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(self.task())

        tb = "".join(kawaiitb.traceback.format_exception(excinfo.value))
        self.try_print_exc(excinfo.value)

        assert r"asyncio.run(self.task())" in tb
        assert r"runner.run(main)" not in tb
        assert "| 压缩了 3 个来自模块 asyncio 的帧" in tb
        assert r"future.result()" not in tb
        assert r'raise Exception("test")' in tb

    def test_donot_foldup(self):
        """测试不进行tb压缩"""
        import asyncio
        kawaiitb.set_config({
            "config.stack.foldup": False,
            "config.file.include_abspath": True,
        }, "neko_zh")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(self.task())

        tb = "".join(kawaiitb.traceback.format_exception(excinfo.value))
        self.try_print_exc(excinfo.value)

        assert r"asyncio.run(self.task())" in tb
        assert "压缩了" not in tb
        assert r"runner.run(main)" in tb
        assert r"self._loop.run_until_complete(task)" in tb
        assert r"future.result()" in tb
        assert r'raise Exception("test")' in tb
