import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time 
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def setup_driver():
    options = uc.ChromeOptions()
    # options.add_argument("--headless=new") 
    
    options.add_argument("--window-size=1366,768")
        
    driver = uc.Chrome(options=options, version_main = 147)
    return driver

def scrape(driver, url):
    driver.get(url)
    data = []

    while True:
        time.sleep(1)

        html_src = driver.page_source
        soup = BeautifulSoup(html_src, "html.parser")

        rows = soup.find_all("tr")

        # for row in rows:
        #     cols = row.find_all("td")
        #     if len(cols) >= 3:
        #         name = cols[1].text.strip()
        #         score = cols[2].text.strip()
        for row in rows:
            td = row.find_all("td")
            if len(td) >= 7:
                name = td[1].find('a').text.strip()
                score = td[3].text.strip()
                clock = td[6].text.strip()
                gpu = td[7].text.strip()

                data.append({
                    "Chipset": name,
                    "Antutu 11": score,
                    "Clock": clock,
                    "GPU": gpu
                })

        try:
            next_button = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Next')]"))
            )

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", next_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click()", next_button)

        except TimeoutException:
            break

    return data

def main():
    url = "https://nanoreview.net/en/soc-list/rating"
    driver = setup_driver()

    antutu_score = scrape(driver, url)

    df = pd.DataFrame(antutu_score)
    df.to_csv("antutu_score_socket.csv", index = False)

    driver.quit()

if __name__ == "__main__":
    main()


