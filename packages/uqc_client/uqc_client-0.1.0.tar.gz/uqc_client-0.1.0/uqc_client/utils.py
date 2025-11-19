import asyncio
import logging
import threading
from typing import Set, Optional

logger = logging.getLogger(__name__)


def is_jupyter_environment():
    """
    判断是否在 Jupyter 环境中运行
    Returns
    -------
    bool
    """
    try:
        # 检查是否有 IPython 内核
        from IPython import get_ipython
        return get_ipython() is not None
    except ImportError:
        return False


def is_event_loop_running() -> bool:
    """
    检测事件循环是否正在运行
    Returns
    -------
    bool
    """
    try:
        loop = asyncio.get_event_loop()
        return loop.is_running()
    except (RuntimeError, AttributeError):
        return False


def is_main_thread() -> bool:
    """
    检测当前是否在主线程中运行
    Returns
    -------
    bool
    """
    return threading.current_thread() == threading.main_thread()


class AsyncRunManager:
    """
    异步运行管理器，用于在不同环境中运行异步任务
    """

    def __init__(self):

        self.is_jupyter_environment = is_jupyter_environment()
        self.loop = None
        self.thread = None

        if self.is_jupyter_environment:
            self._setup_jupyter_environment()
        else:
            self._setup_standard_environment()

    def __del__(self):
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.loop.stop)
            if self.thread:
                self.thread.join()
            self.loop.close()

    def _setup_jupyter_environment(self):
        """设置 Jupyter 环境"""
        # 获取当前事件循环
        import nest_asyncio

        nest_asyncio.apply()
        self.loop = asyncio.get_event_loop()

    def _setup_standard_environment(self):
        """设置标准 Python 环境"""
        # 创建新的事件循环并在后台线程中运行
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()

    def _run_event_loop(self):
        """在后台线程中运行事件循环"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coro):
        """
        运行协程任务
        """
        try:
            if not asyncio.iscoroutine(coro):
                raise ValueError("The provided argument is not a coroutine.")

            if self.is_jupyter_environment:
                return self.loop.run_until_complete(coro)
            else:
                future = asyncio.run_coroutine_threadsafe(coro, self.loop)
                return future.result()
        except Exception as e:
            logger.error(f"Error running coroutine: {e}")
            raise


async def async_export(data: Optional[Set[str]], file_path: str = None):
    """
    导出数据到指定文件
    """
    if not data:
        return
    try:
        from aiofiles import open as aioopen

        async with aioopen(file_path, "w+") as f:
            for item in data:
                await f.write(f"{item}\n")
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
