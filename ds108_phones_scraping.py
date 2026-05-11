from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
import time, random, pickle, pandas as pd
from datetime import datetime
import re

# ================== THAY API KEY CỦA BẠN VÀO ĐÂY ==================
client = ScrapingBeeClient(api_key='TQ5UX1YZBS75GGVS8QWB7TPL37R9R42VI5XMI3GKHOM4PGJG6U9XZLINKPERK06QQBY2PIME2W3MYDC2')   # ←←← THAY VÀO ĐÂY

# ================== CONFIG ==================
BRANDS_CONFIG = {
    # "samsung": 6,
    # "huawei": 6,
    # "xiaomi": 8,
    # "oppo": 6,
    # "honor": 4,
    # "realme": 4,
    # "vivo": 7,
    # "tecno": 3,
    #r"google": 1,
    # "zte": 3,
    #r"oneplus": 2,
    #r"sony": 1,
    #r"nothing": 1,
    #r"infinix": 1,
    #"meizu": 1,
}

BRAND_INFO = {
    "samsung": ("9",   "samsung"),
    "xiaomi":  ("80",  "xiaomi"),
    "huawei":  ("58",  "huawei"),
    "oppo":    ("82",  "oppo"),
    "vivo":    ("98",  "vivo"),
    "realme":  ("118", "realme"),
    "honor":   ("121", "honor"),
    "tecno":   ("120", "tecno"),
    "google":  ("107", "google"),
    "oneplus": ("95",  "oneplus"),
    "sony":    ("7",   "sony"),
    "zte":     ("62",  "zte"),      
    "nothing": ("128", "nothing"),  
    "infinix": ("119", "infinix"),  
    "meizu":   ("74",  "meizu"),    
}

BASE_URL = "https://www.gsmarena.com/"
WANTED_SECTIONS = {"Body", "Display", "Platform", "Memory", "Main Camera", "Selfie camera", "Battery"}

# ================== SAFE GET với ScrapingBee ==================
def safe_get(url: str, retries: int = 6) -> BeautifulSoup | None:
    for attempt in range(retries):
        try:
            response = client.get(
                url,
                params={
                    'render_js': 'false',      
                    'block_resources': 'true',
                    'timeout': 30000,
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Thành công")
                
                time.sleep(random.uniform(7, 13))
                return BeautifulSoup(response.content, "lxml")
            
            elif response.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"🚫 429 → Chờ {wait} giây")
                time.sleep(wait)
            else:
                print(f"⚠️ Status {response.status_code} - Thử lại lần {attempt+1}")
                time.sleep(10)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(12)
    
    print(f"💥 Thất bại sau {retries} lần: {url}")
    return None


# ================== FETCH BRAND PHONES ==================
def fetch_brand_phones(brand_name: str, max_pages: int) -> list:
    brand_id, brand_prefix = BRAND_INFO.get(brand_name.lower(), (None, None))
    if not brand_id:
        print(f"❌ Không tìm thấy brand: {brand_name}")
        return []
    
    phones = []
    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{BASE_URL}{brand_prefix}-phones-{brand_id}.php"
        else:
            url = f"{BASE_URL}{brand_prefix}-phones-f-{brand_id}-0-p{page}.php"
        
        print(f"📄 Đang lấy trang {page}/{max_pages} của {brand_name}")
        soup = safe_get(url)
        if not soup:
            print(f"❌ Không lấy được trang {page}")
            break
            
        items = soup.select("div.makers ul li a")
        for a in items:
            phones.append({
                "brand": brand_name,
                "name": a.get_text(strip=True),
                "slug": a["href"]
            })
        print(f"   ✅ +{len(items)} điện thoại | Tổng: {len(phones)}")
        time.sleep(random.uniform(5, 9))
    return phones


# ================== SCRAPE SPECS ==================
def scrape_specs(slug: str, brand_name: str) -> dict:
    url = BASE_URL + slug
    soup = safe_get(url)
    if not soup:
        return {}
    
    title = soup.find("h1", class_="specs-phone-name-title")
    specs = {
        "brand": brand_name,
        "gsmarena_url": url,
        "name": title.get_text(strip=True) if title else slug,
    }
    
    for table in soup.select("#specs-list table"):
        th = table.find("th")
        if not th or th.get_text(strip=True) not in WANTED_SECTIONS:
            continue
        section = th.get_text(strip=True)
        for row in table.select("tr"):
            key_td = row.find("td", class_="ttl")
            val_td = row.find("td", class_="nfo")
            if key_td and val_td:
                key = key_td.get_text(strip=True)
                val = re.sub(r"[\r\n\t]+", " ", val_td.get_text(" ", strip=True)).strip()
                specs[f"{section} | {key}"] = val
    return specs


# ================== MAIN ==================
def main():
    for BRAND_NAME, MAX_PAGES in BRANDS_CONFIG.items():
        print(f"\n{'='*80}")
        print(f"🚀 BẮT ĐẦU SCRAPE {BRAND_NAME.upper()} - {MAX_PAGES} trang")
        print(f"{'='*80}")
        
        phones = fetch_brand_phones(BRAND_NAME, MAX_PAGES)
        if not phones:
            continue

        progress_file = f"{BRAND_NAME}_progress.pkl"
        try:
            with open(progress_file, "rb") as f:
                data = pickle.load(f)
            all_specs = data["specs"]
            start_i = data["index"]
            print(f"📂 Resume từ phone thứ {start_i}")
        except:
            all_specs, start_i = [], 0

        for i in range(start_i, len(phones)):
            phone = phones[i]
            print(f"[{i+1:3d}/{len(phones)}] {phone['name'][:70]}")
            
            specs = scrape_specs(phone["slug"], BRAND_NAME)
            if specs:
                all_specs.append(specs)

            # Nghỉ dài hơn sau mỗi 25 phones
            if (i + 1) % 25 == 0 and i + 1 < len(phones):
                print("⏸️  Nghỉ 6 phút để tránh bị chặn...")
                time.sleep(360)

            # Checkpoint
            if (i + 1) % 10 == 0:
                with open(progress_file, "wb") as f:
                    pickle.dump({"specs": all_specs, "index": i+1, "phones": phones}, f)

        # Lưu file CSV
        df = pd.DataFrame(all_specs)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{BRAND_NAME}_{len(df)}_phones_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"✅ HOÀN THÀNH {BRAND_NAME.upper()}: {len(df)} phones → {filename}\n")

if __name__ == "__main__":
    main()