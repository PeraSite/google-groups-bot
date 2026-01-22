import asyncio
import logging
import nodriver as uc
from pathlib import Path

from browser import clear_download_directory, create_tab, get_download_dir, start_browser
from csv_reader import extract_emails


async def download_csv(tab: uc.Tab, group_id: str) -> Path:
    url = f"https://groups.google.com/g/{group_id}/members?hl=ko"
    logging.info(f"페이지 열기 중: {url}")
    _ = await tab.get(url)
    logging.info(f"페이지 열기 완료: {url}")
    await asyncio.sleep(5)

    clear_download_directory()

    # Find element with aria-label "목록 내보내기"
    export_button = await tab.select('div[aria-label="목록 내보내기"]')
    if not export_button:
        raise Exception("목록 내보내기 버튼을 찾을 수 없습니다.")

    # Get initial file count in download directory
    initial_files = set(get_download_dir().glob("*"))
    
    # Click the export button
    await export_button.click()
    
    # Wait for download to complete (check for new files)
    logging.info("다운로드 대기 중...")
    max_wait = 5
    waited = 0
    
    while waited < max_wait:
        await asyncio.sleep(1)
        waited += 1
        
        # Check for new files
        current_files = set(get_download_dir().glob("*"))
        new_files = current_files - initial_files
        
        # Also check for .crdownload files (Chrome download in progress)
        downloading_files = list(get_download_dir().glob("*.crdownload"))
        
        if new_files and not downloading_files:
            # Download completed
            for file_path in new_files:
                logging.info(f"다운로드 완료: {file_path.absolute()}")
                return file_path
        elif downloading_files:
            logging.info(f"다운로드 진행 중... ({waited}초)")
    
    raise Exception("다운로드 타임아웃: 파일이 완전히 다운로드되지 않았을 수 있습니다.")