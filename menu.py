import json
import time
import csv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Load configuration ---
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

email = config["email"]
password = config["password"]
login_url = config["login_url"]
menu_url = config["menu_create_url"]
wait_time = config.get("wait_time", 5)
menu_list = config["menu_list"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # --- Function to log in ---
    def login():
        print("🔐 Logging in...")
        try:
            page.goto(login_url)
            page.wait_for_selector("input[name='username']", timeout=10000)
            page.fill("input[name='username']", email)
            page.fill("input[name='password']", password)
            page.click("button:has-text('Sign In')")
            page.wait_for_url("**/dashboard", timeout=20000)
            print("✅ Logged in successfully.")
            print("=" * 60)
        except Exception as e:
            print("❌ Login failed!")
            print(f"Technical error: {e}")
            print("➡️  Check your login URL, username, or password in config.json")
            browser.close()
            exit(1)

    # --- Function to create one menu item ---
    def create_menu_item(item, wait_time=5):
        try:
            page.goto(menu_url)
            page.wait_for_selector("input[name='name']", timeout=10000)
            time.sleep(wait_time)

            # Fill Name
            page.fill("input[name='name']", item["name"])

            # Fill Price
            page.fill("input[name='price']", "")
            page.fill("input[name='price']", item["price"])

            # Fill Description (if available)
            if item.get("description"):
                try:
                    page.wait_for_selector("#description", timeout=5000)
                    page.fill("#description", item["description"])
                except PlaywrightTimeoutError:
                    raise Exception("Description box not found on the page.")

            # Select Category
            try:
                page.click("div[id^='categoryId'] .css-phxhil-control")
                page.fill("div[id^='categoryId'] input", item["category"])
                page.keyboard.press("Enter")
            except PlaywrightTimeoutError:
                raise Exception("Category dropdown not found or not clickable.")

            # Select Unit
            try:
                page.click("div[id^='unit'] .css-phxhil-control")
                page.fill("div[id^='unit'] input", item["unit"])
                page.keyboard.press("Enter")
            except PlaywrightTimeoutError:
                raise Exception("Unit dropdown not found or not clickable.")

            # Click Create
            try:
                page.click("button:has-text('Create')")
                time.sleep(wait_time)
            except PlaywrightTimeoutError:
                raise Exception("Create button not found or not clickable.")

            # If all steps pass
            return True

        except Exception as e:
            # Log error in a readable way
            print(f"❌ Failed to create menu item: {item['name']}")
            print("   👉 Reason:", str(e))
            print("   ⚙️  Tip: Check field names, spelling, or page loading time.")
            print("-" * 60)
            return False

    # --- Start ---
    login()

    # --- Read CSV file ---
    total_items = 0
    success_count = 0
    fail_count = 0

    with open(menu_list, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for idx, parts in enumerate(reader, start=1):
            if not parts or len(parts) < 4:
                print(f"[Line {idx}] ⚠️ Skipped (not enough fields): {parts}")
                continue

            total_items += 1

            # Prepare item dictionary
            item = {
                "unit": parts[0].strip(),
                "category": parts[1].strip(),
                "name": parts[2].strip(),
                "price": parts[3].strip(),
                "description": parts[4].strip() if len(parts) > 4 else None,
            }

            # Try creating item
            success = create_menu_item(item, wait_time)
            if success:
                success_count += 1
                print(f"[{idx}] ✅ Successfully created menu item:")
                print(f"   🏷️  Name         : {item['name']}")
                print(f"   📂  Category     : {item['category']}")
                print(f"   ⚖️  Unit         : {item['unit']}")
                print(f"   💰  Price        : {item['price']}")
                print(f"   📝  Description  : {item['description'] if item['description'] else '-'}")
                print("-" * 60)
            else:
                fail_count += 1

    # --- Summary ---
    print("\n📊 Summary Report")
    print("=" * 60)
    print(f"Total Items Tried : {total_items}")
    print(f"✅ Successfully Created : {success_count}")
    print(f"❌ Failed to Create     : {fail_count}")
    print("=" * 60)

    browser.close()
