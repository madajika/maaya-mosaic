"""
collect_images.py - 写真収集
GASがpushした data/tiles/DATE/ の写真と
collected_DATE.json を確認して収集リストを整備する
"""
import json
from pathlib import Path
from utils import today_str

TODAY          = today_str()
TILES_DIR      = Path(f"data/tiles/{TODAY}")
COLLECTED_JSON = Path(f"data/collected_{TODAY}.json")


def collect():
    # GASがすでにcollected_DATE.jsonを作っている場合はそのまま使う
    if COLLECTED_JSON.exists():
        with open(COLLECTED_JSON, encoding="utf-8") as f:
            collected = json.load(f)
        print(f"collected_{TODAY}.json を読み込み: {len(collected)} 件")

        # image_path が実際に存在するか確認してフィルタ
        valid = []
        for item in collected:
            path = Path("..") / item["image_path"].lstrip("./")
            if path.exists():
                valid.append(item)
            else:
                print(f"  スキップ（ファイルなし）: {item['image_path']}")

        if len(valid) != len(collected):
            print(f"  有効: {len(valid)} 件 / 全体: {len(collected)} 件")
            # 有効なもので上書き保存
            with open(COLLECTED_JSON, "w", encoding="utf-8") as f:
                json.dump(valid, f, ensure_ascii=False, indent=2)

        print(f"収集完了: {len(valid)} 件")
        return valid

    # collected_DATE.json がない場合は tiles フォルダから直接拾う（フォールバック）
    print(f"collected_{TODAY}.json なし → {TILES_DIR} から直接収集")

    if not TILES_DIR.exists():
        print(f"エラー: {TILES_DIR} が存在しません")
        print("GASでフォーム投稿が行われていないか、日付がずれている可能性があります")
        return []

    collected = []
    for img_path in sorted(TILES_DIR.glob("*")):
        if img_path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            continue
        # ファイル名からニックネームを復元（safeName_index.ext の形式）
        stem  = img_path.stem                        # 例: テストファン_0
        parts = stem.rsplit("_", 1)
        name  = parts[0].replace("_", " ").strip() if len(parts) == 2 else stem

        collected.append({
            "image_path":  f"./{img_path}",
            "contributor": name if name else "匿名ファン",
            "x_id":        "",
            "post_url":    None,
            "source":      "form"
        })

    print(f"フォルダから収集: {len(collected)} 件")

    # 今後のために保存
    COLLECTED_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(COLLECTED_JSON, "w", encoding="utf-8") as f:
        json.dump(collected, f, ensure_ascii=False, indent=2)

    return collected


if __name__ == "__main__":
    result = collect()
    print(f"\n最終件数: {len(result)} 件")
