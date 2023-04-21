import asyncio

import aioschedule as schedule


async def run_scheduler_loop():
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)
