from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import random
import json

# Options
options = Options()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36')

# Tự động tải chromedriver đúng version
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.thegioididong.com/dtdd")
time.sleep(5)

# Cuộn load more
for _ in range(15):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

products = []
items = soup.select('li.item.__cate_42, li.ajaxed.__cate_42, li.item')

for item in items:
    a = item.select_one('a.main-contain')
    if a and 'href' in a.attrs:
        link = "https://www.thegioididong.com" + a['href']
        name = item.select_one('h3').get_text(strip=True) if item.select_one('h3') else None
        price = item.select_one('strong.price').get_text(strip=True) if item.select_one('strong.price') else None
        if name and price:
            products.append({'name': name, 'price': price, 'link': link})

print(f"Tổng: {len(products)} sản phẩm")

# ========================
# === HÀM LẤY THÔNG SỐ KỸ THUẬT TỪ JSON-LD ===
# ========================

def get_specs_from_detail(driver, url):
    try:
        driver.get(url)
        time.sleep(random.uniform(2, 4))

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Tìm tất cả thẻ script ld+json, không giới hạn id
        script_tags = soup.find_all('script', {'type': 'application/ld+json'})

        print(f"  → Tìm thấy {len(script_tags)} thẻ ld+json")

        data = None
        for tag in script_tags:
            try:
                parsed = json.loads(tag.string)
                # Tìm thẻ nào có additionalProperty hoặc @type là Product
                if 'additionalProperty' in parsed or parsed.get('@type') == 'Product':
                    data = parsed
                    print(f"  → Dùng thẻ @type: {parsed.get('@type')}, id: {tag.get('id')}")
                    break
            except:
                continue

        if not data:
            # Debug: in ra tất cả script tags để xem có gì
            print(f"  → Không tìm thấy Product JSON. Các thẻ script có:")
            for tag in script_tags:
                try:
                    parsed = json.loads(tag.string)
                    print(f"     - @type: {parsed.get('@type')}, id: {tag.get('id')}, keys: {list(parsed.keys())[:5]}")
                except:
                    pass
            return {}

        specs = {}

        # Lấy additionalProperty (danh sách thông số kỹ thuật)
        additional_props = data.get('additionalProperty', [])
        for prop in additional_props:
            name = prop.get('name', '').strip()
            value = prop.get('value', '')
            if name:
                specs[name] = value

        # Thêm các trường cơ bản
        for field in ['name', 'description', 'brand', 'sku', 'mpn']:
            val = data.get(field)
            if val:
                if isinstance(val, dict):
                    specs[field] = val.get('name', str(val))
                else:
                    specs[field] = val

        # Giá
        offers = data.get('offers', {})
        if offers:
            specs['price_json'] = offers.get('price', '')
            specs['currency'] = offers.get('priceCurrency', '')

        print(f"  → Lấy được {len(specs)} thông số")
        return specs

    except json.JSONDecodeError as e:
        print(f"  → Lỗi parse JSON: {e}")
        return {}
    except Exception as e:
        print(f"  → Lỗi crawl {url}: {e}")
        return {}

# ========================
# === CRAWL THÔNG SỐ CHO TỪNG SẢN PHẨM ===
# ========================

# ⚠️ Đổi thành products[:1] để test trước với 1 sản phẩm
#products = products[:1]

full_data = []

print(f"Bắt đầu crawl thông số kỹ thuật cho {len(products)} sản phẩm...")

for idx, product in enumerate(products, 1):
    print(f"[{idx}/{len(products)}] {product['name']}")

    specs = get_specs_from_detail(driver, product['link'])

    row = product.copy()
    row.update(specs)
    full_data.append(row)

    time.sleep(random.uniform(2, 5))

# Lưu file CSV
if full_data:
    df = pd.DataFrame(full_data)
    df.to_csv('tgdd_full.csv', index=False, encoding='utf-8-sig')
    print("\nĐã lưu file: tgdd_full.csv")
    print("Các cột:", list(df.columns))
    print(df.head(1))
else:
    print("Không lấy được dữ liệu chi tiết nào")

driver.quit()