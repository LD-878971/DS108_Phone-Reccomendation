import pandas as pd
import numpy as np
import re

#----- CLEANING --------------

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
        r"qualcomm\s+(sm|sdm|msm|qm)\w+\s+",  
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

def advanced_clean_os(text):
    if (
        pd.isna(text)
        or not isinstance(text, str)
        or "cập nhật" in text.lower()
    ):
        return "Android", None

    text = text.strip()
    
    is_android = 1
    os_name = "Android"
    if "ios" in text.lower():
        is_android = 0
        os_name = "iOS"

    os_version = None

    if text.isdigit():
        return os_name, float(text)

    if "nâng cấp" in text.lower():
        upgraded_version = re.findall(r"Android\s*(\d+(?:\.\d+)?)", text)
        if upgraded_version:
            return os_name, float(upgraded_version[-1])

    version_match = re.search(r"(?:Android|iOS)\s*(\d+(?:\.\d+)?)", text, re.I)
    if version_match:
        os_version = float(version_match.group(1))
    else:
        os_version = None

    return os_name, os_version


def clean_battery(raw_value):
    # Bước 0: NaN → None
    if pd.isna(raw_value):
        return None

    s = str(raw_value).strip()

    if 'mah' not in s.lower():
        return None

    s = re.sub(r'(\d{1,2})\.(\d{3})(?=\D|$)', r'\1\2', s)

    s = s.replace(',', '')

    match = re.search(r'([\d.]+)\s*mah', s, re.IGNORECASE)
    return float(match.group(1)) if match else None

def clean_sim_options(text):
    max_nano  = 0
    max_esim  = 0
    max_micro = 0
    max_mini  = 0

    if pd.isna(text) or not isinstance(text, str):
        return max_nano, max_esim, max_micro, max_mini

    text_lower = text.lower()
    options    = re.split(r"hoặc|/|;", text_lower)

    for option in options:
        option = option.strip()
        nano_in_opt = 0
        esim_in_opt = 0

        # eSIM
        if "esim" in option:
            match_esim = re.search(r"(\d+)\s*esim", option)
            if match_esim:
                esim_in_opt = int(match_esim.group(1))
            elif "dual" in option or "kép" in option:
                esim_in_opt = 2
            else:
                esim_in_opt = 1

        # Nano SIM
        if "nano" in option or "sim 1 + sim 2" in option:
            match_nano = re.search(r"(\d+)\s*nano", option)
            if match_nano:
                nano_in_opt = int(match_nano.group(1))
            elif "dual" in option or "kép" in option or "sim 1 + sim 2" in option:
                nano_in_opt = 2
            else:
                nano_in_opt = 1
        elif "2 sim" in option and "nano" in text_lower:
            nano_in_opt = 2

        max_nano = max(max_nano, nano_in_opt)
        max_esim = max(max_esim, esim_in_opt)

        if "micro" in option:
            max_micro = 1
        if "mini" in option:
            max_mini = 1

    return max_nano, max_esim, max_micro, max_mini

#----------- EXTRACTING --------------------

def get_brand(text):    
    brand = text.strip().split()[0]
    
    if 'iphone' in brand:
        return 'apple'
    if 'red' in brand:
        return 'nubia'
    if 'xperia' in brand:
        return 'sony'
    if 'black' in brand or 'xiaomii' in brand:
        return 'xiaomi'
    if 'rog' in brand or 'zenfone' in brand:
        return 'asus'
    if 'camon' in brand:
        return 'tecno'
    
    return brand

def extract_refresh_rate(tan_so_quet, tinh_nang):

    def from_tan_so_quet(val):
        if pd.isna(val):
            return None
        s = str(val).lower().strip()
        match = re.search(r'([\d.]+)\s*hz', s)
        return float(match.group(1)) if match else None

    def from_tinh_nang(val):
        if pd.isna(val):
            return None
        s = str(val).lower().strip()

        noise_patterns = [
            r'(?:touch\s*sampling|lấy mẫu cảm ứng|tốc độ\s*(?:phản hồi|quét)\s*cảm ứng|cảm ứng)\s*[\d.]+\s*hz',
            r'pwm\s*(?:dimming)?\s*[\d.]+\s*hz',
            r'[\d.]+\s*hz\s*pwm',
            r'(?:dimming|giảm nhòe|motion blur)\s*[\d.]+\s*hz',
        ]
        for pat in noise_patterns:
            s = re.sub(pat, '', s)

        rr_context = r'(?:tần số quét|refresh rate|tốc độ làm mới|promotion|adaptive)'
        match = re.search(rf'{rr_context}[^,.\n]{{0,30}}?(\d+)\s*hz', s)
        if match:
            return float(match.group(1))

        range_match = re.search(r'\d+\s*[-–]\s*(\d+)\s*hz', s)
        if range_match:
            freq = float(range_match.group(1))
            if 1 <= freq <= 165:
                return freq

        for m in re.findall(r'([\d.]+)\s*hz', s):
            freq = float(m)
            if 1 <= freq <= 165:
                return freq

        return None

    result = from_tan_so_quet(tan_so_quet)
    if result is None:
        result = from_tinh_nang(tinh_nang)
    return result

def extract_architecture(arch_str):
    if pd.isna(arch_str):
        return None, None, None
 
    clusters = arch_str.split("|")
 
    total_cores = 0
    freqs = []
    min_freq = float("inf")
    max_freq = float("inf")
 
    for cluster in clusters:
        cluster = cluster.strip()
 
        match = re.search(r"(\d+)x\s+([\d.]+)\s*GHz", cluster)
        if not match:
            continue
 
        count = int(match.group(1))
        freq = float(match.group(2))
 
        total_cores += count
        freqs.append((count, freq))
        min_freq = min(min_freq, freq)
 
    if not freqs:
        return None, None, None
    
    max_freq = round(max(f for _, f in freqs), 3)
    min_freq = round(min(f for _, f in freqs), 3) 
    weighted_mean = sum(c * f for c, f in freqs) / total_cores
 
    return total_cores, max_freq, min_freq, round(weighted_mean, 3)


def add_chipset_info(df_a, df_c):

    map = {}
    for _, row in df_a.iterrows():
        norm = clean_chipset(row["Chipset"])
        map[norm] = {"antutu_11": row["Antutu_11"], "clock": row["Clock"], "gpu": row["GPU"], "architecture": row["Architecture"]}
 
    mapped = df_c["Chipset"].apply(lambda x : map.get(clean_chipset(x)))

    df_out = df_c.copy()
    df_out["antutu_11"] = mapped.apply(lambda x: x["antutu_11"] if x else None)
    df_out["clock"] = mapped.apply(lambda x: x["clock"] if x else None)
    df_out["gpu"] = mapped.apply(lambda x: x["gpu"] if x else None)
    df_out["architecture"] = mapped.apply(lambda x: x["architecture"] if x else None)
    
 
    return df_out

def extract_camera_info(df):
    def clean_camera(text):
        text = re.sub(r'hỗ trợ chụp.*?(?=\D{3}|$)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\([\d.]+\s*MP\s*(?:và|hoặc|or)\s*[\d.]+\s*MP\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(?:hoặc|hoac|hay|or)\s+[\d.]+\s*MP', '', text, flags=re.IGNORECASE)
        return text

    def extract_mp_values(text):
        text = clean_camera(text)
        text = re.sub(r'(\d)(\d+\.\d+)', r'\1 \2', text)      
        vals  = re.findall(r'([\d.]+)\s*(?:MP|megapixel)', text, re.IGNORECASE)
        vals += re.findall(r'([\d.]+)M(?=\W|$)', text)

        return [float(v) for v in vals if v.count('.') <= 1 and float(v) >= 0.3]

    def extract_aperture(text):
        vals = re.findall(r'[fƒ]\s*/?\s*(\d+)\s(\d+)(?!\s*\d)', text, re.IGNORECASE)
        floats = [float(f'{a}.{b}') for a, b in vals
                  if 0.5 <= float(f'{a}.{b}') <= 6.0]
        vals2  = re.findall(r'[fƒ]\s*/?\s*([\d.]+)', text, re.IGNORECASE)
        floats += [float(v) for v in vals2 if v.count('.') <= 1 and 0.5 <= float(v) <= 6.0]

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
    return pd.concat([df, rear, front], axis=1)

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

def extract_res_row(text):
    if pd.isna(text) or not isinstance(text, str):
        return None, None

    match = re.search(r"^(\d+)\s*[xX×]\s*(\d+)", text.strip())

    if match:
        return int(match.group(1)), int(match.group(2))

    return None, None

def extract_battery_gsm(text):
    # Kiểm tra nếu dữ liệu bị trống (NaN) hoặc không phải dạng chuỗi
    if pd.isna(text) or not isinstance(text, str):
        return None
    
    # Regex tìm các chữ số liền nhau nằm ngay trước chữ "mAh" (có thể có hoặc không có khoảng trắng)
    # Dấu ? sau .* đảm bảo nó sẽ dừng lại ở cụm 'mAh' ĐẦU TIÊN (Non-greedy matching)
    match = re.search(r'(.*?)(?P<capacity>\d+)\s*mAh', text, re.IGNORECASE)
    
    if match:
        # Trả về giá trị số tìm được dưới dạng số nguyên (int)
        return int(match.group('capacity'))
    
    return None

def extract_hz_gsm(text):
    if not isinstance(text, str):
        return np.nan

    try:
        if "," in text:
            text_after_comma = text.split(",", 1)[1]
        else:
            # Nếu chuỗi không có dấu phẩy, tìm kiếm trên toàn bộ chuỗi
            text_after_comma = text

        match = re.search(r"(\d+\.?\d*)\s*Hz", text_after_comma)

        if match:
            return np.float64(match.group(1))

    except Exception:
        pass

    return np.nan

def remove_first_word_if_iphone(text):
    if not isinstance(text, str):
        return text

    if "iphone" in text.lower():
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            return parts[1]
        
    return text

def get_camera_score(row, camera):
    name = str(row['Name']).strip().lower()
    matches = camera[camera['name'] == name]

    if matches.empty:
        return None

    if len(matches) == 1:
        return matches.iloc[0]['Camera_score']

    chipset = row['Chipset_encoded']
    if pd.isna(chipset):
        return matches.iloc[0]['Camera_score']

    chip_match = matches[matches['chip'] == chipset]
    if not chip_match.empty:
        return chip_match.iloc[0]['Camera_score']
    else:
        return matches.iloc[0]['Camera_score']

def extract_display_type(val):
    v = str(val).lower()

    if 'amoled' in v:
        return 'AMOLED'
    elif 'oled' in v:
        return 'OLED'
    elif 'ips lcd' in v or ('ips' in v and 'lcd' in v):
        return 'IPS LCD'
    elif 'ips' in v:
        return 'IPS'
    elif 'lcd' in v:
        return 'LCD'
    else:
        return 'Other'

def extract_chipset(val):
    v = str(val).lower()

    if 'apple' in v or 'bionic' in v or re.match(r'^a\d+', v):
        return 'Apple'
    elif 'snapdragon' in v or 'qualcomm' in v:
        return 'Snapdragon'
    elif 'dimensity' in v or 'helio' in v or 'mediatek' in v:
        return 'MediaTek'
    elif 'exynos' in v:
        return 'Exynos'
    elif 'kirin' in v:
        return 'Kirin'
    elif 'tensor' in v:
        return 'Google'
    elif 'unisoc' in v or 'tiger' in v or re.match(r'^(sc\d|t\d)', v):
        return 'Unisoc'
    else:
        return 'Other'
    
import re

def extract_chipset_gen(val):
    if not isinstance(val, str):
        return 'Unknown'
    v = val.strip().lower()

    if 'bionic' in v or re.match(r'^a\d+', v):
        m = re.search(r'a(\d+)\s*(pro)?', v)
        if m:
            num = m.group(1)
            tier = ' Pro' if m.group(2) else ''
            return f"A{num}{tier}"
        return 'Unknown'

    elif 'snapdragon' in v:
        m = re.search(r'snapdragon\s+(\d+s?)\s+(elite(?:\s+gen\s+\d+)?)', v)
        if m:
            return f"{m.group(1)} Elite{(' Gen ' + re.search(r'gen\s+(\d+)', m.group(2)).group(1)) if 'gen' in m.group(2) else ''}"

        m = re.search(r'snapdragon\s+(\d+(?:s)?(?:\s+plus)?)\s+gen\s+(\d+)', v)
        if m:
            return f"{m.group(1).title()} Gen {m.group(2)}"

        m = re.search(r'snapdragon\s+(\d+g?(?:\s+plus)?)', v)
        if m:
            return m.group(1).title()

        return 'Unknown'

    elif 'dimensity' in v:
        m = re.search(r'dimensity\s+(\d+\w*(?:\s+(?:ultra|plus))?)', v)
        if m:
            return m.group(1).title()
        return 'Unknown'

    elif 'helio' in v:
        m = re.search(r'helio\s+([a-z]\d+)', v)
        if m:
            return m.group(1).upper()
        return 'Unknown'

    elif 'exynos' in v:
        m = re.search(r'exynos\s+(\d+\w*)', v)
        if m:
            return m.group(1)
        return 'Unknown'

    elif 'kirin' in v:
        m = re.search(r'kirin\s+(\w+)', v)
        if m:
            return m.group(1)
        return 'Unknown'

    elif 'tensor' in v:
        m = re.search(r'tensor\s*(g\d+)?', v)
        if m:
            return ('G1' if not m.group(1) else m.group(1).upper())
        return 'Unknown'

    elif any(x in v for x in ['unisoc', 'tiger', 'sc9', 't606', 't820', 't8300', 't9100']):
        m = re.search(r'([t]\d+|sc\d+\w*)', v)
        if m:
            return m.group(1).upper()
        return 'Unknown'

    return 'Unknown'

def extract_gpu(val):
    val = str(val).lower()
    if 'adreno'     in val: return 'Adreno'
    elif 'mali'     in val: return 'Mali'
    elif 'apple'    in val: return 'Apple GPU'
    elif 'xclipse'  in val: return 'Xclipse'
    elif 'powervr'  in val or 'img' in val: return 'PowerVR'
    elif 'immortalis' in val: return 'Immortalis'
    elif 'maleoon'  in val: return 'Maleoon'
    else: return 'Other'


def extract_gpu_gen(val):
    val = str(val).strip()
    val_lower = val.lower()

    if 'adreno' in val_lower:
        m = re.search(r'(\d{3,})', val)
        return m.group(1) if m else 'Unknown'

    elif 'mali' in val_lower:
        m = re.search(r'[Gg](\d+)', val)
        return f"G{m.group(1)}" if m else 'Unknown'

    elif 'apple' in val_lower:
        m = re.search(r'[Aa](\d+)\s*(Pro|pro)?', val)
        if m:
            chip = f"A{m.group(1)}"
            tier = f" {m.group(2).capitalize()}" if m.group(2) else ""
            return chip + tier
        return 'Unknown'

    elif 'xclipse' in val_lower:
        m = re.search(r'(\d{3,})', val)
        return m.group(1) if m else 'Unknown'

    elif 'powervr' in val_lower or 'img' in val_lower:
        m = re.search(r'([A-Z]{2,}[\w-]+\d+)', val)
        return m.group(1) if m else 'Unknown'

    elif 'maleoon' in val_lower:
        m = re.search(r'(\d+)', val)
        return m.group(1) if m else 'Unknown'

    else:
        return 'Unknown'

#---------- FILLING -----------------

def fill_camera_by_chipset(df):
    rear_num_cols  = ['rear_mp_max', 'rear_f/', 'rear_count']
    rear_bin_cols  = ['rear_wide', 'rear_telephoto', 'rear_ois']
    front_cols     = ['front_mp', 'front_f/']

    all_cols = rear_num_cols + rear_bin_cols + front_cols

    for col in rear_num_cols + front_cols:
        df[col] = df.groupby('Chipset')[col].transform(
            lambda x: x.fillna(x.median())
        )

    for col in rear_bin_cols:
        df[col] = df.groupby('Chipset')[col].transform(
            lambda x: x.fillna(x.mode()[0] if not x.mode().empty else 0)
        )

    # Fallback: còn null thì dùng global median/mode
    for col in rear_num_cols + front_cols:
        df[col] = df[col].fillna(df[col].median())

    for col in rear_bin_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    return df

def fill_iphone_ram(df):
    df = df.copy()

    is_null      = df['RAM'].isna()
    is_iphone    = df['Name'].str.lower().str.contains('iphone', na=False)
    mask         = is_null & is_iphone

    df.loc[mask, 'RAM'] = 8.0
    return df


def fill_ram_by_chipset(df):
    df = df.copy()

    chipset_mode = (
        df.groupby('Chipset')['RAM']
        .agg(lambda x: x.mode().iloc[0] if x.notna().any() else None)
    )

    null_mask = df['RAM'].isna()
    df.loc[null_mask, 'RAM'] = (
        df.loc[null_mask, 'Chipset']
        .map(chipset_mode)
    )
    global_mode = df['RAM'].mode().iloc[0]
    df['RAM'] = df['RAM'].fillna(global_mode)

    # Đảm bảo không còn null
    assert df['RAM'].isna().sum() == 0, "RAM vẫn còn null sau khi fill!"

    return df

def fill_rom_by_chipset(df):
    df = df.copy()

    chipset_median = df.groupby('Chipset')['ROM'].median()  # NaN nếu nhóm toàn null

    null_mask = df['ROM'].isna()
    df.loc[null_mask, 'ROM'] = df.loc[null_mask, 'Chipset'].map(chipset_median)

    global_median = df['ROM'].median()
    df['ROM'] = df['ROM'].fillna(global_median)

    assert df['ROM'].isna().sum() == 0, "ROM vẫn còn null sau khi fill!"
    return df

def fill_iphone_battery(df):
    lookup = {
        'iphone 17'          : 3274,
        'iphone air'         : 2830,   
        'iphone 17e'         : 3279,
        'iphone 16e'         : 3279,
        'iphone 12'          : 2815,
        'iphone 12 mini'     : 2227,
        'iphone 12 pro max'  : 3687,   
        'iphone 12 pro'      : 2815,
    }
    sorted_keys = sorted(lookup, key=len, reverse=True)

    def _fill(row):
        if pd.notna(row['Battery']): 
            return row['Battery']
        name = str(row['Name']).lower().strip()
        for key in sorted_keys:
            if key in name:
                return float(lookup[key])
        return None       

    df = df.copy()
    df['Battery'] = df.apply(_fill, axis=1)
    return df

def fill_battery_by_ram(df):
    df = df.copy()

    ram_median = df.groupby('RAM')['Battery'].median()  # NaN nếu nhóm toàn null

    null_mask = df['Battery'].isna()
    df.loc[null_mask, 'Battery'] = df.loc[null_mask, 'RAM'].map(ram_median)

    global_median = df['Battery'].median()
    df['Battery'] = df['Battery'].fillna(global_median)

    assert df['Battery'].isna().sum() == 0, "Battery vẫn còn null sau khi fill!"
    return df

def fill_screen_size(df):
    df = df.copy()
    
    group_median = df.groupby(['RAM', 'Chipset'])['Screen Size'].median()
    null_mask    = df['Screen Size'].isna()
    df.loc[null_mask, 'Screen Size'] = (
        df.loc[null_mask].set_index(['RAM', 'Chipset']).index.map(group_median)
    )
    
    ram_median = df.groupby('RAM')['Screen Size'].median()
    still_null = df['Screen Size'].isna()
    df.loc[still_null, 'Screen Size'] = df.loc[still_null, 'RAM'].map(ram_median)
    
    # Final fallback
    df['Screen Size'] = df['Screen Size'].fillna(df['Screen Size'].median())
    
    assert df['Screen Size'].isna().sum() == 0
    return df

def fill_ppi(df):
    df = df.copy()

    size_median = df.groupby('Screen Size')['PPI'].median()
    null_mask   = df['PPI'].isna()
    df.loc[null_mask, 'PPI'] = df.loc[null_mask, 'Screen Size'].map(size_median)

    df['PPI'] = df['PPI'].fillna(df['PPI'].median())

    assert df['PPI'].isna().sum() == 0
    return df

def fill_refresh_rate(df):
    df = df.copy()
    
    ram_mode = df.groupby('RAM')['Refresh Rate'].agg(
        lambda x: x.mode().iloc[0] if x.notna().any() else None
    )
    null_mask = df['Refresh Rate'].isna()
    df.loc[null_mask, 'Refresh Rate'] = df.loc[null_mask, 'RAM'].map(ram_mode)
    
    df['Refresh Rate'] = df['Refresh Rate'].fillna(df['Refresh Rate'].mode().iloc[0])
    
    assert df['Refresh Rate'].isna().sum() == 0
    return df

import pandas as pd


def fill_missing_os_by_brand(df, brand_col="Brand", os_col="os_version"):
    df_filled = df.copy()

    def get_mode(series):
        mode_val = series.mode()
        return mode_val.iloc[0] if not mode_val.empty else None

    brand_modes = df_filled.groupby(brand_col)[os_col].transform(get_mode)

    df_filled[os_col] = df_filled[os_col].fillna(brand_modes)

    global_mode = df[os_col].mode()
    if not global_mode.empty:
        df_filled[os_col] = df_filled[os_col].fillna(global_mode.iloc[0])

    return df_filled