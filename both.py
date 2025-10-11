import json
import time
import csv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def main():
    print("=" * 60)
    print("🍽️  Restaurant Automation Tool")
    print("=" * 60)
    print("Select an option:")
    print("1️⃣  Create Categories")
    print("2️⃣  Create Menu Items")
    print("0️⃣  Exit")
    print("=" * 60)

    choice = input("👉 Enter your choice (1/2/0): ").strip()

    if choice == "1":
        run_category_creator()
    elif choice == "2":
        run_menu_creator()
    else:
        print("👋 Exiting program...")
        exit(0)

# ---------------------------------------------------------
# CATEGORY CREATOR
# ---------------------------------------------------------
def run_category_creator():
    print("\n📁 Running Category Creator...\n")

    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    email = config["email"]
    password = config["password"]
    login_url = config["login_url"]
    category_url = config["category_create_url"]
    category_list = config["category_list"]
    wait_time = config.get("wait_time", 5)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        def login():
            print("🔐 Logging in...")
            page.goto(login_url)
            page.fill("input[name='username']", email)
            page.fill("input[name='password']", password)
            page.click("button:has-text('Sign In')")
            page.wait_for_url("**/dashboard")
            print("✅ Logged in successfully.\n")

        def create_category(item, wait_time=5):
            page.goto(category_url)
            page.wait_for_load_state("networkidle")
            page.fill("input[name='name']", item['category_name'])

            # Select cost center
            cost_input = page.wait_for_selector("div#costCenterId input[type='text']", state="visible", timeout=20000)
            cost_input.click()
            cost_input.fill(item["category"])
            page.wait_for_timeout(300)
            cost_input.press("Enter")

            save_btn = page.wait_for_selector("button:has-text('Save')", state="visible", timeout=20000)
            save_btn.click()
            page.wait_for_timeout(wait_time * 1000)

        # Start process
        login()

        with open(category_list, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()

        total, success, fail = 0, 0, 0

        for idx, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            total += 1
            parts = [x.strip() for x in line.split(",")]
            item = {"category_name": parts[0], "category": parts[1]}

            try:
                create_category(item, wait_time)
                success += 1
                print(f"[{idx}] ✅ Created Category: {item['category_name']} (Cost Center: {item['category']})")
            except Exception as e:
                fail += 1
                print(f"[{idx}] ❌ Failed to create category '{item['category_name']}' - {e}")
            print("-" * 60)

        print("\n📊 Category Creation Summary")
        print("=" * 60)
        print(f"Total Categories : {total}")
        print(f"✅ Created        : {success}")
        print(f"❌ Failed         : {fail}")
        print("=" * 60)
        browser.close()

# ---------------------------------------------------------
# MENU CREATOR
# ---------------------------------------------------------
def run_menu_creator():
    print("\n🍴 Running Menu Creator...\n")

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
                browser.close()
                exit(1)

        def create_menu_item(item, wait_time=5):
            try:
                page.goto(menu_url)
                page.wait_for_selector("input[name='name']", timeout=10000)
                time.sleep(wait_time)

                # Fill name and price
                page.fill("input[name='name']", item["name"])
                page.fill("input[name='price']", "")
                page.fill("input[name='price']", item["price"])

                # Description
                if item.get("description"):
                    try:
                        page.wait_for_selector("#description", timeout=5000)
                        page.fill("#description", item["description"])
                    except PlaywrightTimeoutError:
                        raise Exception("Description box not found.")

                # Category
                try:
                    page.click("div[id^='categoryId'] .css-phxhil-control")
                    page.fill("div[id^='categoryId'] input", item["category"])
                    page.keyboard.press("Enter")
                except PlaywrightTimeoutError:
                    raise Exception("Category dropdown not found or not clickable.")

                # Unit
                try:
                    page.click("div[id^='unit'] .css-phxhil-control")
                    page.fill("div[id^='unit'] input", item["unit"])
                    page.keyboard.press("Enter")
                except PlaywrightTimeoutError:
                    raise Exception("Unit dropdown not found or not clickable.")

                # Create
                page.click("button:has-text('Create')")
                time.sleep(wait_time)

                return True

            except Exception as e:
                print(f"❌ Failed to create menu item: {item['name']}")
                print("   👉 Reason:", str(e))
                print("-" * 60)
                return False

        # Start
        login()

        total_items = success_count = fail_count = 0

        with open(menu_list, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for idx, parts in enumerate(reader, start=1):
                if not parts or len(parts) < 4:
                    print(f"[Line {idx}] ⚠️ Skipped (not enough fields): {parts}")
                    continue

                total_items += 1

                item = {
                    "unit": parts[0].strip(),
                    "category": parts[1].strip(),
                    "name": parts[2].strip(),
                    "price": parts[3].strip(),
                    "description": parts[4].strip() if len(parts) > 4 else None,
                }

                success = create_menu_item(item, wait_time)
                if success:
                    success_count += 1
                    print(f"[{idx}] ✅ Created: {item['name']}")
                else:
                    fail_count += 1

        print("\n📊 Menu Creation Summary")
        print("=" * 60)
        print(f"Total Items Tried : {total_items}")
        print(f"✅ Created         : {success_count}")
        print(f"❌ Failed          : {fail_count}")
        print("=" * 60)
        browser.close()


# ---------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
