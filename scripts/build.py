"""やぎシミュの character.json から index.html を作る。

使い方: python3 scripts/build.py
  data/character.json を読み、template.html の __DATA__ を置き換えて index.html を書き出す。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (キー, 見出し, グループ)
COLUMNS = [
    ("attack", "攻撃", "基本"),
    ("defense", "防御", "基本"),
    ("physical", "体力", "基本"),
    ("speed", "移動速度", "基本"),
    ("range", "通常射程(m)", "通常攻撃"),
    ("motion", "通常倍率", "通常攻撃"),
    ("ulttime", "HS時間(秒)", "ヒーロースキル"),
    ("ultdamage", "HS倍率", "ヒーロースキル"),
    ("ultinvincible", "HS無敵(秒)", "ヒーロースキル"),
    ("ultrange", "HS射程", "ヒーロースキル"),
    ("ultsize", "HS範囲", "ヒーロースキル"),
    ("hadamage", "HA倍率", "ヒーローアクション"),
    ("hastart", "HA発生", "ヒーローアクション"),
    ("hastop", "HA硬直", "ヒーローアクション"),
    ("harange", "HA射程", "ヒーローアクション"),
    ("hasize", "HA範囲", "ヒーローアクション"),
    ("sh", "近 発生", "攻撃カード"),
    ("ss", "近 硬直", "攻撃カード"),
    ("ch", "周 発生", "攻撃カード"),
    ("cs", "周 硬直", "攻撃カード"),
    ("lh", "遠 初弾", "攻撃カード"),
    ("ll", "遠 全弾", "攻撃カード"),
    ("ls", "遠 硬直", "攻撃カード"),
    ("bh", "連 初弾", "攻撃カード"),
    ("bl", "連 全弾", "攻撃カード"),
    ("bs", "連 硬直", "攻撃カード"),
    ("th", "tel 発生", "攻撃カード"),
    ("ts", "tel 硬直", "攻撃カード"),
    ("sskill", "無 発生", "発動カード"),
    ("sskills", "無 硬直", "発動カード"),
    ("mskill", "短 発生", "発動カード"),
    ("mskills", "短 硬直", "発動カード"),
    ("lskill", "長 発生", "発動カード"),
    ("lskills", "長 硬直", "発動カード"),
    ("push", "プッシュ", "ふっとばし"),
    ("lanch", "ランチ", "ふっとばし"),
    ("blast", "ブラスト", "ふっとばし"),
    ("abt_mag", "アビ倍率", "アビリティ"),
    ("abt_ct", "アビCT", "アビリティ"),
]

EXCLUDE = {"やぎなまず"}

ROLE = {"atk": "アタッカー", "gun": "ガンナー", "spr": "スプリンター", "tnk": "タンク"}


def to_num(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def build():
    chars = json.loads((ROOT / "data/character.json").read_text(encoding="utf-8"))
    # ネタ枠のキャラは載せない
    chars = [c for c in chars if c["name"] not in EXCLUDE]
    chars.sort(key=lambda c: c["num"])
    rows = []
    for c in chars:
        vals = []
        for key, _, _ in COLUMNS:
            raw = c.get(key)
            if key == "ultinvincible":
                nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", str(raw))]
                text = "/".join(f"{n:g}" for n in nums)
                vals.append([max(nums) if nums else None, text if len(nums) > 1 else None])
                continue
            if key == "range":
                m = re.match(r"\s*(\d+(?:\.\d+)?)", str(raw))
                vals.append(float(m.group(1)) if m else None)
                continue
            vals.append(to_num(raw))
        rows.append({
            "n": c["num"],
            "name": c["name"],
            "role": c["role"],
            "extra": c.get("rankflag") == 0,
            "v": vals,
        })
    payload = {
        "columns": [{"key": k, "label": l, "group": g} for k, l, g in COLUMNS],
        "roles": ROLE,
        "rows": rows,
    }
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    (ROOT / "index.html").write_text(tpl.replace("__DATA__", data), encoding="utf-8")
    print(f"{len(rows)} キャラ / {len(COLUMNS)} 項目 -> index.html")


if __name__ == "__main__":
    build()
