"""
normalize_chipset.py
--------------------
Bước 1: Chuẩn hoá tên chipset để có thể so sánh giữa 2 nguồn dữ liệu.

Vấn đề cần giải quyết
----------------------
Cùng một con chip nhưng tên viết rất khác nhau giữa 2 file:

  antutu_score_socket.csv      cellphones_full.csv
  ─────────────────────────    ────────────────────────────────────────────
  Snapdragon 8 Elite Gen 5  ←→ Snapdragon 8 Elite Gen 5 dành cho Galaxy (3nm)
  A19 Pro                   ←→ Chip A19 Pro
  A16 Bionic                ←→ Apple A16 Bionic 6 nhân
  Dimensity 9500s           ←→ MediaTek Dimensity 9500s
  Exynos 2600               ←→ Exynos 2600 (2nm)
  Snapdragon 8 Elite (Gen 4)←→ Snapdragon 8 Elite dành cho Galaxy (3nm)

Sau khi normalize, các cặp trên cho ra cùng một chuỗi.

Cách dùng
---------
  from normalize_chipset import normalize_chipset

  normalize_chipset("MediaTek Dimensity 9500s")
  # -> "dimensity 9500s"

  normalize_chipset("Snapdragon 8 Elite Gen 5 dành cho Galaxy (3nm)")
  # -> "snapdragon 8 elite gen 5"

  normalize_chipset("Apple A16 Bionic 6 nhân")
  # -> "a16 bionic"
"""

import re


# ── Chuỗi rõ ràng không phải tên chip hợp lệ ────────────────────────────────
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

# ── Prefix thương hiệu cần bỏ ở đầu chuỗi ───────────────────────────────────
# Thứ tự quan trọng: pattern dài hơn / cụ thể hơn đặt trước
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
    r"chip\s+",                              # "Chip A19 Pro" -> "A19 Pro"
]


def normalize_chipset(text: str) -> str:
    """
    Chuẩn hoá tên chipset để so sánh giữa 2 nguồn dữ liệu.

    Các bước xử lý (theo thứ tự):
      1.  Lowercase
      2.  "thế hệ" -> "gen"  (tiếng Việt)
      3.  Bỏ nội dung trong ngoặc: (3nm), (7 nm+), (Quartz)
      4.  Ký hiệu đặc biệt ®™ -> dấu cách
      5.  Bỏ model code Qualcomm đứng độc lập: sm8350, sdm845, msm8998
      6.  Bỏ prefix thương hiệu ở đầu: MediaTek, Qualcomm, Apple, Chip...
      7.  Bỏ suffix marketing: "dành cho Galaxy", "for Galaxy", "Mobile Platform",
          "Accelerated Edition", "Flagship", "tối đa X.XGHz", "X nhân"
      8.  Bỏ process node còn sót: "6 nm", "4nm", "7 nm+"
      9.  Chuẩn hoá dấu gạch ngang: "8400-Ultra" -> "8400 Ultra"
      10. Bỏ ký tự không phải chữ/số/khoảng trắng
      11. Chuẩn hoá khoảng trắng
      12. Trả về "" nếu kết quả là chuỗi rác hoặc quá ngắn

    Parameters
    ----------
    text : tên chipset gốc từ CSV

    Returns
    -------
    str : tên đã chuẩn hoá, hoặc "" nếu không hợp lệ
    """
    if not isinstance(text, str):
        return ""

    s = text.strip()

    # 1. Lowercase
    s = s.lower()

    # 2. Tiếng Việt: "thế hệ" -> "gen"
    s = re.sub(r"\bthế\s*hệ\b", "gen", s)

    # 3. Bỏ nội dung trong ngoặc: (3nm), (7 nm+), (Quartz), (4nm TSMC process)
    s = re.sub(r"\(.*?\)", "", s)

    # 4a. "X+" -> "X plus" trước khi bỏ ký tự đặc biệt: "8+" -> "8 plus"
    s = re.sub(r"(\w)\+", r"\1 plus", s)

    # 4b. Ký hiệu đặc biệt -> dấu cách
    s = re.sub(r"[®™°•·]", " ", s)

    # 5. Bỏ model code Qualcomm đứng độc lập (sm8350, sdm845, msm8998, apl0698...)
    s = re.sub(r"\b(sm|sdm|msm|apl)\w+\b", "", s)

    # 6. Bỏ prefix thương hiệu ở đầu (chỉ bỏ khi ở đầu chuỗi)
    for pat in _BRAND_PREFIXES:
        s = re.sub(rf"^{pat}", "", s)

    # 7. Bỏ suffix noise
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

    # 8. Bỏ process node còn sót ngoài ngoặc: "6 nm", "4nm", "7 nm+"
    s = re.sub(r"\b\d+\s*nm\+?\b", "", s)

    # 9. Chuẩn hoá dấu gạch ngang thành khoảng trắng
    s = s.replace("-", " ")

    # 10. Bỏ ký tự không phải chữ/số/khoảng trắng
    s = re.sub(r"[^\w\s]", " ", s)

    # 11. Chuẩn hoá khoảng trắng
    s = re.sub(r"\s+", " ", s).strip()

    # 12. Loại giá trị rác
    if s in _TRASH_VALUES or len(s) < 3:
        return ""

    return s


# ── Test khi chạy trực tiếp ──────────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        # (antutu,                           cellphones,                                              expect_equal)
        ("Snapdragon 8 Elite Gen 5",         "Snapdragon 8 Elite Gen 5 dành cho Galaxy (3nm)",        True),
        ("A19 Pro",                          "Chip A19 Pro",                                          True),
        ("Dimensity 9500",                   "MediaTek Dimensity 9500s",                              False),
        ("Dimensity 9500s",                  "MediaTek Dimensity 9500s",                              True),
        ("Apple A19",                        "Apple A19",                                             True),
        ("Exynos 2600",                      "Exynos 2600 (2nm)",                                     True),
        ("Snapdragon 8 Elite (Gen 4)",       "Snapdragon 8 Elite dành cho Galaxy (3nm)",              True),
        ("A18 Pro",                          "Apple A18 Pro",                                         True),
        ("Kirin 990 (5G)",                   "HiSilicon Kirin 980 (7 nm)",                            False),
        ("A16 Bionic",                       "Apple A16 Bionic 6 nhân",                               True),
        ("Dimensity 8400",                   "MediaTek Dimensity 8400-Ultra",                         False),
        ("Google Tensor",                    "Google Tensor (5 nm)",                                  True),
        ("Tensor G4",                        "Google Tensor G4 (4 nm)",                               True),
        ("Snapdragon 888 Plus",              "Qualcomm SM8350 Snapdragon 888 5G (5nm)",               False),
        ("Snapdragon 888",                   "Qualcomm SM8350 Snapdragon 888 5G (5nm)",               True),
        ("Apple A9",                         "Apple A19",                                             False),
        ("Tensor G3",                        "Google Tensor G3 tiến trình 4nm",                       True),
        ("Snapdragon 8 Plus Gen 1",          "Snapdragon 8+ Gen 1 (4 nm)",                            True),
        ("Snapdragon 778G Plus",             "Qualcomm Snapdragon ™  778G Plus",                      True),
        ("Exynos 1380",                      "Exynos 1380 (Quartz)",                                  True),
    ]

    passed = 0
    failed = 0
    print(f"\n{'Antutu':<32} {'Cellphones':<52} {'Norm A':<28} {'Norm C':<28} {'OK':>3}")
    print("─" * 148)
    for ant, cel, expected in test_cases:
        na = normalize_chipset(ant)
        nc = normalize_chipset(cel)
        same = (na == nc)
        ok = (same == expected)
        status = "✓" if ok else "✗  <── FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"{ant:<32} {cel:<52} {na:<28} {nc:<28} {status}")

    print(f"\nKết quả: {passed}/{len(test_cases)} test pass", "✓" if failed == 0 else f"— {failed} FAIL")