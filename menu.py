import json
import time

from playwright.sync_api import sync_playwright

# --- Load configuration ---
with open("config.json", "r") as f:
    config = json.load(f)

email = config["email"]
password = config["password"]
login_url = config["login_url"]
menu_url = config["menu_create_url"]
wait_time = config.get("wait_time", 5)
menu_list = config["menu_list"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Use .firefox or .webkit if needed
    page = browser.new_page()

    # --- Function to login ---
    def login():
        page.goto(login_url)
        page.fill("input[name='username']", email)
        page.fill("input[name='password']", password)
        page.click("button:has-text('Sign In')")
        page.wait_for_url("**/dashboard")
        print("Logged in successfully.")

    # --- Function to create menu item ---
    def create_menu_item(item, wait_time=5):
        page.goto(menu_url)
        time.sleep(wait_time)

        # Fill Name
        page.fill("input[name='name']", item["name"])

        # Fill Price
        page.fill("input[name='price']", "")
        page.fill("input[name='price']", item["price"])

        # Fill Description if exists
        if item.get("description"):
            page.fill("#description", item["description"])

        # Select Category
        page.click("div[id^='categoryId'] .css-phxhil-control")
        page.fill("div[id^='categoryId'] input", item["category"])
        page.keyboard.press("Enter")

        # Select Unit
        page.click("div[id^='unit'] .css-phxhil-control")
        page.fill("div[id^='unit'] input", item["unit"])
        page.keyboard.press("Enter")

        # Click Create
        page.click("button:has-text('Create')")
        time.sleep(wait_time)

    # --- Login ---
    login()

    # --- Read data from file ---
    with open(menu_list, "r") as file:
        lines = file.read().splitlines()

    total_items = 0
    success_count = 0
    fail_count = 0

    # --- Loop through items ---
    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        total_items += 1
        parts = [x.strip() for x in line.split(",")]
        item = {
            "unit": parts[0],
            "category": parts[1],
            "name": parts[2],
            "price": parts[3],
            "description": ",".join(parts[4:]).strip() if len(parts) > 4 else None,
        }

        try:
            create_menu_item(item, wait_time)
            success_count += 1
            print(f"[Line {idx}] Created Menu Item: {item}")
        except Exception as e:
            fail_count += 1
            print(f"[Line {idx}] Failed to create item: {item['name']} - Error: {e}")

    print("\nSummary:")
    print(f"Total Items  : {total_items}")
    print(f"Created      : {success_count}")
    print(f"Failed       : {fail_count}")

    browser.close()
