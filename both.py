import csv
import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

# --- Load configuration ---
with open("config.json", "r") as f:
    config = json.load(f)

email = config["email"]
password = config["password"]
login_url = config["login_url"]
category_url = config["category_create_url"]
menu_url = config["menu_create_url"]
wait_time = config.get("wait_time", 5)
csv_file = config["both"]

def log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {msg}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # --- Login ---
    def login():
        log("Step 1: Logging in...")
        start = time.time()
        page.goto(login_url)
        page.fill("input[name='username']", email)
        page.fill("input[name='password']", password)
        page.click("button:has-text('Sign In')")
        page.wait_for_url("**/dashboard")
        log(f"Logged in successfully in {time.time() - start:.2f}s")

    # --- Create category ---
    def create_category(name, cost_center):
        log(f"Creating category: {name} ({cost_center})")
        start = time.time()
        page.goto(category_url)
        page.wait_for_load_state("networkidle")

        page.fill("input[name='name']", name)
        cost_input = page.wait_for_selector("div#costCenterId input[type='text']", state="visible", timeout=30000)
        cost_input.click()
        cost_input.fill(cost_center)
        page.wait_for_timeout(200)
        cost_input.press("Enter")

        save_btn = page.wait_for_selector("button:has-text('Save')", state="visible", timeout=30000)
        save_btn.click()
        page.wait_for_timeout(wait_time * 1000)
        log(f"Category '{name}' created in {time.time() - start:.2f}s")

    # --- Create menu item ---
    def create_menu_item(item):
        log(f"Creating menu item: {item['name']}")
        start = time.time()
        page.goto(menu_url)
        page.wait_for_load_state("networkidle")

        page.fill("input[name='name']", item["name"])
        page.fill("input[name='price']", "")
        page.fill("input[name='price']", item["price"])
        if item.get("description"):
            page.fill("#description", item["description"])

        # Select Category
        cat_input = page.wait_for_selector("div[id^='categoryId'] input[type='text']", state="visible", timeout=30000)
        cat_input.click()
        cat_input.fill(item["category"])
        page.wait_for_timeout(200)
        cat_input.press("Enter")

        # Select Unit
        unit_input = page.wait_for_selector("div[id^='unit'] input[type='text']", state="visible", timeout=30000)
        unit_input.click()
        unit_input.fill(item["unit"])
        page.wait_for_timeout(200)
        unit_input.press("Enter")

        create_btn = page.wait_for_selector("button:has-text('Create')", state="visible", timeout=30000)
        create_btn.click()
        page.wait_for_timeout(wait_time * 1000)
        log(f"Menu item '{item['name']}' created in {time.time() - start:.2f}s")

    # --- Start Automation ---
    overall_start = time.time()
    login()

    # --- Read CSV ---
    rows = []
    unique_categories = {}

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            cat_name = row["category"].strip()
            cost_center = row.get("cost center", "").strip() or "Default"
            if cat_name not in unique_categories:
                unique_categories[cat_name] = cost_center

    # --- Create all categories first ---
    log("\nStep 2: Creating Categories...")
    for name, cost_center in unique_categories.items():
        try:
            create_category(name, cost_center)
        except Exception as e:
            log(f"Failed to create category '{name}' - Error: {e}")

    # --- Create all menu items ---
    log("\nStep 3: Creating Menu Items...")
    for item in rows:
        try:
            create_menu_item(item)
        except Exception as e:
            log(f"Failed to create menu item '{item['name']}' - Error: {e}")

    log(f"\nAutomation Complete in {time.time() - overall_start:.2f}s")
    browser.close()
