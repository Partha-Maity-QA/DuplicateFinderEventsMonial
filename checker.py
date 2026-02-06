from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_duplicate_search(driver, duplicates):
    print("\nTesting duplicates by search...")
    
    for name in duplicates.keys():  # Test all duplicates
        try:
            # Find search input and enter duplicate name
            search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Search by business name...']")
            search_input.clear()
            search_input.send_keys(name)
            
            # Click search button
            search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()
            
            time.sleep(2)
            
            # Count results
            results = driver.find_elements(By.CSS_SELECTOR, "div.bg-white.rounded-lg.border h3 span")
            result_count = len([r for r in results if name.lower() in r.text.lower()])
            
            print(f"  Search '{name}': Found {result_count} results")
            
            # Clear search to return to full listing
            search_input.clear()
            search_button.click()
            time.sleep(2)
            
        except Exception as e:
            print(f"  Error testing '{name}': {str(e)}")

def scrape_photography_vendors():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)
    
    try:
        driver.get("https://dev.eventsmonial.com/event-vendors/photography?view=Grid")
        
        all_vendors = []
        page_num = 1
        
        while True:
            print(f"Scraping page {page_num}...")
            
            # Wait for profile cards to load
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.bg-white.rounded-lg.border")))
            time.sleep(2)
            
            # Extract vendor names from current page
            vendor_cards = driver.find_elements(By.CSS_SELECTOR, "div.bg-white.rounded-lg.border")
            
            for card in vendor_cards:
                try:
                    name_element = card.find_element(By.CSS_SELECTOR, "h3 span")
                    vendor_name = name_element.text.strip()
                    if vendor_name:
                        all_vendors.append(vendor_name)
                except NoSuchElementException:
                    continue
            
            print(f"Found {len(vendor_cards)} vendors on page {page_num}")
            
            # Check for next button (right arrow button that's not disabled)
            try:
                pagination_buttons = driver.find_elements(By.CSS_SELECTOR, "div.flex.items-center.justify-center.gap-1 > button")
                next_button = pagination_buttons[-1] if len(pagination_buttons) > 0 else None
                
                if next_button and "cursor-not-allowed" not in next_button.get_attribute("class"):
                    driver.execute_script("arguments[0].click();", next_button)
                    page_num += 1
                    time.sleep(3)
                else:
                    print("No more pages available")
                    break
            except (NoSuchElementException, IndexError):
                print("No more pages available")
                break
        
        # Find duplicates
        vendor_counts = {}
        for vendor in all_vendors:
            vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
        
        duplicates = {name: count for name, count in vendor_counts.items() if count > 1}
        
        print(f"\nTotal vendors found: {len(all_vendors)}")
        print(f"Unique vendors: {len(vendor_counts)}")
        
        if duplicates:
            print(f"\nDuplicate vendors found ({len(duplicates)}):")
            for name, count in duplicates.items():
                print(f"  {name}: {count} times")
            
            # Test duplicates by searching
            test_duplicate_search(driver, duplicates)
            return all_vendors, duplicates
        else:
            print("\nNo duplicate vendors found")
            
        return all_vendors, duplicates
        
    finally:
        driver.quit()

if __name__ == "__main__":
    vendors, duplicates = scrape_photography_vendors()