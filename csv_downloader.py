import asyncio
import logging
import nodriver as uc
from pathlib import Path

from browser import clear_download_directory, create_tab, get_download_dir, start_browser
from csv_reader import extract_emails


async def navigate_to_groups_member(tab: uc.Tab, group_id: str) -> None:
    logging.debug(f"🚀 [STEP 1/2] navigate_to_groups_member 시작 - group_id: {group_id}")
    
    url = f"https://groups.google.com/g/{group_id}/members?hl=ko"
    logging.debug(f"📍 [STEP 1/2] URL 생성 완료: {url}")
    
    logging.info(f"페이지 열기 중: {url}")
    _ = await tab.get(url)
    logging.info(f"페이지 열기 완료: {url}")
    
    logging.debug(f"✅ [STEP 1/2] navigate_to_groups_member 완료")


async def download_csv(tab: uc.Tab) -> Path:
    logging.debug(f"🚀 [STEP 2/2] download_csv 시작")
    
    logging.debug(f"🧹 다운로드 디렉토리 초기화 중...")
    clear_download_directory()
    logging.debug(f"✅ 다운로드 디렉토리 초기화 완료")

    # Debug: Check all .uArJ5e elements and their aria-label attributes
    logging.debug(f"🔍 .uArJ5e 엘리먼트들의 aria-label 확인 중...")
    try:
        aria_labels = await tab.evaluate("""
            (() => {
                try {
                    const elements = document.querySelectorAll('.uArJ5e');
                    return Array.from(elements).map(el => el.getAttribute('aria-label'));
                } catch (e) {
                    return [];
                }
            })()
        """)
        logging.debug(f"📋 발견된 aria-label 목록: {aria_labels}")
    except Exception as e:
        logging.debug(f"⚠️ aria-label 확인 중 오류 발생: {e}")
        aria_labels = []
        logging.debug(f"📋 발견된 aria-label 목록: {aria_labels}")
    
    # Find element with aria-label "목록 내보내기"
    logging.debug(f"🔍 '목록 내보내기' 버튼 찾는 중...")
    export_button = await tab.select('div[jsname="JV2Tqf"]')
    if not export_button:
        logging.error(f"❌ '목록 내보내기' 버튼을 찾을 수 없습니다!")
        raise Exception("목록 내보내기 버튼을 찾을 수 없습니다.")
    logging.debug(f"✅ '목록 내보내기' 버튼 찾기 완료")

    # Get initial file count in download directory
    logging.debug(f"📂 초기 파일 목록 확인 중...")
    initial_files = set(get_download_dir().glob("*"))
    logging.debug(f"📂 초기 파일 개수: {len(initial_files)}")
    
    # Click the export button
    logging.debug(f"🖱️ '목록 내보내기' 버튼 클릭 중...")
    await export_button.click()
    logging.debug(f"✅ '목록 내보내기' 버튼 클릭 완료")
    
    
    # Wait for download to complete (check for new files)
    max_wait = 50
    waited = 0
    logging.debug(f"⏳ 다운로드 대기 시작 (최대 {max_wait * 0.1}초)")
    logging.info("다운로드 대기 중...")
    
    while waited < max_wait:
        await asyncio.sleep(0.1)
        waited += 1
        
        # Check for new files
        current_files = set(get_download_dir().glob("*"))
        new_files = current_files - initial_files
        
        # Also check for .crdownload files (Chrome download in progress)
        downloading_files = list(get_download_dir().glob("*.crdownload"))
        
        if waited % 10 == 0:  # 1초마다 로그
            logging.debug(f"⏱️ {waited * 0.1}초 대기 중... (현재 파일: {len(current_files)}, 새 파일: {len(new_files)}, 다운로드 중: {len(downloading_files)})")
        
        if new_files and not downloading_files:
            # Download completed
            logging.debug(f"🎉 다운로드 완료 감지! 새 파일 개수: {len(new_files)}")
            for file_path in new_files:
                logging.info(f"다운로드 완료: {file_path.absolute()}")
                logging.debug(f"✅ [STEP 2/2] download_csv 완료 - 파일: {file_path.name}")
                return file_path
        elif downloading_files:
            if waited % 10 == 0:  # 1초마다 로그
                logging.info(f"다운로드 진행 중... ({waited * 0.1}초)")
    
    logging.error(f"❌ 다운로드 타임아웃! 대기 시간: {waited * 0.1}초")
    raise Exception("다운로드 타임아웃: 파일이 완전히 다운로드되지 않았을 수 있습니다.")