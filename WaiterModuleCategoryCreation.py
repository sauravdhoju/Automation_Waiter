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
category_url = config["category_create_url"]  # e.g., https://cloud.restroorder.com/category/create
category_list = config["category_list"]        # e.g., categories.txt
wait_time = config.get("wait_time", 5)

# --- Initialize browser ---
options = webdriver.ChromeOptions()
if browser.lower() == "brave":
    options.binary_location = browser_path

driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 20)

# --- Login function ---
def login(driver, wait, email, password, login_url):
    driver.get(login_url)
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[text()='Sign In']").click()
    wait.until(EC.url_contains("dashboard"))
    print("Logged in successfully.")

# --- Create category function ---
def create_category(driver, wait, category_name, cost_center):
    driver.get(category_url)
    time.sleep(wait_time)

    # Enter Category Name
    name_input = wait.until(EC.presence_of_element_located((By.NAME, "name")))
    name_input.clear()
    name_input.send_keys(category_name)

    # Select Cost Center (React Select)
    # Click the Cost Center dropdown
    cost_container = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "div[id^='costCenterId'] .css-phxhil-control")
    ))
    cost_container.click()
    time.sleep(0.5)  # Give React time to render the input

    # Find the input inside the dropdown
    cost_input = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div[id^='costCenterId'] input")
    ))

    # Clear any existing text (optional)
    cost_input.clear()
    time.sleep(0.2)

    # Type the cost center slowly
    for ch in cost_center:
        cost_input.send_keys(ch)
        time.sleep(0.05)

    # Wait for the options to appear
    time.sleep(0.5)

    # Press Enter to select the first matching option
    cost_input.send_keys(Keys.ENTER)
    time.sleep(0.5)


    # Click Save
    save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']")))
    save_button.click()
    time.sleep(wait_time)
    print(f"Created Category: {category_name} ({cost_center})")

# --- Login ---
login(driver, wait, email, password, login_url)

# --- Read categories from file ---
with open(category_list, "r") as file:
    lines = file.read().splitlines()

# --- Counters ---
total = 0
success = 0
fail = 0

# --- Loop through each line ---
for idx, line in enumerate(lines, start=1):
    if not line.strip():
        continue

    total += 1
    parts = [x.strip() for x in line.split(",")]
    category_name = parts[0]
    cost_center = parts[1]

    try:
        create_category(driver, wait, category_name, cost_center)
        success += 1
    except Exception as e:
        fail += 1
        print(f"[Line {idx}] Failed to create category '{category_name}' - Error: {e}")

# --- Print summary ---
print("\nSummary:")
print(f"Total Categories : {total}")
print(f"Created          : {success}")
print(f"Failed           : {fail}")

driver.quit()
