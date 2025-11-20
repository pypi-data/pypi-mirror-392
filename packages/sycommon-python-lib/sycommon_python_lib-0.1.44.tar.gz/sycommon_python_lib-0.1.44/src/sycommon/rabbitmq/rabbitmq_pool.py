import asyncio
from typing import Optional, List, Set, Iterator, Tuple
from aio_pika import connect_robust, Channel, Message
from aio_pika.abc import (
    AbstractRobustConnection, AbstractQueue, AbstractExchange, AbstractMessage
)

from sycommon.logging.kafka_log import SYLogger

logger = SYLogger


class RabbitMQConnectionPool:
    """单连接RabbitMQ通道池（严格单连接）"""

    def __init__(
        self,
        hosts: List[str],
        port: int,
        username: str,
        password: str,
        virtualhost: str = "/",
        channel_pool_size: int = 1,
        heartbeat: int = 30,
        app_name: str = "",
        connection_timeout: int = 30,
        reconnect_interval: int = 30,
        prefetch_count: int = 2,
    ):
        self.hosts = [host.strip() for host in hosts if host.strip()]
        if not self.hosts:
            raise ValueError("至少需要提供一个RabbitMQ主机地址")

        # 连接配置（所有通道共享此连接的配置）
        self.port = port
        self.username = username
        self.password = password
        self.virtualhost = virtualhost
        self.app_name = app_name or "rabbitmq-client"
        self.heartbeat = heartbeat
        self.connection_timeout = connection_timeout
        self.reconnect_interval = reconnect_interval
        self.prefetch_count = prefetch_count
        self.channel_pool_size = channel_pool_size

        # 节点轮询：仅用于连接失效时切换节点（仍保持单连接）
        self._host_iterator: Iterator[str] = self._create_host_iterator()
        self._current_host: Optional[str] = None  # 当前连接的节点

        # 核心资源（严格单连接 + 通道池）
        self._connection: Optional[AbstractRobustConnection] = None  # 唯一连接
        self._free_channels: List[Channel] = []  # 通道池（仅存储当前连接的通道）
        self._used_channels: Set[Channel] = set()

        # 状态控制（确保线程安全）
        self._lock = asyncio.Lock()
        self._initialized = False
        self._is_shutdown = False
        self._reconnecting = False  # 避免重连并发冲突

    def _create_host_iterator(self) -> Iterator[str]:
        """创建节点轮询迭代器（无限循环，仅用于切换节点）"""
        while True:
            for host in self.hosts:
                yield host

    @property
    def is_alive(self) -> bool:
        """检查唯一连接是否存活（使用is_closed判断，兼容所有版本）"""
        if not self._initialized or not self._connection:
            return False
        # 异步清理失效通道（不影响主流程）
        asyncio.create_task(self._clean_invalid_channels())
        return not self._connection.is_closed

    async def _safe_close_resources(self):
        """安全关闭资源：先关通道，再关连接（保证单连接特性）"""
        async with self._lock:
            # 1. 关闭所有通道（无论空闲还是使用中）
            all_channels = self._free_channels + list(self._used_channels)
            for channel in all_channels:
                try:
                    if not channel.is_closed:
                        await channel.close()
                except Exception as e:
                    logger.warning(f"关闭通道失败: {str(e)}")
            self._free_channels.clear()
            self._used_channels.clear()

            # 2. 关闭唯一连接
            if self._connection:
                try:
                    if not self._connection.is_closed:
                        await self._connection.close()
                    logger.info(f"已关闭唯一连接: {self._current_host}:{self.port}")
                except Exception as e:
                    logger.warning(f"关闭连接失败: {str(e)}")
                self._connection = None  # 置空，确保单连接

    async def _create_single_connection(self) -> AbstractRobustConnection:
        """创建唯一连接（失败时轮询节点，切换前关闭旧连接）"""
        max_attempts = len(self.hosts)  # 每个节点尝试1次
        attempts = 0
        last_error: Optional[Exception] = None

        while attempts < max_attempts and not self._is_shutdown:
            next_host = next(self._host_iterator)

            # 切换节点前：强制关闭旧连接（保证单连接）
            if self._connection:
                await self._safe_close_resources()

            self._current_host = next_host
            conn_url = f"amqp://{self.username}:{self.password}@{self._current_host}:{self.port}/{self.virtualhost}"

            try:
                logger.info(f"尝试创建唯一连接: {self._current_host}:{self.port}")
                conn = await connect_robust(
                    conn_url,
                    properties={
                        "connection_name": f"{self.app_name}_single_conn",
                        "product": self.app_name
                    },
                    heartbeat=self.heartbeat,
                    timeout=self.connection_timeout,
                    reconnect_interval=self.reconnect_interval,
                    max_reconnect_attempts=None,  # 单节点内部自动重连
                )
                logger.info(f"唯一连接创建成功: {self._current_host}:{self.port}")
                return conn
            except Exception as e:
                attempts += 1
                last_error = e
                logger.error(
                    f"连接节点 {self._current_host}:{self.port} 失败（{attempts}/{max_attempts}）: {str(e)}",
                    exc_info=True
                )
                await asyncio.sleep(30)  # 避免频繁重试

        raise ConnectionError(
            f"所有节点创建唯一连接失败（节点列表: {self.hosts}）"
        ) from last_error

    async def _init_channel_pool(self):
        """初始化通道池（绑定到唯一连接，仅创建指定数量的通道）"""
        if not self._connection or self._connection.is_closed:
            raise RuntimeError("无有效连接，无法初始化通道池")

        async with self._lock:
            self._free_channels.clear()
            self._used_channels.clear()

            # 创建指定数量的通道（池大小由channel_pool_size控制）
            for i in range(self.channel_pool_size):
                try:
                    channel = await self._connection.channel()
                    await channel.set_qos(prefetch_count=self.prefetch_count)
                    self._free_channels.append(channel)
                except Exception as e:
                    logger.error(f"创建通道失败（第{i+1}个）: {str(e)}", exc_info=True)
                    # 通道创建失败不中断，继续创建剩余通道
                    continue

            logger.info(
                f"通道池初始化完成 - 连接: {self._current_host}:{self.port}, "
                f"可用通道数: {len(self._free_channels)}/{self.channel_pool_size}"
            )

    async def _reconnect_if_needed(self) -> bool:
        """连接失效时重连（保证单连接）"""
        if self._is_shutdown or self._reconnecting:
            return False

        self._reconnecting = True
        try:
            logger.warning("连接失效，开始重连...")
            # 重新创建唯一连接
            self._connection = await self._create_single_connection()
            # 重新初始化通道池
            await self._init_channel_pool()
            logger.info("重连成功，通道池已恢复")
            return True
        except Exception as e:
            logger.error(f"重连失败: {str(e)}", exc_info=True)
            self._initialized = False  # 重连失败后标记未初始化
            return False
        finally:
            self._reconnecting = False

    async def _clean_invalid_channels(self):
        """清理失效通道并补充（仅针对当前唯一连接）"""
        if not self._connection:
            return

        async with self._lock:
            # 1. 清理空闲通道中的失效通道
            valid_free = [
                chan for chan in self._free_channels if not chan.is_closed]
            invalid_count = len(self._free_channels) - len(valid_free)
            if invalid_count > 0:
                logger.warning(f"清理{invalid_count}个失效空闲通道")
            self._free_channels = valid_free

            # 2. 清理使用中通道中的失效通道
            valid_used = {
                chan for chan in self._used_channels if not chan.is_closed}
            invalid_used_count = len(self._used_channels) - len(valid_used)
            if invalid_used_count > 0:
                logger.warning(f"清理{invalid_used_count}个失效使用中通道")
            self._used_channels = valid_used

            # 3. 检查连接是否有效，无效则触发重连
            if self._connection.is_closed:
                await self._reconnect_if_needed()
                return

            # 4. 补充通道到指定大小（仅使用当前唯一连接创建）
            total_valid = len(self._free_channels) + len(self._used_channels)
            missing = self.channel_pool_size - total_valid
            if missing > 0:
                logger.info(f"通道池缺少{missing}个通道，补充中...")
                for _ in range(missing):
                    try:
                        channel = await self._connection.channel()
                        await channel.set_qos(prefetch_count=self.prefetch_count)
                        self._free_channels.append(channel)
                    except Exception as e:
                        logger.error(f"补充通道失败: {str(e)}", exc_info=True)
                        break

    async def init_pools(self):
        """初始化：创建唯一连接 + 初始化通道池（仅执行一次）"""
        if self._initialized:
            logger.warning("通道池已初始化，无需重复调用")
            return

        if self._is_shutdown:
            raise RuntimeError("通道池已关闭，无法初始化")

        try:
            # 1. 创建唯一连接
            self._connection = await self._create_single_connection()
            # 2. 初始化通道池（绑定到该连接）
            await self._init_channel_pool()
            self._initialized = True
            logger.info("RabbitMQ单连接通道池初始化完成")
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}", exc_info=True)
            await self._safe_close_resources()
            raise

    async def acquire_channel(self) -> Tuple[Channel, AbstractRobustConnection]:
        """获取通道（返回元组：(通道, 唯一连接)，兼容上层代码）"""
        if not self._initialized:
            raise RuntimeError("通道池未初始化，请先调用init_pools()")

        if self._is_shutdown:
            raise RuntimeError("通道池已关闭，无法获取通道")

        # 先清理失效通道，确保池内通道有效
        await self._clean_invalid_channels()

        async with self._lock:
            # 优先从空闲池获取
            if self._free_channels:
                channel = self._free_channels.pop()
                self._used_channels.add(channel)
                # 返回（通道, 唯一连接）元组
                return channel, self._connection

            # 通道池已满，创建临时通道（超出池大小，用完关闭）
            try:
                if not self._connection or self._connection.is_closed:
                    raise RuntimeError("唯一连接已失效，无法创建临时通道")

                channel = await self._connection.channel()
                await channel.set_qos(prefetch_count=self.prefetch_count)
                self._used_channels.add(channel)
                logger.warning(
                    f"通道池已达上限（{self.channel_pool_size}），创建临时通道（用完自动关闭）"
                )
                # 返回（通道, 唯一连接）元组
                return channel, self._connection
            except Exception as e:
                logger.error(f"获取通道失败: {str(e)}", exc_info=True)
                raise

    async def release_channel(self, channel: Channel, conn: AbstractRobustConnection):
        """释放通道（接收通道和连接参数，兼容上层代码）"""
        if not channel or not conn or self._is_shutdown:
            return

        # 仅处理当前唯一连接的通道（避免无效连接的通道）
        if conn != self._connection:
            try:
                await channel.close()
                logger.warning("已关闭非当前连接的通道（可能是重连后的旧通道）")
            except Exception as e:
                logger.warning(f"关闭非当前连接通道失败: {str(e)}")
            return

        async with self._lock:
            if channel not in self._used_channels:
                return

            self._used_channels.remove(channel)

            # 仅归还：当前连接有效 + 通道未关闭 + 池未满
            if (not self._connection.is_closed
                and not channel.is_closed
                    and len(self._free_channels) < self.channel_pool_size):
                self._free_channels.append(channel)
            else:
                # 无效通道直接关闭
                try:
                    await channel.close()
                except Exception as e:
                    logger.warning(f"关闭通道失败: {str(e)}")

    async def declare_queue(self, queue_name: str, **kwargs) -> AbstractQueue:
        """声明队列（使用池内通道，共享唯一连接）"""
        channel, conn = await self.acquire_channel()
        try:
            return await channel.declare_queue(queue_name, **kwargs)
        finally:
            await self.release_channel(channel, conn)

    async def declare_exchange(self, exchange_name: str, exchange_type: str = "direct", **kwargs) -> AbstractExchange:
        """声明交换机（使用池内通道，共享唯一连接）"""
        channel, conn = await self.acquire_channel()
        try:
            return await channel.declare_exchange(exchange_name, exchange_type, **kwargs)
        finally:
            await self.release_channel(channel, conn)

    async def publish_message(self, routing_key: str, message_body: bytes, exchange_name: str = "", **kwargs):
        """发布消息（使用池内通道，共享唯一连接）"""
        channel, conn = await self.acquire_channel()
        try:
            exchange = channel.default_exchange if not exchange_name else await channel.get_exchange(exchange_name)
            message = Message(body=message_body, **kwargs)
            await exchange.publish(message, routing_key=routing_key)
            logger.debug(
                f"消息发布成功 - 节点: {self._current_host}, 交换机: {exchange.name}, 路由键: {routing_key}"
            )
        except Exception as e:
            logger.error(f"发布消息失败: {str(e)}", exc_info=True)
            raise
        finally:
            await self.release_channel(channel, conn)

    async def consume_queue(self, queue_name: str, callback, auto_ack: bool = False, **kwargs):
        """消费队列（使用池内通道，共享唯一连接）"""
        if not self._initialized:
            raise RuntimeError("通道池未初始化，请先调用init_pools()")

        queue = await self.declare_queue(queue_name, **kwargs)
        current_channel, current_conn = await self.acquire_channel()  # 元组解包

        async def consume_callback_wrapper(message: AbstractMessage):
            """消费回调包装（处理通道失效重连）"""
            nonlocal current_channel, current_conn
            try:
                # 检查通道是否有效（连接可能已切换）
                if (current_channel.is_closed
                    or current_conn.is_closed
                        or current_conn != self._connection):
                    logger.warning("消费通道失效，重新获取通道...")
                    await self.release_channel(current_channel, current_conn)
                    current_channel, current_conn = await self.acquire_channel()
                    return

                await callback(message)
                if not auto_ack:
                    await message.ack()
            except Exception as e:
                logger.error(f"消费消息失败: {str(e)}", exc_info=True)
                if not auto_ack:
                    await message.nack(requeue=True)

        logger.info(f"开始消费队列: {queue_name}（连接节点: {self._current_host}）")
        try:
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    if self._is_shutdown:
                        logger.info("消费已停止，退出消费循环")
                        break
                    await consume_callback_wrapper(message)
        finally:
            await self.release_channel(current_channel, current_conn)

    async def close(self):
        """关闭通道池：释放所有通道 + 关闭唯一连接"""
        if self._is_shutdown:
            logger.warning("通道池已关闭，无需重复操作")
            return

        self._is_shutdown = True
        logger.info("开始关闭RabbitMQ单连接通道池...")

        # 安全释放所有资源
        await self._safe_close_resources()

        logger.info("RabbitMQ单连接通道池已完全关闭")
