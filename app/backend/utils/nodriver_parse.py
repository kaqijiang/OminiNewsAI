import asyncio
from bs4 import BeautifulSoup
from nodriver import start
from utils.logging_config import LogManager

logger = LogManager.get_logger()

async def fetch_html(tab):
    html_content = await tab.get_content()
    soup = BeautifulSoup(html_content, 'html.parser')
    return ''.join(p.text.strip().replace('\n', '') for p in soup.find_all('p'))

async def get_content_from_page(url):
    # response = requests.get(url)
    # content = ''
    # # 检查请求是否成功
    # if response.status_code == 200:
    #     parse_content
    #     # 使用 BeautifulSoup 解析 HTML 内容
    #     soup = BeautifulSoup(response.text, 'html.parser')
    #     paragraphs = soup.find_all('p')
    #     for p in paragraphs:
    #         content += p.text.strip()
    #     content = content.replace('\n', '')
    browser = await start(browser_args=[
        '--window-size=300,520',
        '--window-position=0,0',
        '--accept-lang=en-US',
        '--no-first-run',
        '--disable-features=Translate',
        '--blink-settings=imagesEnabled=false',
        '--incognito'
    ], headless=True)
    tab = None
    content = ''
    try:
        tab = await browser.get(url)
        attempts = 0
        while attempts < 5 and not content:
            if attempts > 0:
                await asyncio.sleep(1)
            content = await fetch_html(tab)
            if 'Verifying you are human' in content:
                await tab.reload()
                content = await fetch_html(tab)
            attempts += 1
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        content = ""
    finally:
        if tab:
            await tab.close()
        browser.stop()
    return content
