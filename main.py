from playwright.sync_api import sync_playwright
import argparse
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)

########################
########################
########################

items_requested = 37
website = "https://www.amazon.de"
query = "harry potter buch"



def collect_n_items_on_page(page, items_required = 16):

    items = []

    if items_required > 16 or items_required <= 0:
        logging.error(" Invalid number of items requested")
        return items


    #### JUST IN CASE, u can try 4 or 5
    for i in range(3):
        page.evaluate("""
        () => {
          const el = document.scrollingElement || document.documentElement || document.body;
          if (el) window.scrollTo(0, el.scrollHeight);
        }
        """)
        page.wait_for_timeout(1500)

    results = page.locator("div[data-component-type='s-search-result']")

    for i in range(results.count()):

        if(len(items) >= items_required):
            logging.debug(f" Required amount reached . Exiting ...")
            return items

        r = results.nth(i)

        if r.locator("text=Sponsored").count() > 0:
            logger.info(f" 1 NEW (Sponsored) item found, skipping ... ")
            continue

        title_el = r.locator("h2 span")
        if title_el.count() == 0:
            logger.debug(f" Error No title found . Skipping ...")
            continue

        try:
            title = title_el.inner_text().strip()

        except Exception as e:
            logger.debug(f" Error Failed to read title text at index {i}: {type(e).__name__}")

        if not title:
            logger.debug(f" Error No title found . Skipping ...")
            continue


        ############################
        price = None
        price_el = r.locator("span.a-price > span.a-offscreen")

        if price_el.count() > 0:
            try:
                price = price_el.first.inner_text().strip()
            except Exception as e:
                logger.debug(
                    f" Failed to read price for '{title}': {type(e).__name__}"
                )

        if price is None:
            logger.debug(f" No price found for '{title}'")


        ############################

        logger.info(f" 1 NEW item found : {title}...")
        items.append({
            "title": title,
            "price": price,
        })


        logger.info(f" Item added : {title}...")


    return items

def collect_items(page, items_requested=32, max_pages=100):

    collected_items = []
    page_num = 1

    while page_num < max_pages :

        items_required = items_requested - len(collected_items)
        if items_required <= 0:
            break
        elif items_required <= 16:
            items = collect_n_items_on_page(page, items_required)
            collected_items.extend(items)
            break


        items = collect_n_items_on_page(page)
        collected_items.extend(items)

        next_btn = page.locator("a.s-pagination-next")

        if next_btn.count() == 0:
            logging.error(f" Error No next page button")
            break

        cls = next_btn.get_attribute("class") or ""
        if "s-pagination-disabled" in cls:
            logging.error(f"Error Next page disabled")
            break

        next_btn.click()
        logging.info(f"Switching page ...")
        page.wait_for_load_state("domcontentloaded")

        page_num += 1

    return collected_items



def parse_website(website: str, query: str, items_requested=32, silent_mode = True):

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=silent_mode)

        logger.info(f"Launching browser...")

        page = browser.new_page()
        page.goto(website, timeout=60000)

        page.wait_for_selector("#twotabsearchtextbox", timeout=60000)
        page.fill("#twotabsearchtextbox", query)
        page.press("#twotabsearchtextbox", "Enter")

        page.wait_for_selector(
            "div[data-component-type='s-search-result']",
            timeout=60000
        )

        items = collect_items(page, items_requested=items_requested)

        logger.info(f"\nTotal items on page: {len(items)}")

        browser.close()

        return items

def dump_items_to_json(items, path="collected_items.json"):
    logger.info(f"Dumping {len(items)} items to {path}")

    with open(path, "w", encoding="utf-8") as f:
        json.dump( items, f,indent=2 , ensure_ascii=False)

    logger.info("JSON dump completed")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="pwparser", description="Simple CLI parser for amazon website")
    parser.add_argument("--website", default=website, help="website url")
    parser.add_argument("--query", default=query, help="simple query for searching goods")
    parser.add_argument("--n", default=items_requested, help="Amount of items required to parse [1, 100]")
    parser.add_argument("--out", default="collected_items.json", help="Output json file name(default - collected_items.json)")
    parser.add_argument("--silent_mode", default=True, help="flag to parse websites without showing GUI [TRUE/FALSE]")

    args = parser.parse_args()

    items_requested = args.n
    query = args.query
    website = args.website
    outputfile = args.out
    silent_mode = args.silent_mode

    if(args.n > 100 or args.n < 1):
        logging.error("Invalid amount of items requested [1, 100]")

    logger.info(f"Running amazon search, logs level{logger.level}")
    logger.info(f"Website - {website}, Query: {query}, Items requested: {items_requested}")

    collected_items = parse_website(website, query, items_requested, False)
    dump_items_to_json(collected_items, outputfile)

    logger.info(f"Collected {len(collected_items)}/{items_requested} items. Exiting...")
