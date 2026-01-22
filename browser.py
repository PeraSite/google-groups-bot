from pathlib import Path
import nodriver as uc
import shutil

# Create download directory
download_dir = Path("./downloads")
download_dir.mkdir(exist_ok=True)


def get_download_dir() -> Path:
    return download_dir


def clear_download_directory():
    for file in download_dir.glob("*"):
        file.unlink()


async def start_browser():
    # 1. 경로 정의
    inject_source = Path("/app/session_inject") # 마운트된 알짜배기 폴더
    work_dir = Path("/app/run_profile")         # 실제 크롬이 돌아갈 작업 경로
    default_dir = work_dir / "Default"          # 크롬 데이터가 들어갈 핵심 위치

    # 2. 작업 경로 초기화 (이전 실행 찌꺼기 완전 삭제)
    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)
    
    # 3. 디렉토리 구조 생성
    default_dir.mkdir(parents=True, exist_ok=True)

    # 4. 필수 파일 주입 (여기가 핵심!)
    print("💉 Injecting login session files...")
    
    try:
        # (1) Cookies 파일 복사
        if (inject_source / "Cookies").exists():
            shutil.copy2(inject_source / "Cookies", default_dir / "Cookies")
            print("   - Cookies injected ✅")
        
        # (2) Preferences 파일 복사
        if (inject_source / "Preferences").exists():
            shutil.copy2(inject_source / "Preferences", default_dir / "Preferences")
            print("   - Preferences injected ✅")

        # (3) Local Storage 폴더 복사
        if (inject_source / "Local Storage").exists():
            shutil.copytree(inject_source / "Local Storage", default_dir / "Local Storage", dirs_exist_ok=True)
            print("   - Local Storage injected ✅")
            
    except Exception as e:
        print(f"⚠️ Injection Warning: {e}")

    # 5. 브라우저 시작
    browser = await uc.start(
        user_data_dir=str(work_dir), # 주입 완료된 경로로 시작
        browser_args=[
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--headless=new"
        ]
    )
    return browser


async def create_tab(browser: uc.Browser) -> uc.Tab:
    tab = await browser.get()
    await tab.set_download_path(str(download_dir.absolute()))
    return tab