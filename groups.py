import logging
import nodriver as uc

import add_groups_member
from csv_downloader import download_csv
from csv_reader import extract_emails

class GoogleGroups:
    def __init__(self, tab: uc.Tab, group_id: str):
        logging.debug(f"🏗️ [GoogleGroups.__init__] 초기화 시작 - group_id: {group_id}")
        self.tab: uc.Tab = tab
        self.group_id: str = group_id
        logging.debug(f"✅ [GoogleGroups.__init__] 초기화 완료 - group_id: {group_id}")
        
    async def prepare_members(self) -> None:
        logging.debug(f"🚀 [GoogleGroups.prepare_members] 시작 - group_id: {self.group_id}")
        await add_groups_member.navigate_to_groups_member(self.tab, self.group_id)
        logging.debug(f"✅ [GoogleGroups.prepare_members] 완료 - group_id: {self.group_id}")

    async def get_members(self) -> list[str]:
        logging.debug(f"🚀 [GoogleGroups.get_members] 시작 - group_id: {self.group_id}")
        
        logging.debug(f"📥 CSV 다운로드 시작...")
        csv_path = await download_csv(self.tab)
        logging.info(f"CSV 파일 경로: {csv_path}")
        logging.debug(f"✅ CSV 다운로드 완료: {csv_path.name}")
        
        logging.debug(f"📧 이메일 추출 시작...")
        emails = extract_emails(csv_path)
        logging.info(f"추출된 이메일: {emails}")
        logging.debug(f"✅ 이메일 추출 완료 - 개수: {len(emails)}")
        
        logging.debug(f"✅ [GoogleGroups.get_members] 완료 - group_id: {self.group_id}, 멤버 수: {len(emails)}")
        return emails

    async def add_members(self, email: str) -> None:
        logging.debug(f"🚀 [GoogleGroups.add_members] 시작 - email: {email}, group_id: {self.group_id}")
        await add_groups_member.add_groups_member(self.tab, email)
        logging.debug(f"✅ [GoogleGroups.add_members] 완료 - email: {email}")