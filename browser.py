from pathlib import Path
import nodriver as uc

# Create download directory
download_dir = Path("./downloads")
download_dir.mkdir(exist_ok=True)


def get_download_dir() -> Path:
    return download_dir


def clear_download_directory():
    for file in download_dir.glob("*"):
        file.unlink()


async def start_browser() -> uc.Browser:
    # Create a persistent user data directory for cookies and sessions
    user_data_dir = Path("./browser_profile")
    user_data_dir.mkdir(exist_ok=True)
    
    # Start the browser with persistent profile and download settings
    browser = await uc.start(user_data_dir=str(user_data_dir))
    return browser


async def create_tab(browser: uc.Browser) -> uc.Tab:
    tab = await browser.get()
    await tab.set_download_path(str(download_dir.absolute()))
    return tab