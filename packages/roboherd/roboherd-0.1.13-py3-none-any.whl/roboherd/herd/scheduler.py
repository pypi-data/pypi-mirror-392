import asyncio
import logging
from dataclasses import dataclass
from typing import List, Tuple

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from fast_depends import inject

from almabtrieb import Almabtrieb

from roboherd.cow import RoboCow, CronEntry

logger = logging.getLogger(__name__)


@dataclass
class HerdScheduler:
    entries: List[Tuple[RoboCow, CronEntry]]
    connection: Almabtrieb
    scheduler: AsyncIOScheduler | None = None
    task: asyncio.Task | None = None

    def create_task(self, task_group: asyncio.TaskGroup):
        if len(self.entries) == 0:
            logger.info("No tasks to schedule")
            return
        if self.task:
            raise Exception("Task already running")

        self.task = task_group.create_task(self.run())

    async def run(self):
        if len(self.entries) == 0:
            return

        if self.scheduler:
            raise Exception("Scheduler already exists")

        self.scheduler = AsyncIOScheduler()

        for cow, entry in self.entries:
            trigger = CronTrigger.from_crontab(entry.crontab)
            self.scheduler.add_job(
                inject(entry.func),
                trigger=trigger,
                kwargs={
                    "actor_id": cow.internals.actor_id,
                    "connection": self.connection,
                    "cow": cow,
                },
            )

        self.scheduler.start()

        while True:
            await asyncio.sleep(60 * 60)

    async def stop(self):
        logger.warning("Stopping scheduler")
        if self.scheduler:
            self.scheduler.shutdown()
        if self.task:
            self.task.cancel()
