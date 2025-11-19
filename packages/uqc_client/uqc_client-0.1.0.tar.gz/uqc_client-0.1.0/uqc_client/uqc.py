import json
import asyncio
import socketio
import logging
import threading
import pytz
from uuid import uuid4
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta, timezone
from .uqc_config import UQCConfig
from .validator import ensure_static_qasm
from .utils import AsyncRunManager, async_export

logger = logging.getLogger(__name__)


uqc_config = UQCConfig()


class UQCError(Exception):
    """UQC 客户端库的基础异常类。"""

    pass


class UQCConnectionError(UQCError):
    """当与服务器的连接建立或通信失败时引发。"""

    pass


class UQCTimeoutError(UQCError):
    """当请求等待响应超时时引发。"""

    pass


class UQCTaskError(UQCError):
    """当服务器返回任务相关错误时引发。"""

    pass


class UQCAuthenticationError(UQCError):
    """当认证失败或Token无效时引发。"""

    pass


class UQC:

    __uqc_handlers = None

    def __init__(self, token: Optional[str] = None):

        self.sio = socketio.AsyncClient()
        self.connected = False

        self._async_mgr = AsyncRunManager()

        if token:
            self._token = token
        else:
            self._token = uqc_config.USER_TOKEN

        self._event = asyncio.Event()
        self._response_data: Optional[Dict] = None
        self._task_id: Optional[str] = None
        self._task_result: Optional[Any] = None
        self._chips: Optional[List] = None
        self._chip_info: Optional[Dict] = None
        self._task_status: Optional[str] = None

        # Register event handlers
        self.sio.on("connect", self._on_connect)
        self.sio.on("disconnect", self._on_disconnect)
        self.sio.on("response", self._handle_response, namespace="/ws")

        # 自动连接
        self._connect()

    def __del__(self):
        # 自动断开连接
        if self.sio.connected:
            logger.warning("UQC client was not properly disconnected. Use 'async with UQC(...)' for reliable cleanup.")
            self._async_mgr.run(self._disconnect())

    def _setup_jupyter_environment(self):
        """设置 Jupyter 环境"""
        # 获取当前事件循环
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

    async def _on_connect(self):
        logger.info("Connected to the UQC server.")

    async def _on_disconnect(self):
        logger.info("Disconnected to the UQC server.")

    async def _handle_response(self, data):
        """统一处理服务器响应"""
        try:
            self._response_data = json.loads(data) if isinstance(data, str) else data
            self._route_message(self._response_data)
        except Exception as e:
            logger.error(f"Error handling response: {e}")
        finally:
            self._event.set()

    def _route_message(self, data: Dict):
        """根据消息类型分发处理"""
        try:
            if not self.__uqc_handlers:
                self.__uqc_handlers = {
                    "MsgAuthAck": self._handle_auth,
                    "MsgGetChipsAck": self._handle_chips,
                    "MsgGetChipConfigAck": self._handle_chip_config,
                    "MsgTaskAck": self._handle_task_ack,
                    "MsgTaskStatusAck": self._handle_task_status,
                    "MsgTaskResultAck": self._handle_task_result,
                }
            if msg_type := data.get("MsgType"):
                handler = self.__uqc_handlers.get(msg_type)
                if handler:
                    handler(data)
                else:
                    logger.error(f"Unknown message type: {msg_type}")
            else:
                logger.error("Missing message type")
        except Exception as e:
            logger.error(f"Handling message exception: {e}")

    def _handle_auth(self, data: Dict):
        err_info = data.get("ErrInfo")
        logger.error(f"Authentication error: {err_info}.")

    def _handle_chips(self, data: Dict):
        self._chips = data.get("ChipDict")

    def _handle_chip_config(self, data: Dict):
        self._chip_info = data.get("ChipConfig")

    def _handle_task_ack(self, data: Dict):
        self._task_id = data.get("TaskId")

    def _handle_task_status(self, data: Dict):
        self._task_status = data.get("TaskStatus")

    def _handle_task_result(self, data: Dict):
        self._task_result = data.get("TaskResult")

    async def _send_message(self, message: Dict):
        """发送消息通用方法"""
        self._event.clear()
        try:
            await self.sio.emit(event="message", data=message, namespace="/ws")
            # 增加超时机制可以使客户端更健壮
            await asyncio.wait_for(self._event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            logger.error("Request timed out.")
            raise UQCTimeoutError("Request timed out.")

    async def _connect_async(self):
        try:
            await self.sio.connect(
                uqc_config.SERVER_URL, headers={"Authorization": str(self._token)}, namespaces=["/ws"]
            )
        except Exception as e:
            logger.error(f"Error connecting to server: {e}")
            self.connected = False

    def _connect(self):

        if self.connected:
            return

        try:
            self._async_mgr.run(self._connect_async())

            if self.sio.connected:
                self.connected = True
            else:
                raise UQCConnectionError("Failed to connect to the server.")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise UQCConnectionError(f"Connection error: {e}")

    async def _disconnect(self):
        await self.sio.disconnect()
        self.connected = False

    async def _get_chips(self, chip_status: Optional[str] = "active"):
        """获取芯片列表信息"""
        if not self._token:
            raise UQCAuthenticationError("Missing access token")
        message = self._build_message(
            msg_type="MsgGetChips",
            body={"ChipStatus": chip_status or uqc_config.CHIP_STATUS},
        )
        await self._send_message(message)
        return self._chips

    def get_chips(self, chip_status: Optional[str] = None):
        """
        获取可用的量子芯片列表。

        Parameters
        ----------
        chip_status : str, optional
            查询的芯片状态，例如 "all", "active", "closed", "banned", "maintenance"，默认为 "active"。
            如果为 None，则默认查询 "active"状态。

        Returns
        -------
        list or None
            包含芯片信息的列表，如果请求失败或没有数据则可能返回 None。
        """
        return self._async_mgr.run(self._get_chips(chip_status=chip_status))

    async def _get_chip_info(self, chip_name: Optional[str] = None):
        """获取芯片信息"""
        if not self._token:
            raise UQCAuthenticationError("Missing access token")
        message = self._build_message(
            msg_type="MsgGetChipConfig",
            body={"SN": 0, "Chip": chip_name or uqc_config.DEFAULT_TASK_TARGET},
        )
        await self._send_message(message)
        return self._chip_info

    def get_chip_info(self, chip_name: Optional[str] = None):
        """
        获取指定芯片的信息
        Parameters
        ----------
        chip_name : str, optional
            查询的芯片名称，默认为 "Matrix2"。
            如果为 None，则默认使用 "Matrix2"。

        Returns
        -------
        dict or None
            包含芯片信息的字典，如果请求失败或没有数据则可能返回 None。
        """
        return self._async_mgr.run(self._get_chip_info(chip_name=chip_name))

    async def _submit_task(self, convert_qprog: str, target: Optional[str] = None, shots: Optional[int] = None):
        """提交量子计算任务"""
        if not self._token:
            raise UQCAuthenticationError("Missing access token")

        try:
            ensure_static_qasm(convert_qprog)
        except Exception:
            raise UQCTaskError("Error check qasm circle .")

        message = self._build_message(
            msg_type="MsgTask",
            body={
                "TaskId": str(uuid4()),
                "Target": target or uqc_config.DEFAULT_TASK_TARGET,
                "ConvertQProg": convert_qprog,
                "QProgType": uqc_config.DEFAULT_TASK_QPROGTYPE,
                "QProgVersion": uqc_config.DEFAULT_TASK_QProgVersion,
                "Configure": {
                    "Shot": shots or uqc_config.DEFAULT_SHOTS,
                    "IsProbCount": True,
                },
            },
        )

        await self._send_message(message)

        if self._task_id:
            shanghai_tz = pytz.timezone(uqc_config.USER_TIMEZONE)
            task_sub_time = str(datetime.now(shanghai_tz))
            await async_export({f"{self._task_id},{task_sub_time}"}, file_path=uqc_config.DEFAULT_TASKS_FILE_PATH)
        return self._task_id

    def submit_task(self, convert_qprog: str, target: Optional[str] = None, shots: Optional[int] = None):
        """
        提交量子计算任务
        Parameters
        ----------
        convert_qprog ：str
            qasm3格式的静态线路程序，不支持动态线路程序
            支持的门类型为："rzz", "rx", "ry", 及 "measure", "barrier"操作

        target : str, optional
            线路执行的目标芯片，默认为"Matrix2"
            如果为 None，则默认使用 "Matrix2"。

        shots : int, optional
            试验次数，默认为 100 次。
            如果为 None，则默认使用 100 次。

        Returns
        -------
        str or None
            任务 ID，如果提交失败则可能返回 None。

        """
        if shots is not None and (not isinstance(shots, int) or shots <= 0):
            raise UQCTaskError("Invalid shots value. It must be a positive integer.")
        if shots > uqc_config.MAX_SHOTS or shots % 100 != 0:
            raise UQCTaskError("Invalid shots value. It must be a multiple of 100 and less than or equal to 1000.")

        return self._async_mgr.run(self._submit_task(convert_qprog=convert_qprog, target=target, shots=shots))

    async def _get_task_status(self, task_id: Optional[str] = None):
        """获取任务状态"""
        if not self._token:
            raise UQCAuthenticationError("Missing access token")

        if not task_id and not self._task_id:
            raise UQCTaskError("Missing task id")

        message = self._build_message(
            msg_type="MsgTaskStatus",
            body={"SN": 0, "TaskId": task_id or self._task_id},
        )
        await self._send_message(message)
        return self._task_status

    def get_task_status(self, task_id: Optional[str] = None):
        """
        获取任务状态
        Parameters
        ----------
        task_id : str, optional
            查询的任务 ID，默认为 None。
            如果为 None，则默认使用上次提交的任务 ID。

        Returns
        -------
        str or None
            任务状态，如果获取失败则可能返回 None。

        """
        return self._async_mgr.run(self._get_task_status(task_id=task_id))

    async def _get_task_result(self, task_id: Optional[str] = None):
        """获取任务结果"""
        if not self._token:
            raise UQCAuthenticationError("Missing access token")
        if not task_id and not self._task_id:
            raise UQCTaskError("Missing task id")

        message = self._build_message(
            msg_type="MsgTaskResult",
            body={"SN": 0, "TaskId": task_id or self._task_id},
        )
        await self._send_message(message)
        return self._task_result

    def get_task_result(self, task_id: Optional[str] = None):
        """
        获取任务结果
        Parameters
        ----------
        task_id : str, optional
            查询的任务 ID，默认为 None。
            如果为 None，则默认使用上次提交的任务 ID。

        Returns
        -------
        dict or None
            任务结果，如果获取失败则可能返回 None。

        """
        return self._async_mgr.run(self._get_task_result(task_id=task_id))

    def _build_message(self, msg_type: str, body: Dict) -> Dict:
        """构建标准消息结构"""
        return {
            "Header": {
                "MsgType": msg_type,
                "Version": uqc_config.PROTOCOL_VERSION,
                "Authorization": self._token,
            },
            "Body": body,
        }
