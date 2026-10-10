#!/usr/bin/env python3
"""回放脱敏演示数字：不联网、不动账号。"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def main() -> int:
    priced = json.loads((RAW / "calculate-price.sample.json").read_text(encoding="utf-8"))
    account = json.loads((RAW / "account-points.sample.json").read_text(encoding="utf-8"))

    print("麦省心 · 演示回放（脱敏样例）")
    print("=" * 56)
    print("场景：到店自取 · 本店可用券算价（单位分→元）")
    print()
    for case in priced["cases"]:
        r = case["response"]
        print(f"· {case['name']}")
        print(
            f"  现价 ¥{r['price']/100:.2f} "
            f"（原价 ¥{r['originalPrice']/100:.2f}，已省 ¥{r['discount']/100:.2f}）"
        )
    print()
    print(
        f"积分：可用 {account['availablePoint']} · "
        f"本月将过期 {account['currentMouthExpirePoint']}"
    )
    print()
    print("完整决策链请看 SKILL.md；离线排序：")
    print("  python scripts/coupon_rank.py --demo")
    print("  python scripts/points_guard.py --demo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
