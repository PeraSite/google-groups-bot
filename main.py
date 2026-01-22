import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from browser import create_tab, start_browser
from groups import GoogleGroups
from groups_monitor import GoogleGroupsMemberMonitor, LastSuccessfulResult
import nodriver as uc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

ENABLE_MONITOR = False

browser: uc.Browser | None = None
groups_member_monitor: GoogleGroupsMemberMonitor | None = None


async def initialize_monitor(browser: uc.Browser, group_id: str) -> GoogleGroupsMemberMonitor:
    tab = await create_tab(browser)
    monitor = GoogleGroupsMemberMonitor(tab, group_id)
    _ = asyncio.create_task(monitor.run())
    return monitor


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global browser, groups_member_monitor
    browser = await start_browser()
    if ENABLE_MONITOR:
        groups_member_monitor = await initialize_monitor(browser, "didtest2")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/last-successful")
async def get_last_successful() -> LastSuccessfulResult:
    if groups_member_monitor is None:
        raise HTTPException(status_code=503, detail="Groups member monitor not initialized")

    return groups_member_monitor.get_last_successful()


@app.get("/groups/{group_id}/members")
async def get_members(group_id: str) -> list[str]:
    if browser is None:
        raise HTTPException(status_code=503, detail="Browser not initialized")

    tab = await create_tab(browser)
    groups = GoogleGroups(tab, group_id)
    return await groups.get_members()