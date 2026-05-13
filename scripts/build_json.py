"""
build_json.py - サイト用JSON生成
mosaic.html が読み込む mosaic_DATE.json と
latest.json を生成する
"""
import json
from pathlib import Path
from utils import today_str

TODAY = today_str()

ASSIGNMENTS_JSON = Path(f"data/assignments_{TODAY}.json")
COLLECTED_JSON   = Path(f"data/collected_{TODAY}.json")
MOSAIC_IMG       = Path(f"data/mosaic_{TODAY}.jpg")
OUTPUT_JSON      = Path(f"data/mosaic_{TODAY}.json")
LATEST_JSON      = Path("data/latest.json")

GRID_W     = 40
GRID_H     = 60
TILE_SIZE  = 20


def build():
    # 入力ファイルの確認
    if not ASSIGNMENTS_JSON.exists():
        print(f"エラー: {ASSIGNMENTS_JSON} が見つかりません")
        print("generate_mosaic.py を先に実行してください")
        return False

    if not MOSAIC_IMG.exists():
        print(f"エラー: {MOSAIC_IMG} が見つかりません")
        print("generate_mosaic.py を先に実行してください")
        return False

    with open(ASSIGNMENTS_JSON, encoding="utf-8") as f:
        assignments = json.load(f)

    # 投稿者数をカウント（ニックネームの種類数）
    collected = []
    if COLLECTED_JSON.exists():
        with open(COLLECTED_JSON, encoding="utf-8") as f:
            collected = json.load(f)

    contributors = set(
        c["contributor"] for c in collected
        if c.get("contributor")
    )

    # サイト用JSON生成
    output = {
        "date":                 TODAY,
        "mosaic_image":         f"./data/mosaic_{TODAY}.jpg",
        "grid_w":               GRID_W,
        "grid_h":               GRID_H,
        "tile_size":            TILE_SIZE,
        "total_contributors":   len(contributors),
        "tiles":                assignments
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"サイト用JSON生成: {OUTPUT_JSON}")
    print(f"  タイル数: {len(assignments)}")
    print(f"  投稿者数: {len(contributors)}")

    # latest.json を更新（mosaic.html が毎回これを読む）
    latest = {
        "date":  TODAY,
        "json":  f"data/mosaic_{TODAY}.json",
        "image": f"data/mosaic_{TODAY}.jpg"
    }
    with open(LATEST_JSON, "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=2)
    print(f"latest.json 更新: {LATEST_JSON}")

    return True


if __name__ == "__main__":
    success = build()
    if success:
        print("\n✅ build_json.py 完了")
    else:
        print("\n❌ build_json.py 失敗")
        import sys
        sys.exit(1)
