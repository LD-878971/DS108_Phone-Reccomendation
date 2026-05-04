import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException # Thêm thư viện bắt lỗi Timeout

# Headers bắt buộc để chui vào hàng trăm link con không bị khóa IP
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Mở trình duyệt Chrome
options = webdriver.ChromeOptions()
# options.add_argument("--headless") 
driver = webdriver.Chrome(options=options)

url = "https://cellphones.com.vn/mobile.html"
driver.get(url)
time.sleep(1) # Đợi trang chủ load xong

# ========================================================
# 1. VÒNG LẶP CLICK NÚT LIÊN TỤC ĐẾN KHI HẾT
# ========================================================
click_count = 0
while True:
    # --- THÊM ĐOẠN NÀY ĐỂ TRỊ POPUP ---
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
        # Tìm nút Xem thêm
        button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.button.btn-show-more.button__show-more-product"))    
        )
        
        # Cuộn màn hình xuống ngay cái nút đó
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(1)
        
        # Click nút
        driver.execute_script("arguments[0].click();", button)
        click_count += 1
        print(f"Đã click nút Xem thêm lần {click_count}... Đang đợi load!")
        
        # Nghỉ cho máy chủ CellphoneS nhả data mới về
        time.sleep(1) 
        
    except TimeoutException:
        #print("Đã hết nút Xem thêm! Bắt đầu trích xuất HTML...")
        break
    except Exception as e:
        print(f"Dừng click vì lỗi không xác định: {e}")
        break

soup = BeautifulSoup(driver.page_source, "html.parser")

div_product = soup.find_all("div", class_="product__name")
#for product in div_product:
#    print(product.get_text())

div_product_price = soup.find_all("div", class_="box-info__box-price")
p_price = [product_price.find("p", class_="product__price--show") for product_price in div_product_price]
#for price in p_price:
#    print(price.text.strip())

div_product_info = soup.find_all("div", class_="product-info")
a_product_info = [a_product.find("a") for a_product in div_product_info]
product_href = [href["href"] for href in a_product_info]
#print(product_href)

screen_size = []
screen_tech = []
ram = []
rom = []
battery = []
chipset = []
fps = []

for product_link in product_href:
    time.sleep(1)
    request_product = requests.get(product_link)
    soup_product = BeautifulSoup(request_product.content, "html.parser")
    technical_content_item = soup_product.find_all("tr", class_="technical-content-item")
    done = 0 
    
    screen_size_=np.nan
    screen_tech_=np.nan
    ram_=np.nan
    rom_=np.nan
    battery_=np.nan
    chipset_=np.nan
    fps_ = np.nan

    for item in technical_content_item:
        td_item = item.find_all("td")
        if td_item[0].text.strip() == "Kích thước màn hình":
            screen_size_ = td_item[1].text.strip()
        if td_item[0].text.strip() == "Công nghệ màn hình":
            screen_tech_ = td_item[1].text.strip()
        if td_item[0].text.strip() == "Chipset":
            chipset_ = td_item[1].text.strip()
        if td_item[0].text.strip() == "Dung lượng ram":
            ram_ = td_item[1].text.strip()
        if td_item[0].text.strip() == "Bộ nhớ trong":
            rom_ = td_item[1].text.strip()
        if td_item[0].text.strip() == "Pin":
            battery_ = td_item[1].text.strip()
    screen_size.append(screen_size_)
    screen_tech.append(screen_tech_)
    ram.append(ram_)
    rom.append(rom_)
    battery.append(battery_)
    chipset.append(chipset_)

csv = {
    "name" : [product.text for product in div_product],
    "price" : [price.text.strip() for price in p_price],
    "link" : product_href,
    "screen_size": screen_size,
    "screen_tech": screen_tech,
    "RAM": ram,
    "ROM": rom,
    "Battery": battery,
    "Chipset": chipset,
}

csv_frame = pd.DataFrame(csv)
csv_frame.to_csv("all.csv")