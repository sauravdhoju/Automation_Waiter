import json
import time
from playwright.sync_api import sync_playwright

# --- Load configuration ---
with open("config.json", "r") as f:
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

    # --- Login function ---
    def login():
        page.goto(login_url)
        page.fill("input[name='username']", email)
        page.fill("input[name='password']", password)
        page.click("button:has-text('Sign In')")
        page.wait_for_url("**/dashboard")
        print("Logged in successfully.")

    # --- Create category function ---
    def create_category(item, wait_time=5):
        page.goto(category_url)
        page.wait_for_load_state("networkidle")  # Wait until page is fully loaded

        # Enter Category Name
        page.fill("input[name='name']", item['category_name'])

        # --- Select Cost Center ---
        cost_input = page.wait_for_selector("div#costCenterId input[type='text']", state="visible", timeout=30000)
        cost_input.click()
        cost_input.fill(item["category"])
        page.wait_for_timeout(200)  # short delay
        cost_input.press("Enter")

        # Click Save
        save_btn = page.wait_for_selector("button:has-text('Save')", state="visible", timeout=30000)
        save_btn.click()
        page.wait_for_timeout(wait_time * 1000)

    # --- Start automation ---
    login()

    # --- Read categories from file ---
    with open(category_list, "r") as file:
        lines = file.read().splitlines()

    total = 0
    success = 0
    fail = 0

    # --- Loop through categories ---
    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        total += 1
        parts = [x.strip() for x in line.split(",")]
        item = {
            "category_name": parts[0],
            "category": parts[1]   # used for cost center
        }

        try:
            create_category(item, wait_time)
            success += 1

            # --- Print detailed info ---
            print(f"[Line {idx}] Created Category:")
            print(f"   Category Name : {item['category_name']}")
            print(f"   Cost Center   : {item['category']}")
            print("-" * 50)

        except Exception as e:
            fail += 1
            print(f"[Line {idx}] Failed to create category '{item['category_name']}' - Error: {e}")
            print("-" * 50)

    # --- Summary ---
    print("\nSummary:")
    print(f"Total Categories : {total}")
    print(f"Created          : {success}")
    print(f"Failed           : {fail}")

    browser.close()
