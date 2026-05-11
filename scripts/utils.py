"""
utils.py - 共通関数
"""
from pathlib import Path


def get_avg_color(img):
    """PIL Imageの平均色をnumpy配列で返す"""
    import numpy as np
    return np.array(img.convert("RGB").resize((8, 8))).mean(axis=(0, 1))


def crop_square(img):
    """画像を中央で正方形にクロップする"""
    w, h = img.size
    size = min(w, h)
    left = (w - size) // 2
    top  = (h - size) // 2
    return img.crop((left, top, left + size, top + size))


def today_str():
    """今日の日付文字列を返す（JST）"""
    from datetime import datetime, timezone, timedelta
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).strftime("%Y-%m-%d")
