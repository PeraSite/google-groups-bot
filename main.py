import asyncio
import logging
import time
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
global_tab: uc.Tab | None = None

# Single flight pattern: 같은 group_id에 대한 동시 요청을 하나로 통합
_get_members_flights: dict[str, asyncio.Task[list[str]]] = {}


async def initialize_monitor(group_id: str) -> GoogleGroupsMemberMonitor:
    max_retries = 10
    retry_interval = 1.0
    
    for attempt in range(max_retries):
        if global_tab is not None:
            monitor = GoogleGroupsMemberMonitor(global_tab, group_id)
            _ = asyncio.create_task(monitor.run())
            return monitor
        
        if attempt < max_retries - 1:
            logging.info(f"global_tab is None, waiting {retry_interval} seconds before retry (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(retry_interval)
    
    raise Exception(f"Failed to initialize monitor: global_tab is None after {max_retries} attempts ({max_retries * retry_interval} seconds)")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global groups_member_monitor, global_tab
    browser = await start_browser()
    global_tab = await create_tab(browser)
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
    if global_tab is None:
        raise HTTPException(status_code=503, detail="Tab not initialized")
    groups = GoogleGroups(global_tab, group_id)
    await groups.prepare_members()
    members = await groups.get_members()
    return members


@app.post("/groups/{group_id}/prepare", status_code=204)
async def prepare_members(group_id: str) -> None:
    if global_tab is None:
        raise HTTPException(status_code=503, detail="Tab not initialized")
    groups = GoogleGroups(global_tab, group_id)
    await groups.prepare_members()


class AddMembersRequest(BaseModel):
    email: EmailStr


@app.post("/groups/{group_id}/members", status_code=204)
async def add_members(group_id: str, request: AddMembersRequest) -> None:
    if global_tab is None:
        raise HTTPException(status_code=503, detail="Tab not initialized")
    start_time = time.time()
    groups = GoogleGroups(global_tab, group_id)
    await groups.add_members(request.email)
    elapsed_time = time.time() - start_time
    logging.info(f"add_members completed in {elapsed_time:.2f} seconds for group_id={group_id}, email={request.email}")
    
