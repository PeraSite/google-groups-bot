import asyncio
from browser import create_tab, start_browser
from csv_downloader import download_csv
from csv_reader import extract_emails


async def main():
    browser = await start_browser()
    tab = await create_tab(browser)
    while True:
        csv_path = await download_csv(tab, "didtest2")
        print(csv_path)
        emails = extract_emails(csv_path)
        print(emails)
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
