import logging
import nodriver as uc

from csv_downloader import download_csv
from csv_reader import extract_emails

class GoogleGroups:
    def __init__(self, tab: uc.Tab, group_id: str):
        self.tab: uc.Tab = tab
        self.group_id: str = group_id

    async def get_members(self) -> list[str]:
        csv_path = await download_csv(self.tab, self.group_id)
        logging.info(f"CSV 파일 경로: {csv_path}")
        emails = extract_emails(csv_path)
        logging.info(f"추출된 이메일: {emails}")
        return emails