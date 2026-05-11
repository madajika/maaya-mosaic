"""
collect_images.py - 写真収集
GASがpushした data/tiles/DATE/ の写真と
collected_DATE.json を確認して収集リストを整備する
今日分がない場合は過去7日間を遡って最新のデータを使う
"""
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from utils import today_str

TODAY = today_str()
COLLECTED_JSON = Path(f"data/collected_{TODAY}.json")


def find_fallback_collected():
    """今日から遡って最新のcollected_DATE.jsonを探す（最大7日）"""
    jst = timezone(timedelta(hours=9))
    for i in range(1, 8):
        day  = datetime.now(jst) - timedelta(days=i)
        path = Path(f"data/collected_{day.strftime('%Y-%m-%d')}.json")
        if path.exists():
            print(f"{i}日前のデータを使用: {path}")
            return path
    return None


def load_and_validate(json_path: Path) -> list:
    """JSONを読み込み存在するファイルだけ返す"""
    with open(json_path, encoding="utf-8") as f:
        collected = json.load(f)

    valid = []
    for item in collected:
        path = Path(item["image_path"].lstrip("./"))
        if path.exists():
            valid.append(item)
        else:
            print(f"  スキップ（ファイルなし）: {item['image_path']}")

    print(f"  有効: {len(valid)} 件 / 全体: {len(collected)} 件")
    return valid


def collect():
    # 今日のcollected_DATE.jsonがある場合
    if COLLECTED_JSON.exists():
        print(f"今日のデータあり: {COLLECTED_JSON}")
        valid = load_and_validate(COLLECTED_JSON)
        if valid:
            # 重複を除去（同じimage_pathが複数ある場合）
            seen  = set()
            dedup = []
            for item in valid:
                if item["image_path"] not in seen:
                    seen.add(item["image_path"])
                    dedup.append(item)
            if len(dedup) != len(valid):
                print(f"  重複除去: {len(valid)} -> {len(dedup)} 件")
            print(f"収集完了: {len(dedup)} 件")
            return dedup

    # 今日のJSONがない or 有効ファイルが0件 → 過去データで代替
    print(f"今日のデータなし → 過去データを探します")
    fallback = find_fallback_collected()

    if fallback:
        valid = load_and_validate(fallback)
        if valid:
            # 今日付けのJSONとしてコピー保存
            COLLECTED_JSON.parent.mkdir(parents=True, exist_ok=True)
            with open(COLLECTED_JSON, "w", encoding="utf-8") as f:
                json.dump(valid, f, ensure_ascii=False, indent=2)
            print(f"過去データを今日付けで保存: {COLLECTED_JSON}")
            print(f"収集完了: {len(valid)} 件")
            return valid

    # 過去7日間にもデータがない場合
    print("エラー: 使用できる写真データがありません")
    print("Googleフォームから写真を投稿してください")
    return []


if __name__ == "__main__":
    result = collect()
    print(f"\n最終件数: {len(result)} 件")
