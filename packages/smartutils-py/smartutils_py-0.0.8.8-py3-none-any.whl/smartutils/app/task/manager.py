from abc import ABC, abstractmethod
from typing import AsyncGenerator, Generic, List, Optional

from smartutils.infra.cache.ext.queue.abstract import (
    AbstractSafeQueueT,
    Task,
    TaskID,
)
from smartutils.time import get_now_stamp


class TaskManager(Generic[AbstractSafeQueueT], ABC):
    def __init__(
        self, queue: str, pending: str, pool_num: int, cli: AbstractSafeQueueT
    ):
        self._pool_num = pool_num
        self._reverse_num = int(pool_num * 0.5)
        self._cli = cli
        self._queue = queue
        self._pending = pending
        self._pending_timeout = 3

    @abstractmethod
    async def get_todo_tasks(self, limit: int) -> List[Task]: ...

    async def warm_task(self):
        # 计算消费速率，预估填充任务数量
        fill_num = int(self._pool_num) - await self._cli.task_num(self._queue)
        if fill_num > 0:
            tasks = await self.get_todo_tasks(fill_num)
            await self._cli.enqueue_task(self._queue, tasks)

    async def fetch_task_ctx(self) -> AsyncGenerator[Optional[TaskID]]:
        # 存入pending时，使用负时间戳作为优先级，保证先进先出
        async with self._cli.fetch_task_ctx(
            self._queue, self._pending, priority=-get_now_stamp()
        ) as task:
            yield task

    async def handle_timeout_pending(self):
        # 优先级为负时间戳，提前 N 秒为超时区间
        # 取所有超时的pending任务，不包含刚领取的
        timeout_boundary = -(get_now_stamp() - self._pending_timeout)
        tasks = await self._cli.get_pending_members(
            self._pending, max_priority=timeout_boundary, limit=5
        )
        for task_id in tasks:
            await self._cli.requeue_task(self._queue, self._pending, task_id)

    async def run(self):
        while True:
            await self.warm_task()
            await self.handle_timeout_pending()
