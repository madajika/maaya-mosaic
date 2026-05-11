"""
generate_mosaic.py - モザイク画像生成
collected_DATE.json の写真を使って
assets/main_photo.jpg のモザイクを生成する
"""
import json
import sys
from pathlib import Path
from PIL import Image
import numpy as np
from utils import today_str, get_avg_color, crop_square

TODAY       = today_str()
INPUT_JSON  = Path(f"data/collected_{TODAY}.json")
OUTPUT_IMG  = Path(f"data/mosaic_{TODAY}.jpg")
OUTPUT_JSON = Path(f"data/assignments_{TODAY}.json")
TARGET_IMG  = Path("assets/main_photo.jpg")

TILE_SIZE   = 40    # タイル1枚のピクセルサイズ
GRID_W      = 30    # 横タイル数
GRID_H      = 40    # 縦タイル数
MIN_TILES   = 10    # 最低必要枚数（不足時は繰り返し使用）


def load_tiles(collected: list) -> list:
    """写真を読み込んでタイルデータを作る"""
    tiles = []
    for item in collected:
        path = Path(item["image_path"].lstrip("./"))
        try:
            img  = Image.open(path).convert("RGB")
            img  = crop_square(img)
            img  = img.resize((TILE_SIZE, TILE_SIZE))
            tiles.append({
                **item,
                "img": img,
                "avg": get_avg_color(img)
            })
        except Exception as e:
            print(f"  スキップ: {path} → {e}")
    return tiles


def generate():
    # 入力ファイルの確認
    if not INPUT_JSON.exists():
        print(f"エラー: {INPUT_JSON} が見つかりません")
        print("collect_images.py を先に実行してください")
        sys.exit(1)

    if not TARGET_IMG.exists():
        print(f"エラー: {TARGET_IMG} が見つかりません")
        print("assets/main_photo.jpg をリポジトリに追加してください")
        sys.exit(1)

    with open(INPUT_JSON, encoding="utf-8") as f:
        collected = json.load(f)

    print(f"入力写真: {len(collected)} 枚")

    if len(collected) == 0:
        print("エラー: 写真が0枚です")
        sys.exit(1)

    # 枚数が足りない場合は繰り返して補う
    if len(collected) < MIN_TILES:
        print(f"写真が少ない（{len(collected)}枚）→ 繰り返して補完")
        while len(collected) < MIN_TILES:
            collected += collected
        collected = collected[:GRID_W * GRID_H]

    # タイルデータ準備
    tiles = load_tiles(collected)
    if not tiles:
        print("エラー: 有効な画像が0枚です")
        sys.exit(1)
    print(f"有効タイル: {len(tiles)} 枚")

    # メイン写真読み込み
    target = Image.open(TARGET_IMG).convert("RGB")
    target = target.resize((GRID_W * TILE_SIZE, GRID_H * TILE_SIZE))
    print(f"メイン写真サイズ: {target.size}")

    # モザイク生成
    result      = Image.new("RGB", (GRID_W * TILE_SIZE, GRID_H * TILE_SIZE))
    assignments = []
    used_count  = {}

    total = GRID_W * GRID_H
    for idx in range(total):
        row = idx // GRID_W
        col = idx % GRID_W
        x   = col * TILE_SIZE
        y   = row * TILE_SIZE

        # メイン写真の該当エリアの平均色
        region_color = np.array(
            target.crop((x, y, x + TILE_SIZE, y + TILE_SIZE))
        ).mean(axis=(0, 1))

        # 色の近さ ＋ 使用回数ペナルティで最適タイルを選ぶ
        best = min(
            tiles,
            key=lambda t: (
                np.linalg.norm(t["avg"] - region_color)
                + used_count.get(t["image_path"], 0) * 8
            )
        )

        used_count[best["image_path"]] = used_count.get(best["image_path"], 0) + 1
        result.paste(best["img"], (x, y))

        assignments.append({
            "row":         row,
            "col":         col,
            "image_path":  best["image_path"],
            "contributor": best["contributor"],
            "x_id":        best.get("x_id", ""),
            "post_url":    best.get("post_url")
        })

        # 進捗表示
        if (idx + 1) % GRID_W == 0:
            print(f"  行 {row + 1}/{GRID_H} 完了")

    # 保存
    OUTPUT_IMG.parent.mkdir(parents=True, exist_ok=True)
    result.save(OUTPUT_IMG, quality=85, optimize=True)
    print(f"\nモザイク画像保存: {OUTPUT_IMG}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(assignments, f, ensure_ascii=False, indent=2)
    print(f"配置情報保存: {OUTPUT_JSON}")

    return assignments


if __name__ == "__main__":
    generate()
