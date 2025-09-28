from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# --- Load configuration ---
with open("config.json", "r") as f:
    config = json.load(f)

email = config["email"]
password = config["password"]
browser = config.get("browser", "brave")
browser_path = config.get("browser_path", "/usr/bin/brave-browser")
login_url = config["login_url"]
menu_url = config["menu_create_url"]
wait_time = config.get("wait_time", 5)
menu_list = config["menu_list"]

# --- Initialize browser ---
options = webdriver.ChromeOptions()
if browser.lower() == "brave":
    options.binary_location = browser_path

driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 20)

# --- Function to login ---
def login(driver, wait, email, password, login_url):
    driver.get(login_url)
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[text()='Sign In']").click()
    wait.until(EC.url_contains("dashboard"))
    print("Logged in successfully.")

# --- Function to create menu item ---
def create_menu_item(driver, wait, menu_url, item, wait_time=5):
    driver.get(menu_url)
    time.sleep(wait_time)  # Wait for page & React Select to initialize

    # Fill Name
    name_input = wait.until(EC.presence_of_element_located((By.NAME, "name")))
    name_input.clear()
    name_input.send_keys(item["name"])

    # Fill Price
    price_input = wait.until(EC.presence_of_element_located((By.NAME, "price")))
    price_input.send_keys(Keys.BACKSPACE)
    price_input.send_keys(item["price"])

    # Fill Description if exists
    if item.get("description"):
        desc_input = wait.until(EC.presence_of_element_located((By.ID, "description")))
        desc_input.clear()
        desc_input.send_keys(item["description"])

    # Select Category
    category_container = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[id^='categoryId'] .css-phxhil-control")))
    category_container.click()
    category_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[id^='categoryId'] input")))
    category_input.send_keys(item["category"])
    category_input.send_keys(Keys.ENTER)

    # Select Unit
    unit_container = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[id^='unit'] .css-phxhil-control")))
    unit_container.click()
    unit_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[id^='unit'] input")))
    unit_input.send_keys(item["unit"])
    unit_input.send_keys(Keys.ENTER)

    # Click Create
    create_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Create']")))
    create_button.click()
    time.sleep(wait_time)


# --- Login ---
login(driver, wait, email, password, login_url)

# --- Read data from file ---
with open(menu_list, "r") as file:
    lines = file.read().splitlines()

# --- Counters for summary ---
total_items = 0
success_count = 0
fail_count = 0

# --- Loop through items with line numbers ---
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
        "description": ",".join(parts[4:]).strip() if len(parts) > 4 else None
    }

    try:
        create_menu_item(driver, wait, menu_url, item, wait_time)
        success_count += 1

        # Print detailed info
        print(f"[Line {idx}] Created Menu Item:")
        print(f"   Unit       : {item['unit']}")
        print(f"   Category   : {item['category']}")
        print(f"   Name       : {item['name']}")
        print(f"   Price      : {item['price']}")
        print(f"   Description: {item['description']}")
        print("-" * 50)

    except Exception as e:
        fail_count += 1
        print(f"[Line {idx}] Failed to create item: {item['name']} - Error: {e}")
        print("-" * 50)

# --- Print summary ---
print("\nSummary:")
print(f"Total Items  : {total_items}")
print(f"Created      : {success_count}")
print(f"Failed       : {fail_count}")

driver.quit()
