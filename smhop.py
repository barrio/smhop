#!/usr/bin/env python


from pprint import pp
import string
import time

from playwright.sync_api import sync_playwright
import parsel
import IPython
import nest_asyncio

nest_asyncio.apply()


URL = "https://www.rewe.de/angebote/goettingen/241057/rewe-markt-reinhaeuser-landstr-177/"
button_css = string.Template("li.sos-navigation__categories-item:nth-child($num) > a:nth-child(1)")


def scroll(page, js=False):
    if js:
        page.evaluate("""
        let items=document.querySelectorAll('a');
        items[items.length-1].scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
        """)
        return
    while True:
        products = page.locator("a")
        (products_on_page := products.element_handles())[-1].scroll_into_view_if_needed()
        num_products_on_page = len(products_on_page)
        page.wait_for_timeout(10_000)
        num_products_on_page_after_scroll = len(products_on_page)
        if num_products_on_page_after_scroll > num_products_on_page:
            continue
        else:
            break


def main():
    angebote = []
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.goto(URL)

        cookie_button = "#uc-center-container > div.sc-eBMEME.ixkACg > div > div.sc-jsJBEP.iXSECa > div > button:nth-child(2)"
        page.wait_for_selector(cookie_button)
        page.click(cookie_button)

        for i in range(4, 16):
            page.locator(button_css.safe_substitute(num=i)).click()

        html = page.content()
        selector = parsel.Selector(text=html)
        a_tags = selector.css("a")

        #IPython.embed()

        angebote += [
            angebot.split(" €")[0] for a_tag in a_tags
            if (angebot := a_tag.attrib.get("aria-label"))
            and angebot.find("€") > -1
        ]
        pp(angebote)
        input()


if __name__ == '__main__':
    main()
