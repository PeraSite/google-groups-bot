import asyncio
import nodriver as uc

from browser import create_tab, start_browser

async def add_groups_member(tab: uc.Tab, group_id: str, email: str) -> None:
    url = f"https://groups.google.com/g/{group_id}/members?hl=ko"
    _ = await tab.get(url)
    await asyncio.sleep(5)

    add_button = await tab.select('div[aria-label="회원 추가"]')
    if not add_button:
        raise Exception("회원 추가 버튼을 찾을 수 없습니다.")

    await add_button.click()

    add_member_checkbox = await tab.select('input[aria-labelledby="add-member-checkbox-label"]')
    if not add_member_checkbox:
        raise Exception("회원 추가 체크박스를 찾을 수 없습니다.")

    await add_member_checkbox.click()
    
    group_member_field = await tab.select('input[aria-label="그룹 멤버"]')
    if not group_member_field:
        raise Exception("그룹 멤버 입력칸을 찾을 수 없습니다.")

    await group_member_field.send_keys(email)
    await asyncio.sleep(3)

    member_ul = await tab.select('ul')
    if not member_ul:
        raise Exception("회원 목록을 찾을 수 없습니다.")

    member_li = await tab.select('div[data-aria-label="그룹 멤버"] ul:first-of-type > *:first-child')
    if not member_li:
        raise Exception("회원 목록을 찾을 수 없습니다.")
    await member_li.click()
    await asyncio.sleep(1)

    add_button = await tab.select_all('div[aria-label="회원 추가"]')
    if len(add_button) == 0:
        raise Exception("회원 추가 버튼을 찾을 수 없습니다.")
    await add_button[1].click()

    await asyncio.sleep(3)

    captcha_button = await tab.select_all('iframe[title="reCAPTCHA"]')
    if len(captcha_button) == 0:
        raise Exception("Captcha 확인 버튼을 찾을 수 없습니다.")
    print(captcha_button)
    await captcha_button[0].mouse_click()
    await asyncio.sleep(10)

    add_button = await tab.select_all('div[aria-label="회원 추가"]')
    if len(add_button) == 0:
        raise Exception("회원 추가 버튼을 찾을 수 없습니다.")
    print(add_button)
    await add_button[-1].click()
    await asyncio.sleep(3)

async def main():
    browser = await start_browser()
    tab = await create_tab(browser)
    await add_groups_member(tab, "didtest2", "test@example.com")

if __name__ == "__main__":
    asyncio.run(main())