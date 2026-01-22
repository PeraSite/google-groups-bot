import logging
import nodriver as uc

import add_groups_member
from csv_downloader import download_csv
from csv_reader import extract_emails

class GoogleGroups:
    def __init__(self, tab: uc.Tab, group_id: str):
        self.tab: uc.Tab = tab
        self.group_id: str = group_id
        
    async def prepare_members(self) -> None:
        await add_groups_member.navigate_to_groups_member(self.tab, self.group_id)

    async def get_members(self) -> list[str]:
        logging.debug(f"[GoogleGroups.get_members] Starting get_members for group_id={self.group_id}")
        csv_path = await download_csv(self.tab)
        logging.info(f"CSV 파일 경로: {csv_path}")
        emails = extract_emails(csv_path)
        logging.info(f"추출된 이메일: {emails}")
        logging.debug(f"[GoogleGroups.get_members] Completed get_members for group_id={self.group_id}, count={len(emails)}")
        return emails

    async def add_members(self, email: str) -> None:
        await add_groups_member.add_groups_member(self.tab, email)