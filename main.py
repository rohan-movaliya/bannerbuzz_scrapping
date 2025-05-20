from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import json
import re


# Selenium WebDriver setup
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Open the website
driver.get("https://www.bannerbuzz.com/")
time.sleep(2)

# Locate the main category dropdown
category_dropdown = driver.find_element(By.NAME, "category")
select = Select(category_dropdown)

# Loop through all main categories
for i in range(len(select.options)):
    select = Select(driver.find_element(By.NAME, "category"))
    option = select.options[i]
    category_name = option.text
    print(f"\n🔹 Main Category: [{i+1}] {category_name}")
    
    # Select main category
    select.select_by_index(i)
    time.sleep(1)

    # Get alt data
    category_dropdown = driver.find_element(By.NAME, "category")
    alt_data = category_dropdown.get_attribute("alt")
    
    if not alt_data:
        # print("⚠️ No subcategories found.")
        continue

    try:
        category_data = json.loads(alt_data)
        filename_safe = re.sub(r'[^\w\-_.]', '_', category_data["url"]) + ".json"
        scraped_data = []
        subcategories = category_data.get("subcategory", [])
    except Exception as e:
        # print("❌ Failed to parse subcategories:", e)
        continue
    
    
    product_count = 1

    # Visit subcategories
    for sub in subcategories:
        sub_name = sub["label"]
        sub_url = sub["url"]
        page = 1

        while True:
            paged_url = f"https://www.bannerbuzz.com/{sub_url}?page={page}"
            # print(f"  ↳ Visiting Subcategory: {sub_name} (Page {page}): {paged_url}")
            # print(f"  ↳ {sub_name}")
            driver.get(paged_url)
            time.sleep(2)

            product_boxes = driver.find_elements(By.CLASS_NAME, "cSingleProductBox")
            if not product_boxes:
                # print("    🚫 No more products found.")
                break

            for box in product_boxes:
                try:
                    name = box.find_element(By.XPATH, './/meta[@itemprop="name"]').get_attribute("content")
                    url = box.find_element(By.XPATH, './/meta[@itemprop="url"]').get_attribute("content")
                    scraped_data.append({
                        "id":product_count,
                        "subcategory": sub_name,
                        "product_name": name,
                        "product_url": url
                    })
                    product_count += 1
                except Exception as e:
                    # print("    ⚠️ Skipping product due to error:", e)
                    pass

                page += 1
    
    # After all subcategories of one main category are done
    if scraped_data:
        with open(f"data/{filename_safe}", "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved data to: {filename_safe}")


    # 🔄 Go back to homepage before next main category
    driver.get("https://www.bannerbuzz.com/")
    time.sleep(2)

if driver:
    driver.quit()
