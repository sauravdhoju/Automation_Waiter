from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time



# --- Brave Browser setup ---
options = webdriver.ChromeOptions()
options.binary_location = "/usr/bin/brave-browser"
driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 20)

email = "info@chillmrp.com"
passw = "Chillmrp@123#"

# --- Login ---
driver.get("https://waitermoduleapp.danfesolution.com/login")
wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(email)
driver.find_element(By.NAME, "password").send_keys(passw)
driver.find_element(By.XPATH, "//button[text()='Sign In']").click()

# --- Open Menu Item Create Page ---
wait.until(EC.url_contains("dashboard"))
driver.get("https://waitermoduleapp.danfesolution.com/menu-item/create")
time.sleep(5)  # Wait for page & React Select to initialize

# --- Read data from text file ---
with open("menu_list.txt", "r") as file:
    lines = file.read().splitlines()

# --- Loop over data ---
# for line in lines:
#     if not line.strip():
#         continue

#     unit, category, name, price = [x.strip() for x in line.split(",")]
#     print(f"Processing: Name={name}, Category={category}, Unit={unit}, Price={price}")

#     # --- Open Menu Item Create Page fresh each iteration ---
#     driver.get("https://waitermoduleapp.danfesolution.com/menu-item/create")
#     time.sleep(5)  # Wait for page & React Select to initialize

#     # --- Fill 'Name' ---
#     name_input = wait.until(EC.presence_of_element_located((By.NAME, "name")))
#     name_input.clear()
#     name_input.send_keys(name)

#     # --- Fill 'Price' ---
#     price_input = wait.until(EC.presence_of_element_located((By.NAME, "price")))
#     price_input.send_keys(Keys.BACKSPACE)
#     price_input.send_keys(price)

#     # --- Select 'Category' ---
#     category_container = wait.until(EC.element_to_be_clickable(
#         (By.CSS_SELECTOR, "div[id^='categoryId'] .css-phxhil-control")
#     ))
#     category_container.click()
#     category_input = wait.until(EC.presence_of_element_located(
#         (By.CSS_SELECTOR, "div[id^='categoryId'] input")
#     ))
#     category_input.send_keys(category)
#     category_input.send_keys(Keys.ENTER)

#     # --- Select 'Unit' dynamically ---
#     # Find any div whose id starts with 'unit' for the dropdown
#     unit_container = wait.until(EC.element_to_be_clickable(
#         (By.CSS_SELECTOR, "div[id^='unit'] .css-phxhil-control")
#     ))
#     unit_container.click()
#     unit_input = wait.until(EC.presence_of_element_located(
#         (By.CSS_SELECTOR, "div[id^='unit'] input")
#     ))
#     unit_input.send_keys(unit)
#     unit_input.send_keys(Keys.ENTER)

#     # --- Click 'Create' button ---
#     create_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Create']")))
#     create_button.click()

#     print(f"Created: {name}")
#     time.sleep(2)


# --- Loop over data ---
for line in lines:
    if not line.strip():
        continue

    # --- Split fields (last part is description if present, even with commas) ---
    parts = [x.strip() for x in line.split(",")]
    unit, category, name, price = parts[:4]
    description = ",".join(parts[4:]).strip() if len(parts) > 4 else None

    print(f"Processing: Name={name}, Category={category}, Unit={unit}, Price={price}, Description={description}")

    # --- Open Menu Item Create Page fresh each iteration ---
    driver.get("https://waitermoduleapp.danfesolution.com/menu-item/create")
    time.sleep(5)  # Wait for page & React Select to initialize

    # --- Fill 'Name' ---
    name_input = wait.until(EC.presence_of_element_located((By.NAME, "name")))
    name_input.clear()
    name_input.send_keys(name)

    # --- Fill 'Price' ---
    price_input = wait.until(EC.presence_of_element_located((By.NAME, "price")))
    price_input.send_keys(Keys.BACKSPACE)
    price_input.send_keys(price)

    # --- Fill 'Description' (only if provided) ---
    if description:
        desc_input = wait.until(EC.presence_of_element_located((By.ID, "description")))
        desc_input.clear()
        desc_input.send_keys(description)

    # --- Select 'Category' ---
    category_container = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "div[id^='categoryId'] .css-phxhil-control")
    ))
    category_container.click()
    category_input = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div[id^='categoryId'] input")
    ))
    category_input.send_keys(category)
    category_input.send_keys(Keys.ENTER)

    # --- Select 'Unit' dynamically ---
    unit_container = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "div[id^='unit'] .css-phxhil-control")
    ))
    unit_container.click()
    unit_input = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div[id^='unit'] input")
    ))
    unit_input.send_keys(unit)
    unit_input.send_keys(Keys.ENTER)

    # --- Click 'Create' button ---
    create_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Create']")))
    create_button.click()

    print(f"Created: {name}")
    time.sleep(2)

driver.quit()
