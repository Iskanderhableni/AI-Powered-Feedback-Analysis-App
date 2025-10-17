import sys
sys.stdout.reconfigure(encoding='utf-8')
# src/scraper/agoda_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


def scrape_agoda_reviews(url, headless=True, delay=2):
    # Setup Chrome options
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    reviews = set()

    wait = WebDriverWait(driver, 10)

    # Locate pagination container
    pagination_nav = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "nav[data-element-name='review-paginator-step']"))
    )
    ulist = pagination_nav.find_element(By.TAG_NAME, "ul")
    li_items = ulist.find_elements(By.TAG_NAME, "li")

    total_pages = int(li_items[0].get_attribute("aria-setsize"))
    print("Total pages detected:", total_pages)

    for i in range(total_pages):
        # Wait for reviews to be visible
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-selenium='comment']")))

        # Collect reviews
        elements = driver.find_elements(By.CSS_SELECTOR, "[data-selenium='comment']")
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-selenium='comment']")))
        time.sleep(2)



        for el in elements:
            text = el.text.strip()
            if text:
                reviews.add(text)

        print(f"Page {i+1}/{total_pages} - Collected {len(reviews)} reviews")


        # Find next button again
        pagination_nav = driver.find_element(By.CSS_SELECTOR, "nav[data-element-name='review-paginator-step']")
        next_button = pagination_nav.find_element(By.CSS_SELECTOR, "button[data-element-name='review-paginator-next']")

        # Stop if disabled
        if not next_button.is_enabled():
            print("🚫 Last page reached.")
            break

        # Scroll to next button and click
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
    
        
        time.sleep(1)
        driver.execute_script("arguments[0].click();", next_button)


    driver.quit()
    return list(reviews)


if __name__ == "__main__":
    url = "https://www.agoda.com/HOTEL..."
    all_reviews = scrape_agoda_reviews(url, headless=False)

    df = pd.DataFrame(all_reviews, columns=["name","review","rating"])
    df.to_csv("agoda_reviews.csv", index=False, encoding="utf-8-sig")
    print(f"\n🎉 Done! Saved {len(all_reviews)} reviews to agoda_reviews.csv")
