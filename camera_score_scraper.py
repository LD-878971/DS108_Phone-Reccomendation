import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def setup_driver():
    options = webdriver.ChromeOptions()

    #options.add_argument("--headless") #chạy ngầm k cần giao diện
    #options.add_argument("--window-size=1920,1080")#kích thước màn hình
    options.page_load_strategy = 'eager' #hạn chế tải hình ảnh, ads trên web

    #Tắt load hình ảnh, CSS, và popup mặc định
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.stylesheets": 2
    }
    options.add_experimental_option("prefs", prefs)

    # Thêm vài đối số giúp Chrome chạy nhẹ hơn trên máy
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options = options) #gọi Chrome để dùng

    return driver

def load_full_page(driver, url):
    driver.get(url)
    time.sleep(2)
    while True:
        try:
            #Tìm nút xem thêm trong 2s
            button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Load more')]"))
            )

            #Cuộn đến nút "Xem thêm"
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", button)
            time.sleep(1)

            #Nhấn nút "Xem thêm"
            driver.execute_script("arguments[0].click()", button)
            time.sleep(1)

        #Hết nút "Xem thêm"
        except TimeoutException:
            break

    html_source = driver.page_source #Tất cả html của trang
    return html_source

def scrape(html_source):
    soup = BeautifulSoup(html_source, "html.parser")
    data = []

    rows = soup.find_all("div", class_ = "row device-row")
    for row in rows:
        name_tag = row.find("span", attrs = {"x-text": "deviceData.name"})
        score_tags = row.find_all("span", attrs={"x-text": lambda x: x and "scoreValueToDisplay" in x})
        if name_tag:
            name = name_tag.text.strip()
            score = None
            for tag in score_tags:
                text = tag.text.strip()
                
                # Bỏ qua các thẻ rỗng
                if text == "":
                    continue
                    
                if tag.has_attr('class') and 'devicePrice' in tag['class']:
                    continue
                    
                if tag.has_attr('class') and 'deviceDate' in tag['class']:
                    continue

                score = text
                break

            data.append({
                "name": name,
                "camera_score": score
            })

    return data

def main():
    url = "https://www.dxomark.com/smartphones/"
    driver = setup_driver()
    html_source = load_full_page(driver, url)

    camera_score = scrape(html_source)

    df = pd.DataFrame(camera_score)
    df.to_csv("camera_score.csv", index = False)

    driver.quit()

if __name__ == "__main__":
    main()
            