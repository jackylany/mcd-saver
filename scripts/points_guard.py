#!/usr/bin/env python3
"""麦省心 · 积分到期守护（零第三方依赖，可离线跑）。

根据将过期积分，从积分商城候选里挑「门槛低、可兑、仍在期内」的建议。
不发起真实兑换；只输出待确认参数。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def parse_dt(s: str) -> datetime | None:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def recommend(account: dict, products: list, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now()
    available = float(account.get("availablePoint") or 0)
    expiring = float(account.get("currentMouthExpirePoint") or 0)

    scored = []
    for p in products:
        point = float(p.get("point") or 0)
        shop_id = int(p.get("shopId") or 0)
        status = int(p.get("status") or 0)
        down = parse_dt(str(p.get("downTime") or ""))
        up = parse_dt(str(p.get("upTime") or ""))

        if shop_id != 2:
            continue
        if status != 2:  # 2=上架
            continue
        if point <= 0 or point > available:
            continue
        if up and now < up:
            continue
        if down and now > down:
            continue

        # 过期守护：优先「门槛 ≤ 将过期额度」的低分商品，避免为了 137 过期去兑 800 分大额。
        cover = min(point, expiring) if expiring > 0 else 0
        within_expiry = 0 if (expiring > 0 and point <= expiring) else 1
        scored.append(
            {
                "score": (within_expiry, point),
                "spuName": p.get("spuName"),
                "spuId": p.get("spuId"),
                "skuId": p.get("skuId"),
                "point": point,
                "spuCategory": str(p.get("spuCategory", "1")),
                "extTradePrice": p.get("extTradePrice"),
                "selling": p.get("selling"),
                "covers_expiring": cover,
            }
        )

    scored.sort(key=lambda x: x["score"])
    for row in scored:
        row.pop("score", None)
    return scored


def render(account: dict, recs: list[dict]) -> str:
    available = account.get("availablePoint")
    expiring = account.get("currentMouthExpirePoint")
    lines = [
        "麦省心 · 积分到期守护",
        "=" * 56,
        f"可用积分：{available} · 本月将过期：{expiring}",
        "",
    ]
    if float(expiring or 0) <= 0:
        lines.append("本月无即将过期积分；仍可按需兑换。")
    if not recs:
        lines.append("当前没有可推荐的兑换项（积分不足或已下架）。")
        return "\n".join(lines)

    lines.append("推荐（请人工确认后再 mall-create-order，一单一商品）：")
    for i, r in enumerate(recs[:5], 1):
        lines.append(
            f"[{i}] {r['spuName']} · {int(r['point'])} 分"
            f" · skuId={r['skuId']} · spuCategory={r['spuCategory']}"
            f" · 核销约 ¥{r.get('extTradePrice')}"
        )
        if r.get("covers_expiring"):
            lines.append(f"    可消化过期额度约 {r['covers_expiring']} 分")
    lines.append("")
    lines.append("示例确认调用（请勿在未确认时执行）：")
    top = recs[0]
    lines.append(
        json.dumps(
            {"skuId": top["skuId"], "spuCategory": top["spuCategory"], "count": 1},
            ensure_ascii=False,
        )
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="麦省心积分到期守护")
    parser.add_argument("--demo", action="store_true", help="使用 data/raw 样例")
    parser.add_argument("--input", type=Path, help="mall-redeem JSON")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    path = args.input or (RAW / "mall-redeem.sample.json")
    doc = load_json(path)
    account = doc.get("account") or {}
    # 兼容 query-my-account 扁平样例
    if "availablePoint" in doc and "account" not in doc:
        account = doc
    products = doc.get("products") or []
    recs = recommend(account, products)

    if args.json:
        json.dump({"account": account, "recommendations": recs}, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(render(account, recs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
