#  python tools/vintrace_playwright_dispatch_search_console.py
import asyncio
import os
import sys
import datetime
import shutil
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page

CSV_SAVE_DIR = "Main/data/vintrace_reports/disp_console/"
os.makedirs(CSV_SAVE_DIR, exist_ok=True)

def sanitize_filename(s):
    return re.sub(r'[\\/*?:"<>|]', '_', str(s))

LARGE_TIMEOUT = 120000  # 2 minutes
DOWNLOAD_TIMEOUT = 240000  # 4 minutes

async def wait_for_vintrace_loader(page: Page, timeout=LARGE_TIMEOUT):
    """Waits only if the vintrace loader is visible."""
    is_visible = await page.evaluate("""
        () => {
            const el = document.getElementById('serverDelayMessageLong');
            return el && getComputedStyle(el).visibility === 'visible';
        }
    """)
    if is_visible:
        print("Waiting for vintrace loader to disappear...")
        await page.wait_for_function(
            """() => {
                const el = document.getElementById('serverDelayMessageLong');
                return el && getComputedStyle(el).visibility === 'hidden';
            }""",
            timeout=timeout
        )
    else:
        print("No vintrace loader visible, continuing immediately.")

async def wait_for_all_vintrace_loaders(page: Page, timeout=LARGE_TIMEOUT):
    """Waits for all vintrace loader overlays to be hidden."""
    await page.wait_for_function(
        """
        () => {
            const long = document.getElementById('serverDelayMessageLong');
            const main = document.getElementById('serverDelayMessage');
            const longHidden = !long || getComputedStyle(long).visibility === 'hidden';
            const mainHidden = !main || getComputedStyle(main).visibility === 'hidden';
            return longHidden && mainHidden;
        }
        """,
        timeout=timeout
    )

async def vintrace_login_and_navigate(page: Page, username: str, password: str, login_url: str, old_url: str):
    print("Navigating to login page...")
    await page.goto(login_url, timeout=LARGE_TIMEOUT)
    await page.wait_for_selector("#email", timeout=LARGE_TIMEOUT)
    await page.fill("#email", username)
    await page.fill("#password", password)
    login_btn = await page.query_selector("button[type='submit']:has-text('Login')")
    if login_btn:
        await login_btn.scroll_into_view_if_needed()
        await login_btn.click()
    else:
        print("Login button not found.")
        return False
    await page.wait_for_url(lambda url: url != login_url, timeout=LARGE_TIMEOUT)
    print("Login successful. Navigating to old vintrace URL...")
    await page.goto(old_url, timeout=LARGE_TIMEOUT)
    await page.wait_for_timeout(4000)
    print("Arrived at old vintrace URL.")
    return True

async def show_dispatch_search_options(page: Page):
    print("Attempting to click Search drop-down to show more options...")
    try:
        await page.wait_for_selector('#c_32SubMenuIMG', timeout=LARGE_TIMEOUT)
        await page.click('#c_32SubMenuIMG')
        print("Clicked the Search row drop-down image to show more options.")
    except Exception as e:
        print(f"Could not click the Search drop-down: {e}")

    print('Attempting to click "Dispatch search"...')
    try:
        await page.wait_for_selector('td#c_42_td_0', timeout=LARGE_TIMEOUT)
        await page.click('td#c_42_td_0')
        print('Clicked "Dispatch search" option.')
    except Exception as e:
        print('Could not click "Dispatch search":', e)

async def fill_dispatch_search_dates(page: Page, from_date: str, to_date: str):
    print(f"Setting From date: {from_date} and To date: {to_date}")
    try:
        await page.wait_for_selector('#c_353', timeout=LARGE_TIMEOUT)
        await page.fill('#c_353', from_date)
        print(f'Filled From date: {from_date}')
    except Exception as e:
        print(f"Could not fill From date: {e}")

    try:
        await page.wait_for_selector('#c_363', timeout=LARGE_TIMEOUT)
        await page.fill('#c_363', to_date)
        print(f'Filled To date: {to_date}')
    except Exception as e:
        print(f"Could not fill To date: {e}")

async def click_dispatch_search_button(page: Page):
    print('Attempting to click the "Search" button...')
    try:
        await page.wait_for_selector('#c_302', timeout=LARGE_TIMEOUT)
        await page.click('#c_302')
        print('Clicked "Search" button.')
    except Exception as e:
        print(f'Could not click "Search" button: {e}')

async def get_dispatch_table_keys(page: Page):
    """Collects all (date, bol, quantity) tuples from the current table view."""
    await page.wait_for_selector("#c_305_tbody > tr", timeout=LARGE_TIMEOUT)
    rows = await page.query_selector_all("#c_305_tbody > tr")
    keys = []
    for row in rows:
        cells = await row.query_selector_all("td")
        if len(cells) > 2:
            date = (await cells[0].inner_text()).strip().replace("/", "-")
            bol = (await cells[1].inner_text()).strip()
            quantity = (await cells[2].inner_text()).strip()
            keys.append((date, bol, quantity))
    return keys

async def select_dispatch_table_row_by_key(page: Page, key_tuple):
    """Selects a row by its (date, bol, quantity) tuple."""
    # Wait for overlays to be gone before interacting with the table
    await wait_for_all_vintrace_loaders(page)
    await page.wait_for_selector("#c_305_tbody > tr", timeout=LARGE_TIMEOUT)
    rows = await page.query_selector_all("#c_305_tbody > tr")
    for i, row in enumerate(rows):
        cells = await row.query_selector_all("td")
        if len(cells) > 2:
            date = (await cells[0].inner_text()).strip().replace("/", "-")
            bol = (await cells[1].inner_text()).strip()
            quantity = (await cells[2].inner_text()).strip()
            if (date, bol, quantity) == key_tuple:
                await row.scroll_into_view_if_needed()
                # Wait again right before clicking in case a loader pops up
                await wait_for_all_vintrace_loaders(page)
                await row.click()
                print(f"Clicked row with Date {date}, BOL {bol}, Quantity {quantity} (index {i}) in the dispatch table.")
                await page.wait_for_timeout(2000)
                code = (await cells[4].inner_text()).strip()
                return {"bol": bol, "date": date, "code": code, "quantity": quantity}
    print(f"Record {key_tuple} not found in table.")
    return False

async def click_view_wine_details(page: Page):
    print('Attempting to click the "View wine details" button...')
    try:
        await page.wait_for_selector('button:has-text("View wine details")', timeout=LARGE_TIMEOUT)
        await page.click('button:has-text("View wine details")')
        print('Clicked "View wine details" button.')
        await page.wait_for_timeout(2000)
        return True
    except Exception as e:
        print(f'Could not click "View wine details" button: {e}')
        return False

async def should_wait_before_fruit_tab(page: Page):
    # Returns True if the loading spinner is visible, else False.
    is_visible = await page.evaluate("""
        () => {
            const el = document.getElementById('serverDelayMessageLong');
            return el && getComputedStyle(el).visibility === 'visible';
        }
    """)
    return bool(is_visible)

async def click_fruit_tab(page: Page):
    print('Attempting to click the "Fruit" tab...')
    try:
        # Only wait if loading spinner is visible
        if await should_wait_before_fruit_tab(page):
            print("Loading spinner visible before clicking fruit tab. Waiting 6 seconds.")
            await page.wait_for_timeout(6000)
        else:
            print("No spinner before fruit tab, continuing immediately.")
        await page.wait_for_selector('div.tabInactive, div.tabActive', timeout=LARGE_TIMEOUT)
        fruit_tabs = await page.query_selector_all('div.tabInactive, div.tabActive')
        clicked = False
        for tab in fruit_tabs:
            tab_text = (await tab.inner_text()).strip()
            if tab_text.lower() == "fruit":
                await tab.scroll_into_view_if_needed()
                await tab.click()
                print('Clicked "Fruit" tab, waiting for tab to activate...')
                await page.wait_for_function(
                    """(el) => el.className.includes('tabActive')""",
                    arg=tab,
                    timeout=200000
                )
                await wait_for_vintrace_loader(page)
                # Wait for at least two visible CSV buttons with exact text "CSV"
                for _ in range(10):  # retry for up to ~5 seconds
                    csv_buttons = []
                    for button in await page.query_selector_all('button:visible'):
                        text = (await button.inner_text()).strip()
                        if text == "CSV":
                            csv_buttons.append(button)
                    if len(csv_buttons) >= 2:
                        break
                    await page.wait_for_timeout(500)
                clicked = True
                break
        if not clicked:
            print('Could not find or click "Fruit" tab.')
            return False
        return True
    except Exception as e:
        print(f'Could not click "Fruit" tab: {e}')
        return False

async def download_all_csv_buttons(page: Page, save_prefix: str, info: dict):
    try:
        # Wait for at least two visible CSV buttons with exact text "CSV"
        await page.wait_for_selector('button:visible', timeout=LARGE_TIMEOUT)
        csv_buttons = []
        for button in await page.query_selector_all('button:visible'):
            text = (await button.inner_text()).strip()
            if text == "CSV":
                csv_buttons.append(button)
        retries = 0
        while len(csv_buttons) < 2 and retries < 10:
            await page.wait_for_timeout(500)
            csv_buttons = []
            for button in await page.query_selector_all('button:visible'):
                text = (await button.inner_text()).strip()
                if text == "CSV":
                    csv_buttons.append(button)
            retries += 1
        if len(csv_buttons) != 2:
            print(f"Did not find two visible 'CSV' buttons (found {len(csv_buttons)}).")
            return False, False

        filenames = []
        for idx, button in enumerate(csv_buttons):
            async with page.expect_download(timeout=DOWNLOAD_TIMEOUT) as download_info:
                await button.click()
                print(f'Clicked CSV button #{idx+1}')
            download = await download_info.value
            temp_path = await download.path()
            bol = sanitize_filename(info.get('bol', 'unknown'))
            date = sanitize_filename(info.get('date', 'unknown'))
            code = sanitize_filename(info.get('code', 'unknown'))
            quantity = sanitize_filename(info.get('quantity', 'unknown'))
            fn = f"{save_prefix}_{idx+1}_BOL_{bol}_Date_{date}_Qty_{quantity}_Code_{code}.csv"
            save_path = os.path.join(CSV_SAVE_DIR, fn)
            shutil.move(temp_path, save_path)
            print(f"Downloaded CSV moved to {save_path}")
            filenames.append(save_path)
        return True, True  # If both downloaded
    except Exception as e:
        print(f"Could not download or move CSV from CSV buttons: {e}")
        return False, False

async def close_wine_details_window(page: Page):
    print("Attempting to close the wine details window...")
    try:
        await page.wait_for_selector('div[id$="_close"].echo2-window-pane-close', timeout=LARGE_TIMEOUT)
        close_buttons = await page.query_selector_all('div[id$="_close"].echo2-window-pane-close')
        clicked = False
        for button in close_buttons:
            if await button.is_visible():
                await button.scroll_into_view_if_needed()
                for _ in range(2):
                    await button.click()
                    await page.wait_for_timeout(1000)
                    try:
                        visible = await button.is_visible()
                    except Exception:
                        visible = False
                    if not visible:
                        print("Closed the wine details window.")
                        clicked = True
                        break
                if clicked:
                    break
        # Wait for the table behind the dialog to be visible as a sign the window is closed
        await wait_for_all_vintrace_loaders(page)
        await page.wait_for_selector("#c_305_tbody > tr", state="visible", timeout=LARGE_TIMEOUT)
        await page.wait_for_timeout(500)  # let the UI settle

        if not clicked:
            print("No visible close button found or close did not take effect.")
            return False
        return True
    except Exception as e:
        print(f"Could not close the wine details window: {e}")
        return False

def month_ranges(start: str, end: str):
    current = datetime.datetime.strptime(start, "%m/%d/%Y")
    end_dt = datetime.datetime.strptime(end, "%m/%d/%Y")
    while current <= end_dt:
        first = current.replace(day=1)
        last = (first + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
        last = min(last, end_dt)
        yield (first.strftime("%m/%d/%Y"), last.strftime("%m/%d/%Y"))
        current = last + datetime.timedelta(days=1)

async def process_all_table_rows(page: Page):
    keys = await get_dispatch_table_keys(page)
    row_count = len(keys)
    for i, key_tuple in enumerate(keys):
        print(f"\n--- Processing record {i+1} of {row_count} (Date: {key_tuple[0]}, BOL: {key_tuple[1]}, Qty: {key_tuple[2]}) ---")
        # Build expected filenames
        info = {
            "bol": key_tuple[1],
            "date": key_tuple[0],
            "quantity": key_tuple[2],
            "code": ""  # will fill after selecting the row
        }
        bulk_pattern = f"report_1_BOL_{sanitize_filename(info['bol'])}_Date_{sanitize_filename(info['date'])}_Qty_{sanitize_filename(info['quantity'])}_Code_.*\\.csv"
        fruit_pattern = f"report_2_BOL_{sanitize_filename(info['bol'])}_Date_{sanitize_filename(info['date'])}_Qty_{sanitize_filename(info['quantity'])}_Code_.*\\.csv"
        bulk_exists = any(re.fullmatch(bulk_pattern, f) for f in os.listdir(CSV_SAVE_DIR))
        fruit_exists = any(re.fullmatch(fruit_pattern, f) for f in os.listdir(CSV_SAVE_DIR))
        if bulk_exists and fruit_exists:
            print(f"Skipping {key_tuple}: Both CSVs already exist.")
            continue

        info = await select_dispatch_table_row_by_key(page, key_tuple)
        if not info:
            print(f"Skipping {key_tuple}: could not select or gather info.")
            continue
        if not await click_view_wine_details(page):
            print(f"Skipping {key_tuple}: could not open wine details.")
            continue
        if not await click_fruit_tab(page):
            print(f"Skipping {key_tuple}: could not open Fruit tab.")
            continue
        bulk_downloaded, fruit_downloaded = await download_all_csv_buttons(page, save_prefix="report", info=info)
        if bulk_downloaded and fruit_downloaded:
            print("Both CSV files downloaded and moved.")
        else:
            print("One or both CSV downloads failed.")
        await close_wine_details_window(page)
        await page.wait_for_timeout(1000)  # shorter pause, UI is ready quickly

async def perform_monthly_dispatch_search(page: Page, start_date: str, end_date: str):
    for from_date, to_date in month_ranges(start_date, end_date):
        print(f"\n=== Processing dispatch search for {from_date} to {to_date} ===")
        await fill_dispatch_search_dates(page, from_date, to_date)
        await click_dispatch_search_button(page)
        await page.wait_for_timeout(1000)
        await process_all_table_rows(page)

REPORT_CONFIG = {
    "reports_icon_id": "c_170",
    "reports_icon_fallback": "div[title='Reports']",
    "tab_menu_id": "c_382|Text",
}

async def main():
    load_dotenv()
    USERNAME = os.getenv("VINTRACE_USER")
    PASSWORD = os.getenv("VINTRACE_PW")
    LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"
    OLD_URL = "https://us61.vintrace.net/smwe/2.app?oldVintrace=true"

    if not USERNAME or not PASSWORD:
        print("VINTRACE_USER or VINTRACE_PW environment variables not set.")
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        # Step 1: Login and navigate to old vintrace
        success = await vintrace_login_and_navigate(page, USERNAME, PASSWORD, LOGIN_URL, OLD_URL)
        if not success:
            print("Login failed.")
            await browser.close()
            return

        # Step 2: Click Search drop-down and Dispatch search
        await show_dispatch_search_options(page)

        # Step 3: For each month in the range, search, then process all records in table
        await perform_monthly_dispatch_search(page, "08/01/2024", "08/31/2024")

if __name__ == "__main__":
    asyncio.run(main())