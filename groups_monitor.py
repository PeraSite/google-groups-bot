
import asyncio
import time
from datetime import datetime
import logging
import nodriver as uc
from pydantic import BaseModel

from csv_downloader import download_csv
from csv_reader import extract_emails
from groups import GoogleGroups


class LastSuccessfulResult(BaseModel):
    id: str
    time: datetime | None = None
    emails: list[str] | None = None
    
    def update(self, emails: list[str]) -> None:
        self.time = datetime.now()
        self.emails = emails


class GoogleGroupsMemberMonitor:
    def __init__(self, tab: uc.Tab, group_id: str, interval: int = 0):
        self.tab: uc.Tab = tab
        self.group_id: str = group_id
        self.interval: int = interval
        self.last_successful: LastSuccessfulResult = LastSuccessfulResult(id=group_id)
    

    def get_last_successful(self) -> LastSuccessfulResult:
        return self.last_successful


    async def run(self):
        while True:
            try:
                groups = GoogleGroups(self.tab, self.group_id)
                
                total_start = time.time()
                
                prepare_start = time.time()
                await groups.prepare_members()
                prepare_elapsed = time.time() - prepare_start
                #logging.info(f"prepare_members completed in {prepare_elapsed:.2f} seconds")
                
                get_members_start = time.time()
                emails = await groups.get_members()
                get_members_elapsed = time.time() - get_members_start
                #logging.info(f"get_members completed in {get_members_elapsed:.2f} seconds")
                
                total_elapsed = time.time() - total_start
                logging.info(f"Total time (prepare_members + get_members): {total_elapsed:.2f} seconds")
                
                self.last_successful.update(emails)
                logging.info(f"성공: {len(emails)}개의 이메일 추출 완료")
                
            except Exception as e:
                logging.error(f"오류 발생: {str(e)}", exc_info=True)
            
            await asyncio.sleep(self.interval)