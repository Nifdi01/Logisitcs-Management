from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import time


options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=options)

# Open the URL
url = "https://latitude.to/map/az/azerbaijan/cities/by-population/page/1"
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

all_links = []

while True:
    try:
        cities_list = driver.find_elements(By.XPATH, '//div[contains(@class, "b-cities-listing")]/ul//li')
    except NoSuchElementException:
        print("No element with class 'b-cities-listing' found. Exiting.")
        break

    for city in cities_list:
        link = city.find_element(By.XPATH, "./a").get_attribute('href')
        name = city.find_element(By.XPATH, "./a").text
        all_links.append((name, link))

    # Check if there is a next page
    try:
        next_page = driver.find_element(By.XPATH, '//a[@class="next"]')
    except NoSuchElementException:
        print("No element with class 'next' found. Exiting.")
        break

    if 'disabled' in next_page.get_attribute('class'):
        break

    try:
        # Click the next page link using JavaScript
        driver.execute_script("arguments[0].click();", next_page)

        # Wait for a brief moment to allow the page to load
        time.sleep(2)

        # Explicitly wait for the presence of the new cities_list
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "b-cities-listing")]/ul//li')))
    except StaleElementReferenceException:
        print("StaleElementReferenceException occurred. Retrying...")
        time.sleep(2)
    except TimeoutException:
        print("Timed out waiting for the page to load. Exiting.")
        driver.quit()
        exit()

# Process each city link
with open("heuristics.txt", 'w', encoding='utf-8') as output_file:
    for city_name, city_link in all_links:
        try:
            driver.get(city_link)
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='DD']")))
            location = driver.find_element(By.XPATH, "//input[@id='DD']").get_attribute("value")
            time.sleep(3)
            print(f"{city_name} scraped")
            longitude, latitude = location.split()[0], location.split()[1]
            output_file.write(f"{city_name}: ({longitude}, {latitude}),\n")
        except NoSuchElementException as e:
            print(f"Error processing {city_name}: {e}")
        except Exception as e:
            print(f"Unexpected error processing {city_name}: {e}")


output_file.close()

# Close the browser
driver.quit()
