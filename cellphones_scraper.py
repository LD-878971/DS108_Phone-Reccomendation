import requests
from bs4 import BeautifulSoup
import pandas as pd
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

    driver = webdriver.Chrome(options = options) #gọi Chrome

    return driver

def load_full_page(driver, url):
    driver.get(url)
    time.sleep(2)

    while True:
        #tắt pop-up quảng cáo, v.v...
        try:
            close_buttons = driver.find_elements(By.CSS_SELECTOR, "button.cancel-button-top")
        
            if len(close_buttons) > 0 and close_buttons[0].is_displayed():
                driver.execute_script("arguments[0].click();", close_buttons[0])
                print("Đã tắt pop-up!")
                time.sleep(1)
        except Exception:
            pass

        #Load more
        try:
            button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.button.btn-show-more.button__show-more-product"))    
            )
        
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(0.5)
            
            driver.execute_script("arguments[0].click();", button)
            time.sleep(0.5)
        except TimeoutException:
            break

    html_source = driver.page_source
    return html_source

def get_products(html_src):
    soup = BeautifulSoup(html_src, "html.parser")
    products = []

    product_containers = soup.find_all("div", class_ = "product-info")

    for container in product_containers:
        name_tag = container.find("div", class_ = "product__name")
        price_tag = container.find("p", class_ = "product__price--show")

        h3_name = name_tag.find("h3")
        name = h3_name.text.strip() 
        price = price_tag.text.strip() if (price_tag.text.strip() and "liên hệ" not in price_tag.text.strip().lower()) else None

        link_tag = container.find("a")
        link = link_tag["href"]
        
        products.append({
            "Name": name,
            "Price": price,
            "Link": link
        })

    return products

def get_product_spec(driver, products): 
    count = 0    
    for product in products:
        link = product['Link'] 
        try:
            driver.get(link)
            time.sleep(1)
            try:
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Xem tất cả')]"))
                )
                driver.execute_script("arguments[0].click()", button)
                time.sleep(1)
            except TimeoutException:
                pass

            soup_spec = BeautifulSoup(driver.page_source, "html.parser")

            spec_container = soup_spec.find_all("tr", class_ = "technical-content-item")
            for spec in spec_container:
                td = spec.find_all("td")
                td_text = td[0].get_text(strip = True)
                td_spec = td[1].get_text(strip = True)
                product[td_text] = td_spec
            
            count = count + 1
            print(f"Da crawl {count}!")
        except Exception as e:
            print(e)
        
    return products

def save_to_csv(data, name):
    df = pd.DataFrame(data)
    df.to_csv(f"{name}.csv")

def main():
    url = "https://cellphones.com.vn/mobile.html"
    driver = setup_driver()
    # html_src = load_full_page(driver, url)
    # products = get_products(html_src)
    products = pd.read_csv(r'cellphones_raw.csv')
    products = products.to_dict('records')
    detail_products = get_product_spec(driver, products)
    driver.quit()

    save_to_csv(detail_products, "cellphones_raw")

if __name__ == "__main__":
    main()


