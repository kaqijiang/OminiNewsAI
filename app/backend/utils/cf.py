import asyncio
from loguru import logger

# Cloudflare 挑战的标题和选择器
CHALLENGE_TITLES = [
    'Just a moment...',
    'DDoS-Guard'
]
CHALLENGE_SELECTORS = [
    '#cf-challenge-running', '.ray_id', '.attack-box', '#cf-please-wait', '#challenge-spinner', '#trk_jschal_js',
    'td.info #js_info', 'div.vc div.text-box h2', '#challenge-form', '#challenge-stage', 'main-wrapper'
]
SHORT_TIMEOUT = 2  # 秒

async def bypass(link, page):
    try:
        await page.goto(link)
        await asyncio.sleep(2)
        await page.wait_for_load_state('domcontentloaded')

        if await page.query_selector('[aria-label="Username"]'):
            logger.debug("页面已正常加载，没有发现 Cloudflare 挑战。")
            return

        challenge_found = await check_for_challenge(page)
        if challenge_found:
            await handle_challenge(page)
        # else:
        #     logger.debug("没有检测到 Cloudflare 挑战。")
    except Exception as e:
        logger.error(f"处理 Cloudflare 挑战时出错: {e}")

async def bypasslogin( page):
    try:

        await asyncio.sleep(2)
        await page.wait_for_load_state('domcontentloaded')

        if await page.query_selector('[aria-label="Username"]'):
            logger.debug("页面已正常加载，没有发现 Cloudflare 挑战。")
            return

        challenge_found = await check_for_challenge(page)
        if challenge_found:
            await handle_challenge(page)
        else:
            logger.debug("没有检测到 Cloudflare 挑战。")
    except Exception as e:
        logger.error(f"处理 Cloudflare 挑战时出错: {e}")

async def check_for_challenge(page):
    page_title = await page.title()
    if any(title.lower() == page_title.lower() for title in CHALLENGE_TITLES):
        return True

    # 对于每个选择器，只检查元素是否存在
    for selector in CHALLENGE_SELECTORS:
        if await page.query_selector(selector):
            return True
    return False


async def handle_challenge(page):
    for selector in CHALLENGE_SELECTORS:
        # logger.debug(f"检查选择器: {selector}")
        if await page.query_selector(selector):
            await click_verify(page)
            break
    logger.debug("挑战可能已解决！")

async def click_verify(page):
    try:
        iframe_element = await page.wait_for_selector("iframe")
        iframe = await iframe_element.content_frame()
        checkbox = await iframe.wait_for_selector('xpath=//*[@id="challenge-stage"]/div/label/input', state="visible")
        await checkbox.click()
        await page.wait_for_navigation()
        logger.debug("找到并点击了 Cloudflare 验证复选框！")
    except Exception as e:
        logger.debug(f"处理 Cloudflare 验证复选框时出错: {e}")

        # 尝试查找并点击“验证您是人类”按钮
        # try:
        #     logger.debug("尝试查找 Cloudflare '验证您是人类' 按钮...")
        #     button = await iframe.wait_for_selector("xpath=//input[@type='button' and @value='Verify you are human']", state="visible")
        #     await button.click()
        #     logger.debug("找到并点击了 Cloudflare '验证您是人类' 按钮！")
        # except Exception:
        #     logger.debug("页面上未找到 Cloudflare '验证您是人类' 按钮。")