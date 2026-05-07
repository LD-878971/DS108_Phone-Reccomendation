import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd

options = webdriver.ChromeOptions()
# options.add_argument("--headless") 
driver = webdriver.Chrome(options=options)

url = "https://cellphones.com.vn/mobile.html"
driver.get(url)
time.sleep(1)

# ========================================================
# 1. VÒNG LẶP CLICK NÚT LIÊN TỤC ĐẾN KHI HẾT
# ========================================================
click_count = 0
while True:
    try:
        close_buttons = driver.find_elements(By.CSS_SELECTOR, "button.cancel-button-top")
        if len(close_buttons) > 0 and close_buttons[0].is_displayed():
            driver.execute_script("arguments[0].click();", close_buttons[0])
            print("Đã dọn dẹp popup cản đường!")
            time.sleep(1)
    except Exception:
        pass

    try:
        button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.button.btn-show-more.button__show-more-product"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", button)
        click_count += 1
        print(f"Đã click nút Xem thêm lần {click_count}... Đang đợi load!")
        time.sleep(1)

    except TimeoutException:
        print("Đã hết nút Xem thêm! Bắt đầu trích xuất HTML...")
        break
    except Exception as e:
        print(f"Dừng click vì lỗi không xác định: {e}")
        break

# ========================================================
# 2. TRÍCH XUẤT TÊN VÀ GIÁ
# ========================================================
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

div_product = soup.find_all("div", class_="product__name")
div_product_price = soup.find_all("div", class_="box-info__box-price")
p_price = [div.find("p", class_="product__price--show") for div in div_product_price]

df = pd.DataFrame({
    "name":  [p.text.strip() for p in div_product],
    "price": [p.text.strip() if p else "N/A" for p in p_price],
})

print(df)
df.to_csv("dien_thoai.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ Đã lưu {len(df)} sản phẩm vào 'dien_thoai.csv'")