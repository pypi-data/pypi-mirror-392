import asyncio
from typing import AsyncGenerator

import grpc

from geodrive.logging import get_logger
from ..commands import RoverCommands
from .base import BaseCommunicator
from ..generated import (
    RoverServiceStub,
    DifferentialCommand,
    LedCustomCommand,
    VelocityCommand,
    TelemetryData,
    GotoProgress,
    GotoCommand,
    BatteryData,
    RoverStatus,
    LedCommand,
    CommandAck,
    GotoAck,
    Empty
)

logger = get_logger("gRPC-communicator")


class AsyncGRPCCommunicator(BaseCommunicator):
    """
    Асинхронный gRPC клиент для управления ровером.

    Обеспечивает двустороннюю связь с роботом через gRPC протокол.
    Поддерживает отправку команд, получение телеметрии и потоковую передачу данных.

    :param host: IP-адрес или hostname ровера. По умолчанию "localhost"
    :type host: str
    :param port: Порт gRPC сервера. По умолчанию 5656
    :type port: int
    """
    
    def __init__(self, host: str = "localhost", port: int = 5656):
        super().__init__()
        self.host: str = host
        self.port: int = port
        self.channel: grpc.aio.Channel | None = None
        self.stub: RoverServiceStub | None = None
        self._is_connected: bool = False

        self._alive_task: asyncio.Task | None = None
        self._alive_check_interval: int = 3
        self._reconnect_attempts: int = 0
        self._max_reconnect_delay: int = 10

    @property
    def is_connected(self) -> bool:
        """
        Проверить подключение к роверу.

        :return: True если подключение активно
        :rtype: bool
        """
        return self._is_connected

    async def _check_connection(self):
        """
        Проверка соединения
        """
        request = Empty()
        await self.stub.get_status(request)

    async def connect(self) -> bool:
        """
        Установить соединение с ровером.

        Выполняет подключение к gRPC серверу ровера и проверяет доступность.

        :return: True если подключение успешно, False в случае ошибки
        :rtype: bool
        """
        try:
            self.channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
            self.stub = RoverServiceStub(self.channel)
            
            await asyncio.wait_for(
                self._check_connection(),
                timeout=5.0
            )
            
            self._is_connected = True
            if self._alive_task is None:
                self._alive_task = asyncio.create_task(self.__alive_monitor())
            return True
            
        except Exception:
            await self.disconnect()
            return False

    async def disconnect(self):
        """
        Отключиться от ровера
        """
        if self.channel:
            await self.channel.close()
            self.channel = None
            self.stub = None
            self._is_connected = False

    async def send_command(
            self,
            command: RoverCommands,
            **kwargs
    ) -> CommandAck:
        """
        Отправить команду роверу.

        :param command: Тип команды из RoverCommands
        :type command: RoverCommands
        :param kwargs: Параметры команды
        :return: Результат выполнения команды
        :rtype: CommandAck
        """
        request = Empty()

        match command:
            case RoverCommands.SET_VELOCITY:
                request = VelocityCommand(**kwargs)
                response = await self.stub.set_velocity(request)
            case RoverCommands.SET_DIFF_SPEED:
                request = DifferentialCommand(**kwargs)
                response = await self.stub.set_differential_speed(request)
            case RoverCommands.LED_CONTROL:
                request = LedCommand(**kwargs)
                response = await self.stub.led_control(request)
            case RoverCommands.LED_CUSTOM:
                request = LedCustomCommand(**kwargs)
                response = await self.stub.led_custom(request)
            case RoverCommands.STOP:
                response = await self.stub.stop(request)
            case RoverCommands.EMERGENCY_STOP:
                response = await self.stub.emergency_stop(request)
            case RoverCommands.GOTO_CANCEL:
                response = self.stub.goto_cancel(request)
            case RoverCommands.BEEP:
                response = await self.stub.beep(request)
            case RoverCommands.MOO:
                response = await self.stub.moo(request)
            case _:
                response = CommandAck(
                    success=False,
                    message=f"Unknown command: {command}"
                )
        return response

    async def get_status(self) -> RoverStatus:
        """
        Получить текущий статус ровера.

        :return: Объект статуса ровера
        :rtype: RoverStatus
        """
        request = Empty()
        response = await self.stub.get_status(request)
        return response

    async def get_battery_status(self) -> BatteryData:
        """
        Получить данные о заряде батареи ровера.

        Возвращает данные о заряде батареи ровера.

        :return: Статус батареи с полями voltage и percentage
        :rtype: int
        """
        request = Empty()
        response = await self.stub.get_battery_status(request)
        return response

    async def get_telemetry(self) -> TelemetryData:
        """
        Получить телеметрию ровера.

        Возвращает данные о положении, скорости и углах эйлера ровера.

        :return: Объект телеметрии
        :rtype: TelemetryData
        """
        request = Empty()
        response = await self.stub.get_telemetry(request)
        return response

    async def stream_telemetry(self) -> AsyncGenerator[TelemetryData, None]:
        """
        Получить поток телеметрии в реальном времени.

        :return: Асинхронный генератор объектов TelemetryData
        :rtype: AsyncGenerator[TelemetryData, None]
        """
        request = Empty()
        async for response in self.stub.stream_telemetry(request):
            yield response

    async def goto(
            self,
            x: float,
            y: float,
            yaw: float | None
    ) -> GotoAck:
        request = GotoCommand(target_x=x, target_y=y, target_yaw=yaw)
        response = await self.stub.goto(request)
        return response

    async def goto_stream_position(
            self,
            x: float,
            y: float,
            yaw: float | None=None
    ) -> AsyncGenerator[GotoProgress, None]:
        command = GotoCommand(target_x=x, target_y=y)
        if yaw is not None:
            command.target_yaw = yaw
        progress_stream = self.stub.goto_stream_position(command)

        async for progress in progress_stream:
            yield progress

    async def __alive_monitor(self):
        while True:
            try:
                if self.channel and self.stub:
                    try:
                        await asyncio.wait_for(self.get_status(), timeout=1.0)
                        self._is_connected = True
                        self._reconnect_attempts = 0
                    except asyncio.TimeoutError:
                        logger.warning("Connection lost, attempting to reconnect...")
                        self._is_connected = False
                        await self._reconnect()
                else:
                    self._is_connected = False
                    await self._reconnect()

                await asyncio.sleep(self._alive_check_interval)

            except Exception as e:
                logger.error(f"Alive monitor error: {e}")
                await asyncio.sleep(self._alive_check_interval)

    async def _reconnect(self):
        """
        Попытка переподключения с экспоненциальной задержкой
        """
        try:
            delay = min(2 ** self._reconnect_attempts, self._max_reconnect_delay)
            logger.info(f"Reconnecting in {delay} seconds (attempt {self._reconnect_attempts + 1})")
            await asyncio.sleep(delay)

            if self.channel:
                await self.channel.close()

            self.channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
            self.stub = RoverServiceStub(self.channel)

            try:
                await asyncio.wait_for(self.get_status(), timeout=1.0)
                self._is_connected = True
                self._reconnect_attempts = 0
                logger.info("Reconnected successfully")
            except asyncio.TimeoutError:
                self._reconnect_attempts += 1
                self._is_connected = False

        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            self._reconnect_attempts += 1
            self._is_connected = False
