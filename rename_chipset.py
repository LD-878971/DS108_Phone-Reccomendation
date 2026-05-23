import re
import pandas as pd
import difflib

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

def normalize_chipset(text):
    if not isinstance(text, str):
        return ""

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
        return ""

    return s

def map_chipset_info(df_a, df_c) -> pd.DataFrame:

    map = {}
    for _, row in df_a.iterrows():
        norm = normalize_chipset(row["Chipset"])
        map[norm] = {"antutu_11": row["Antutu_11"], "clock": row["Clock"], "gpu": row["GPU"]}
 
    mapped = df_c["Chipset"].apply(lambda x : map.get(normalize_chipset(x)))

    df_out = df_c.copy()
    df_out["antutu_11"] = mapped.apply(lambda x: x["antutu_11"] if x else None)
    df_out["clock"] = mapped.apply(lambda x: x["clock"] if x else None)
    df_out["gpu"] = mapped.apply(lambda x: x["gpu"] if x else None)
 
    return df_out