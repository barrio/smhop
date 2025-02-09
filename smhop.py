#!/usr/bin/env python


from pprint import pp
import string
import time

import IPython
import nest_asyncio
import parsel
from playwright.sync_api import sync_playwright

nest_asyncio.apply()


url = "https://www.rewe.de/angebote/goettingen/241057/rewe-markt-reinhaeuser-landstr-177/"
cookie_button = "#uc-center-container > div.sc-eBMEME.ixkACg > div > div.sc-jsJBEP.iXSECa > div > button:nth-child(2)"
categories_button_css = string.Template("li.sos-navigation__categories-item:nth-child($num) > a:nth-child(1)")


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


def create_page(playwright_context):
    browser = playwright_context.firefox.launch(headless=False)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    return context.new_page()


def click_cookie_banner(page):
    page.wait_for_selector(cookie_button)
    page.click(cookie_button)


def cycle_categories(page):
    for i in range(4, 16):
        page.locator(categories_button_css.safe_substitute(num=i)).click()


def get_products(html, css):
    selector = parsel.Selector(text=html)
    a_tags = selector.css(css)

    return [
        angebot.split(" €")[0].replace(",", "", 1)
        for a_tag in a_tags
        if (angebot := a_tag.attrib.get("aria-label"))
        and angebot.find("€") > -1
    ]


def main():
    with sync_playwright() as playwright_context:
        page = create_page(playwright_context)
        page.goto(url)
        click_cookie_banner(page)
        cycle_categories(page)
        angebote = get_products(page.content(), "a")
        #angebote = [product.replace(",", "", 1) for product in angebote]
        with open("rewe_angebote.txt", "w") as rewe_file:
            rewe_file.write("\n".join(angebote))


if __name__ == '__main__':
    main()
