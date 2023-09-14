"""Web scraping commands using Playwright"""
from __future__ import annotations

# from autogpt.logs import logger

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    logger.info(
        "Playwright not installed. Please install it with 'pip install playwright' to use."
    )
from bs4 import BeautifulSoup

# from autogpt.processing.html import extract_hyperlinks, format_hyperlinks


def scrape_text(url: str, need_login=False, username="", password="") -> str:
    """Scrape text from a webpage

    Args:
        url (str): The URL to scrape text from

    Returns:
        str: The scraped text
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            if need_login:
                page.type('#fm-login-id', username)
                page.type('#fm-login-password', password)
                page.click('.fm-button')
                # page.wait_for_selector('.site-nav-mytaobao')

            html_content = page.content()
            soup = BeautifulSoup(html_content, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

        except Exception as e:
            text = f"Error: {str(e)}"

        finally:
            browser.close()

    return text




# def scrape_links(url: str) -> str | list[str]:
#     """Scrape links from a webpage
#
#     Args:
#         url (str): The URL to scrape links from
#
#     Returns:
#         Union[str, List[str]]: The scraped links
#     """
#     with sync_playwright() as p:
#         browser = p.chromium.launch()
#         page = browser.new_page()
#
#         try:
#             page.goto(url)
#             html_content = page.content()
#             soup = BeautifulSoup(html_content, "html.parser")
#
#             for script in soup(["script", "style"]):
#                 script.extract()
#
#             hyperlinks = extract_hyperlinks(soup, url)
#             formatted_links = format_hyperlinks(hyperlinks)
#
#         except Exception as e:
#             formatted_links = f"Error: {str(e)}"
#
#         finally:
#             browser.close()
#
#     return formatted_links

def main():
    print(scrape_text(
        "https://login.taobao.com/member/login.jhtml",
        need_login=True,
        username="土土126",
        password="jackseaver79" ))
    # print(scrape_text("https://www.gui2000.com/www-notes/notes-102.html"))

if __name__ == "__main__":
    main()
