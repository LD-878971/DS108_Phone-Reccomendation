import pandas as pd
import re
def extract_refresh_rate(raw_value):
    if pd.isna(raw_value):
        return None

    s = str(raw_value).lower().strip()
    
    match = re.search(r'([\d.]+)\s*hz', s)
    return float(match.group(1)) if match else None

def clean_phone_name(raw_name):
    if pd.isna(raw_name):
        return ""

    name = str(raw_name).lower().strip()
    if not name:
        return ""

    # Chuẩn hóa dấu nối và loại bỏ phân đoạn không cần thiết
    name = re.sub(r"[\u2010\u2013\u2014\u2212]", "-", name)
    name = re.sub(r"\s*\|\s*.*$", "", name)
    name = re.sub(r"\bđiện thoại\b", "", name, flags=re.I)
    name = re.sub(r"\b(?:ram|rom)\b", "", name, flags=re.I)

    # Xóa các cụm từ quảng cáo / danh mục không phải model
    patterns_to_delete = [
        r"mới",
        r"chính hãng",
        r"vn/?a",
        r"bản quốc tế",
        r"bản chính hãng",
        r"xách tay",
        r"nhập khẩu",
        r"full ?box",
        r"open ?box",
        r"like ?new",
        r"second ?hand",
        r"trả góp",
        r"giá tốt",
        r"giá rẻ",
        r"hàng chính hãng",
        r"hàng.*",
        r"Exynos",
        r"Snapdragon",
        r"special edition",
        r"edition",
        r'china',
        '2021',
        '2022',
        '2023',
        '2024',
        '2025',
        
    ]
    name = re.sub(r"\b(?:" + "|".join(patterns_to_delete) + r")\b", "", name, flags=re.I)

    # Xóa các thông tin mạng và kết nối không phải tên model
    name = re.sub(r"\b(?:4g|5g|nfc|lte|wifi|bluetooth)\b", "", name, flags=re.I)

    # Xóa dung lượng RAM/ROM/ổ cứng
    name = re.sub(r"\b\d+(?:[\.,]\d+)?\s*(?:gb|tb|mb)\b", "", name, flags=re.I)
    name = re.sub(r"\b\d+\s*[x×]\s*\d+\s*(?:gb|tb|mb)\b", "", name, flags=re.I)
    name = re.sub(r"\b\d+\s*[+\/]\s*\d+\s*(?:gb|tb|mb)\b", "", name, flags=re.I)

    # Loại bỏ ký tự không cần và chuẩn hóa khoảng trắng
    name = re.sub(r"[\[\]\(\)\{\}]", " ", name)
    name = re.sub(r"[^\w\s\-]+", " ", name)
    name = re.sub(r"\s{2,}", " ", name)
    name = re.sub(r"\b-\b", " ", name)
    name = name.strip()

    return name

def clean_price(raw_price):
    if pd.isna(raw_price):
        return None
    s = str(raw_price).lower().strip()
    if re.search(r'liên hệ', s):
        return None
    
    s = re.sub(r'[đ]', '', s)
    s = s.replace('.', '')

    match = re.search(r'(\d+)', s)
    return int(match.group(1)) if match else None

def clean_storage(raw_value):
    if pd.isna(raw_value):
        return None

    s = str(raw_value).lower().strip()
    
    match = re.search(r'([\d.]+)', s)
    if not match:
        return None
    
    value = float(match.group(1))
    
    if 'tb' in s:
        value = value * 1024
    if 'mb' in s:
        value = value / 1024
    
    return value

def clean_metrics(raw_value):
    if pd.isna(raw_value):
        return None

    s = str(raw_value).lower().strip()
    
    match = re.search(r'([\d.]+)', s)
    return float(match.group(1)) if match else None

def clean_chipset(text):
    if not isinstance(text, str):
        return None
    
    _TRASH_VALUES = {
        "",
        "đang cập nhật",
        "mediatek",
        "exynos",
        "snapdragon",
        "bộ xử lý octa-core",
        "asr",
        "asr platform",
        "sc6531e",
        "ums9117",
    }
    _BRAND_PREFIXES = [
        r"qualcomm\s+(sm|sdm|msm|qm)\w+\s+",   # "Qualcomm SM8350 Snapdragon..." -> "Snapdragon..."
        r"qualcomm\s+",
        r"mediatek\s+",
        r"hisilicon\s+",
        r"samsung\s+",
        r"google\s+",
        r"huawei\s+",
        r"spreadtrum\s+",
        r"unisoc\s+",
        r"apple\s+",
        r"chip\s+",                      
    ]

    s = text.strip().lower()
    s = re.sub(r"\bthế\s*hệ\b", "gen", s) #"thế hệ" -> "gen"
    s = re.sub(r"\(.*?\)", "", s) #nội dung trong ()
    s = re.sub(r"(\w)\+", r"\1 plus", s) #từ + -> plus
    s = re.sub(r"[®™°•·]", " ", s) #Ký hiệu đặc biệt -> dấu cách
    s = re.sub(r"\b(sm|sdm|msm|apl)\w+\b", "", s) #(sm8350, sdm845, msm8998, apl0698...)

    for pat in _BRAND_PREFIXES:
        s = re.sub(rf"^{pat}", "", s)

    s = re.sub(r"\b(dành cho|cho|danh cho)\s+galaxy\b.*$", "", s)   # "dành cho Galaxy ..."
    s = re.sub(r"\bfor\s+galaxy\b.*$", "", s)                        # "for Galaxy ..."
    s = re.sub(r"\b\d+\s*nhân\b", "", s)                             # "8 nhân", "6 nhân"
    s = re.sub(r"\bocta[\s-]?core\b", "", s)                         # "octa core", "octa-core"
    s = re.sub(r"\b(mobile\s+)?platform\b", "", s)                   # "Mobile Platform"
    s = re.sub(r"\baccelerated\s+edition\b", "", s)                  # "Accelerated Edition"
    s = re.sub(r"\bflagship\b", "", s)                               # "Flagship"
    s = re.sub(r"\btối\s+đa\s+[\d.,]+\s*ghz\b", "", s)              # "tối đa 2.2GHz"
    s = re.sub(r"\btiến\s*trình\b.*$", "", s)                       # "tiến trình 4nm ..."
    s = re.sub(r"\btăng\s+lên\b.*$", "", s)                         # "tăng lên 42% AI ..."
    s = re.sub(r"\b5g\b", "", s)                                     # "5G"
    s = re.sub(r"\b4g\b", "", s)                                     # "4G"

    s = re.sub(r"\b\d+\s*nm\+?\b", "", s) #"6 nm"
    s = s.replace("-", " ")
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    if s in _TRASH_VALUES or len(s) < 3:
        return None

    return s

def add_chipset_info(df_a, df_c):

    map = {}
    for _, row in df_a.iterrows():
        norm = clean_chipset(row["Chipset"])
        map[norm] = {"antutu_11": row["Antutu_11"], "clock": row["Clock"], "gpu": row["GPU"]}
 
    mapped = df_c["Chipset"].apply(lambda x : map.get(clean_chipset(x)))

    df_out = df_c.copy()
    df_out["antutu_11"] = mapped.apply(lambda x: x["antutu_11"] if x else None)
    df_out["clock"] = mapped.apply(lambda x: x["clock"] if x else None)
    df_out["gpu"] = mapped.apply(lambda x: x["gpu"] if x else None)
 
    return df_out

def extract_camera_info(df):
    def clean_camera(text):
        # "hỗ trợ chụp 24MP hoặc 48MP"
        text = re.sub(r'hỗ trợ chụp.*?(?=\D{3}|$)', '', text, flags=re.IGNORECASE)
        # "(24MP và 48MP)", "(24MP hoặc 48MP)"
        text = re.sub(r'\([\d.]+\s*MP\s*(?:và|hoặc|or)\s*[\d.]+\s*MP\)', '', text, flags=re.IGNORECASE)
        # "hoặc 48MP" còn sót
        text = re.sub(r'(?:hoặc|hoac|hay|or)\s+[\d.]+\s*MP', '', text, flags=re.IGNORECASE)
        return text
    def extract_mp_values(text):
        text = clean_camera(text)
        vals  = re.findall(r'([\d.]+)\s*(?:MP|megapixel)', text, re.IGNORECASE)
        vals += re.findall(r'([\d.]+)M(?=[^a-zA-Z]|$)', text)
        return [float(v) for v in vals if v.count('.') <= 1 and float(v) >= 0.3]
    def extract_aperture(text):
        vals   = re.findall(r'[fƒ]\s*/?\s*([\d.]+)', text, re.IGNORECASE)
        floats = [float(v) for v in vals if v.count('.') <= 1 and 0.5 <= float(v) <= 6.0]
        return min(floats) if floats else None
    def count_cameras(text: str, mps: list):
        if len(mps) >= 2:
            return len(mps)
        m = re.search(r'(\d)\s*camera', text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        return 1 if mps else None
    def extract_rear(text):
        if not isinstance(text, str) or not text.strip():
            return {"rear_count": None, "rear_mp_max": None, "rear_f/": None, "rear_ois": None, "rear_telephoto": None, "rear_wide": None}
        mps      = extract_mp_values(text)
        aperture = extract_aperture(text)
        return {
            "rear_count": count_cameras(text, mps),
            "rear_mp_max": max(mps) if mps else 0,
            "rear_f/": aperture if aperture else 0,
            "rear_ois": int(bool(re.search(r'\bOIS\b', text, re.IGNORECASE))),
            "rear_telephoto": int(bool(re.search(r'tele(?:photo)?|zoom quang|kính tiềm vọng|periscope', text, re.IGNORECASE))),
            "rear_wide": int(bool(re.search(r'siêu rộng|ultra.?wide|góc rộng|wide|superwide', text, re.IGNORECASE))),
    }
    def extract_front(text):
        if not isinstance(text, str) or not text.strip():
            return {"front_mp": None, "front_f/": None}
        mps = extract_mp_values(text)
        aperture = extract_aperture(text)
        return {
            "front_mp": max(mps) if mps else None,
            "front_f/": aperture if aperture else None,
    }
    rear  = df["Rear Camera"].apply(extract_rear).apply(pd.Series)
    front = df["Front Camera"].apply(extract_front).apply(pd.Series)
    df_out = pd.concat([df, rear, front], axis=1)

    return df_out

def add_ram(df_source, df_target):

    def parse_ram_for_rom(mem_internal, rom_str):
        if pd.isna(mem_internal) or pd.isna(rom_str):
            return None
        
        rom_num = re.sub(r'[^0-9]', '', str(rom_str))
        pattern = rf'{rom_num}GB\s+(\d+)GB\s+RAM'
        m = re.search(pattern, str(mem_internal), re.IGNORECASE)
        if m:
            return f"{m.group(1)} GB"
        
        all_rams = re.findall(r'\d+GB\s+(\d+)GB\s+RAM', str(mem_internal), re.IGNORECASE)
        return f"{all_rams[0]} GB" if all_rams else None

    def find_match(norm_name, df_source):
        exact = df_source[df_source['name_clean'] == norm_name]
        if len(exact) > 0:
            return exact.iloc[0]
        
        candidates = df_source[df_source['name_clean'].str.contains(re.escape(norm_name), regex=True)]
        if len(candidates) > 0:
            return candidates.iloc[candidates['name_clean'].str.len().argmin()]
        
        candidates2 = df_source[df_source['name_clean'].apply(lambda x: x in norm_name and len(x) > 5)]
        if len(candidates2) > 0:
            return candidates2.iloc[candidates2['name_clean'].str.len().argmax()]
        
        return None

    df_source = df_source.copy()
    df_target = df_target.copy()

    for idx, row in df_target.iterrows():
        need_ram = pd.isna(row['RAM'])
        if not need_ram:
            continue

        match = find_match(row['Name'], df_source)
        if match is None:
            continue

        if need_ram:
            ram = parse_ram_for_rom(match['Memory | Internal'], row['ROM'])
            if ram:
                df_target.at[idx, 'RAM'] = ram

    return df_target

