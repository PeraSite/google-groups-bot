import asyncio
import nodriver as uc


async def navigate_to_groups_member(tab: uc.Tab, group_id: str) -> None:
    url = f"https://groups.google.com/g/{group_id}/members?hl=ko"
    _ = await tab.get(url)


async def add_groups_member(tab: uc.Tab, email: str) -> None:
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

    member_ul = await tab.select('ul')
    if not member_ul:
        raise Exception("회원 목록을 찾을 수 없습니다.")

    member_li = await tab.select('div[data-aria-label="그룹 멤버"] ul:first-of-type > *:first-child')
    if not member_li:
        raise Exception("회원 목록을 찾을 수 없습니다.")
    await member_li.click()

    add_button = await tab.select_all('div[aria-label="회원 추가"]')
    if len(add_button) == 0:
        raise Exception("회원 추가 버튼을 찾을 수 없습니다.")
    await add_button[1].click()

    max_retries = 10
    for attempt in range(max_retries):
        try:
            captcha_token = await tab.select('#recaptcha-token', timeout=0)
            print(captcha_token.attrs['value'])
            await asyncio.sleep(3)
        except Exception as e:
            print(e)
            if attempt == max_retries - 1:
                raise Exception(f"Captcha 처리 실패: {max_retries}번 시도 후에도 실패했습니다. {str(e)}")
            await asyncio.sleep(1)

    while True:
        add_buttons = await tab.select_all('div[aria-label="회원 추가"]')
        if len(add_buttons) == 0:
            raise Exception("회원 추가 버튼을 찾을 수 없습니다.")
        add_button = add_buttons[-1]
        if not "aria-disabled" in add_button.attrs:
            await add_button.click()
            break
        await asyncio.sleep(1)
    
    await asyncio.sleep(3)