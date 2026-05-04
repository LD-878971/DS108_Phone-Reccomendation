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
    time.sleep(3)

    #click_count = 0
    while True:
        try:
            # Dùng find_elements (trả về danh sách) thay vì find_element. 
            # Nếu không có popup, nó trả về mảng rỗng [], code không bị văng lỗi.
            close_buttons = driver.find_elements(By.CSS_SELECTOR, "button.cancel-button-top")
        
            if len(close_buttons) > 0 and close_buttons[0].is_displayed():
                driver.execute_script("arguments[0].click();", close_buttons[0])
                print("Đã dọn dẹp popup cản đường!")
                time.sleep(1) # Nghỉ 1 giây để hiệu ứng ẩn popup chạy xong
        except Exception:
            pass # Lỗi vặt khi tắt popup thì kệ nó, đi tiếp
    # ----------------------------------
        try:
            #Tìm nút xem thêm trong 2s
            button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Xem thêm')]"))
            )

            #Cuộn đến nút "Xem thêm"
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", button)
            time.sleep(1)

            #Nhấn nút "Xem thêm"
            driver.execute_script("arguments[0].click()", button)
            #click_count += 1
            time.sleep(1)

        #Hết nút "Xem thêm"
        except TimeoutException:
            break

    html_source = driver.page_source #Tất cả html của trang
    #driver.quit() #tắt Chrome
    return html_source

def get_product(html_source):
    soup = BeautifulSoup(html_source, "html.parser") 
    products = []
    
    card_infos = soup.find_all("div", class_ = "cardInfo p-2")
    for card in card_infos:
        link_tag = card.find("a", href = True)
        if not link_tag:
            continue

        Name = link_tag.get("title", "").strip()
        if not Name:
            Name = link_tag.text.strip()

        Link = link_tag['href']

        Price_tag = card.find("p", class_ = lambda c : c and "b1-semibold" in c)
        Price = Price_tag.text.strip() if Price_tag else np.nan

        #Khởi tạo các biến thông số
        products.append({
            "name": Name,
            "price": Price,
            "link": Link
        })
    return products

def get_product_specifications(driver, products):
    for product in products:
        link = product["link"]
        if not link or pd.isna(link):
            continue
        
        full_url = f"https://fptshop.com.vn{link}"
        try:
            driver.get(full_url)
            time.sleep(1)
            #Click nút "Xem tất cả thông số"
            try:
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Xem tất cả thông số')]"))
                )
                driver.execute_script("arguments[0].click()", button)
                time.sleep(1)
            except TimeoutException:
                pass
            soup_spec = BeautifulSoup(driver.page_source, "html.parser")

            product_spec = soup_spec.find_all("div", class_ = lambda c: c and "flex gap-2" in c)

            for spec in product_spec:
                div_spec = spec.find(["div", "span", "p"], class_ = lambda c: c and "w-2/5" in c)
                span_spec = spec.find(["div", "span", "p"], class_ = lambda c: c and ("flex-1" in c or "flex flex-1" in c))

                if div_spec and span_spec:
                    stat = div_spec.text.strip()
                    value = span_spec.text.strip()
                    product[stat] = value

        except Exception as e:
            print(f"Lỗi vào link của {product['name']} : {e}")

    return products

def save_to_csv(data, filename = "fpt.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename)


def main():
    url = "https://fptshop.com.vn/dien-thoai"
    driver = setup_driver()
    html_source = load_full_page(driver, url)
    products = get_product(html_source)
    detailed_products = get_product_specifications(driver, products)
    save_to_csv(detailed_products)
    driver.quit()

if __name__ == "__main__":
    main()

