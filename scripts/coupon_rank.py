#!/usr/bin/env python3
"""麦省心 · 本店可用券排序（零第三方依赖，可离线跑）。

输入：门店可用券 + 菜单价（或内置 demo）。
输出：按「预估可省金额」排序的方案，提醒券码须来自 query-store-coupons。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def fen_to_yuan(fen: int) -> float:
    return fen / 100.0


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def estimate_coupon_deals(coupons: list, meals: dict, priced: dict | None = None) -> list[dict]:
    """把本店券映射成可解释的候选方案。

    若提供 calculate-price 样例（priced），优先用真实算价；
    否则用菜单 currentPrice 作为「无券参考价」，并标记为估算。
    """
    priced_by_code: dict[str, dict] = {}
    if priced:
        for case in priced.get("cases", []):
            resp = case.get("response", {})
            for item in resp.get("productList", []):
                priced_by_code[item["productCode"]] = {
                    "name": item.get("productName"),
                    "original_fen": resp.get("originalPrice", item.get("originalSubtotal")),
                    "price_fen": resp.get("price", item.get("subtotal")),
                    "discount_fen": resp.get("discount", 0),
                    "source": "calculate-price",
                    "case": case.get("name"),
                }

    deals = []
    for coupon in coupons:
        products = coupon.get("products") or []
        if not products:
            continue
        product = products[0]
        code = product["productCode"]
        title = coupon.get("title", "")
        meal = meals.get(code, {})

        if code in priced_by_code:
            row = priced_by_code[code]
            deals.append(
                {
                    "rank_key": row["discount_fen"],
                    "coupon_title": title,
                    "product_code": code,
                    "product_name": row["name"] or product.get("productName") or meal.get("name"),
                    "original_yuan": fen_to_yuan(row["original_fen"]),
                    "pay_yuan": fen_to_yuan(row["price_fen"]),
                    "save_yuan": fen_to_yuan(row["discount_fen"]),
                    "evidence": row["source"],
                    "note": row.get("case", ""),
                }
            )
        else:
            # 无算价证据时：只能展示菜单价，节省额未知（避免瞎编）
            cur = float(meal.get("currentPrice") or 0)
            deals.append(
                {
                    "rank_key": -1,
                    "coupon_title": title,
                    "product_code": code,
                    "product_name": product.get("productName") or meal.get("name") or code,
                    "original_yuan": cur,
                    "pay_yuan": None,
                    "save_yuan": None,
                    "evidence": "menu-only",
                    "note": "需再调 calculate-price 才有实付",
                }
            )

    deals.sort(key=lambda d: (d["rank_key"] < 0, -d["rank_key"]))
    return deals


def render(deals: list[dict]) -> str:
    lines = [
        "麦省心 · 本店券方案排序",
        "=" * 56,
        "规则：只用 query-store-coupons 的券；卡包券不能直接当本店可用。",
        "",
    ]
    if not deals:
        lines.append("（无可用券候选）")
        return "\n".join(lines)

    for i, d in enumerate(deals, 1):
        if d["pay_yuan"] is None:
            lines.append(
                f"[{i}] {d['coupon_title']} → {d['product_name']}\n"
                f"    菜单参考价 ¥{d['original_yuan']:.2f} · {d['note']}"
            )
        else:
            lines.append(
                f"[{i}] {d['coupon_title']} → {d['product_name']}\n"
                f"    现价 ¥{d['pay_yuan']:.2f}（原价 ¥{d['original_yuan']:.2f}，"
                f"已省 ¥{d['save_yuan']:.2f}）· 证据:{d['evidence']}"
            )
    lines.append("")
    lines.append("下一步：选一个方案，确认后再 create-order。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="麦省心本店券排序")
    parser.add_argument("--demo", action="store_true", help="使用 data/raw 样例")
    parser.add_argument("--coupons", type=Path, help="query-store-coupons JSON")
    parser.add_argument("--menu", type=Path, help="菜单价 JSON")
    parser.add_argument("--priced", type=Path, help="calculate-price 样例 JSON")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args(argv)

    if args.demo or not args.coupons:
        coupons_doc = load_json(RAW / "store-coupons.sample.json")
        menu_doc = load_json(RAW / "menu-prices.sample.json")
        priced_doc = load_json(RAW / "calculate-price.sample.json")
    else:
        coupons_doc = load_json(args.coupons)
        menu_doc = load_json(args.menu) if args.menu else {"meals": {}}
        priced_doc = load_json(args.priced) if args.priced else None

    deals = estimate_coupon_deals(
        coupons_doc.get("data", []),
        menu_doc.get("meals", {}),
        priced_doc,
    )

    if args.json:
        json.dump(deals, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(render(deals))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
