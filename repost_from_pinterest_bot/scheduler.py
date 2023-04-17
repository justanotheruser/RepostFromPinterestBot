import asyncio
import logging
from typing import Optional

import aioschedule as schedule


async def run_scheduler_loop():
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)


class JobScheduler:
    def __init__(self):
        self.job: Optional[schedule.Job] = None

    def reschedule(self, hours: int, job_fn):
        if hours > 0:
            if self.job:
                logging.info(f'Cancelling previously scheduled job')
                schedule.cancel_job(self.job)
            logging.info(f'Scheduled posting every {hours} hour(s)')
            # TODO: seconds->hours
            self.job = schedule.every(hours).seconds.do(job_fn)
