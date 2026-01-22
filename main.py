import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from browser import create_tab, start_browser
from groups import GoogleGroups
from groups_monitor import GoogleGroupsMemberMonitor, LastSuccessfulResult
import nodriver as uc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

ENABLE_MONITOR = False
groups_member_monitor: GoogleGroupsMemberMonitor | None = None


async def initialize_monitor(group_id: str) -> GoogleGroupsMemberMonitor:
    browser = await start_browser()
    tab = await create_tab(browser)
    monitor = GoogleGroupsMemberMonitor(tab, group_id)
    _ = asyncio.create_task(monitor.run())
    return monitor


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global groups_member_monitor
    if ENABLE_MONITOR:
        groups_member_monitor = await initialize_monitor("didtest2")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/last-successful")
async def get_last_successful() -> LastSuccessfulResult:
    if groups_member_monitor is None:
        raise HTTPException(status_code=503, detail="Groups member monitor not initialized")

    return groups_member_monitor.get_last_successful()


@app.get("/groups/{group_id}/members")
async def get_members(group_id: str) -> list[str]:
    browser = await start_browser()
    tab = await create_tab(browser)
    groups = GoogleGroups(tab, group_id)
    members = await groups.get_members()
    await tab.close()
    return members


class AddMembersRequest(BaseModel):
    email: EmailStr


@app.post("/groups/{group_id}/members", status_code=204)
async def add_members(group_id: str, request: AddMembersRequest) -> None:
    browser = await start_browser()
    tab = await create_tab(browser)
    groups = GoogleGroups(tab, group_id)
    await groups.add_members(request.email)
    await tab.close()
    
