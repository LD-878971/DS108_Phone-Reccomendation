import re
import pandas as pd

def clean_phone_name(raw_name: str) -> str:
    if not raw_name:
        return ""

    name = raw_name.strip()
    if not name:
        return ""

    # Chuẩn hóa dấu nối và loại bỏ phân đoạn không cần thiết
    name = re.sub(r"[\u2010\u2013\u2014\u2212]", "-", name)
    name = re.sub(r"\s*\|\s*.*$", "", name)
    name = re.sub(r"\bđiện thoại\b", "", name, flags=re.I)
    name = re.sub(r"\b(?:ram|rom)\b", "", name, flags=re.I)

    # Xóa các cụm từ quảng cáo / danh mục không phải model
    marketing_terms = [
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
        r"hàng.*"
    ]
    name = re.sub(r"\b(?:" + "|".join(marketing_terms) + r")\b", "", name, flags=re.I)

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


if __name__ == "__main__":
    df_cleaned = pd.read_csv('cleaned.csv')
    df_antutu_cleaned = pd.read_csv('antutu_cleaned.csv')

    print("Một số tên từ cleaned.csv (từ cellphones_raw):")
    for i, name in enumerate(df_cleaned['name'].head(15)):
        print(f"{i+1:2d}: {name!r}")

    print("\nMột số tên từ antutu_cleaned.csv:")
    for i, name in enumerate(df_antutu_cleaned['name'].head(15)):
        print(f"{i+1:2d}: {name!r}")

    # Kiểm tra số lượng khớp
    matched = df_cleaned['name'].isin(df_antutu_cleaned['name'])
    print(f"\nKhớp: {matched.sum()}/{len(df_cleaned)}")