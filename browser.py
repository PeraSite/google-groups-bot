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
    inject_source = Path("/app/session_inject")
    work_dir = Path("/app/run_profile")
    default_dir = work_dir / "Default"

    # 1. 기존 실행 프로필 초기화 (찌꺼기 제거)
    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)
    
    default_dir.mkdir(parents=True, exist_ok=True)

    print("💉 Injecting session files...")

    try:
        # [수정 1] Preferences는 복사하지 마세요! (충돌 원인 1순위)
        # if (inject_source / "Preferences").exists():
        #     shutil.copy2(...) 

        # [수정 2] Cookies는 필수
        if (inject_source / "Cookies").exists():
            shutil.copy2(inject_source / "Cookies", default_dir / "Cookies")
            print("   - Cookies injected ✅")

        # # [수정 3] Local Storage 복사 시 'LOCK' 파일은 제외 (충돌 방지)
        # if (inject_source / "Local Storage").exists():
        #     shutil.copytree(
        #         inject_source / "Local Storage", 
        #         default_dir / "Local Storage", 
        #         dirs_exist_ok=True,
        #         # 중요: LOCK 파일과 임시 파일을 무시합니다.
        #         ignore=shutil.ignore_patterns("LOCK", "*.lock", "*.tmp")
        #     )
        #     print("   - Local Storage injected (Safely) ✅")
            
    except Exception as e:
        print(f"⚠️ Injection Warning: {e}")


    browser_executable = shutil.which("chromium")

    # 2. 브라우저 시작
    browser = await uc.start(
        user_data_dir=str(work_dir),
        browser_executable=browser_executable,
        browser_args=[
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--headless=new",
            "--window-size=1920,1080"   # 화면 크기가 너무 작아도 렌더링 터질 수 있음
            "--lang=ko_KR",             # 한국어 설정 (구글 페이지 언어 고정)
            # [추가] 렌더링 관련 크래시 방지 옵션들
            "--disable-software-rasterizer", # SW 렌더러 비활성화
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-default-apps",
            "--mute-audio"
        ]
    )
    return browser


async def create_tab(browser: uc.Browser) -> uc.Tab:
    tab = await browser.get()
    await tab.set_download_path(str(download_dir.absolute()))
    return tab