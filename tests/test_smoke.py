#!/usr/bin/env python3
"""零依赖自测：样例数据 + 本地决策脚本。"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RAW = ROOT / "data" / "raw"
sys.path.insert(0, str(SCRIPTS))

import coupon_rank  # noqa: E402
import points_guard  # noqa: E402


class TestSamples(unittest.TestCase):
    def test_raw_files_exist(self):
        for name in (
            "store-coupons.sample.json",
            "calculate-price.sample.json",
            "account-points.sample.json",
            "mall-redeem.sample.json",
            "menu-prices.sample.json",
        ):
            self.assertTrue((RAW / name).is_file(), name)

    def test_price_units_are_fen(self):
        doc = json.loads((RAW / "calculate-price.sample.json").read_text(encoding="utf-8"))
        fries = doc["cases"][0]["response"]
        self.assertEqual(fries["price"], 1990)
        self.assertEqual(fries["originalPrice"], 4050)
        self.assertEqual(fries["discount"], 2060)
        self.assertAlmostEqual(coupon_rank.fen_to_yuan(1990), 19.9)

    def test_no_secrets_in_repo_text(self):
        import re

        text_files = []
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            if any(part in {".git", ".tools", "__pycache__", "assets"} for part in path.parts):
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pyc"}:
                continue
            text_files.append(path)

        other_files = [p for p in text_files if p.name != "test_smoke.py"]
        blob = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in other_files)
        # 完整 token 形态，不是前缀字面量（避免自测文件误伤）
        self.assertIsNone(re.search(r"gho_[A-Za-z0-9]{10,}", blob))
        self.assertIsNone(re.search(r"ghp_[A-Za-z0-9]{10,}", blob))
        self.assertIsNone(re.search(r"github_pat_[A-Za-z0-9_]{10,}", blob))
        self.assertIsNone(re.search(r"\beyJ[A-Za-z0-9_\-]{20,}\.", blob))
        # 真实券码模式：MCD + 长串，不允许 SAMPLE 占位以外的完整码
        for match in re.finditer(r"MCD[0-9A-Za-z]{12,}", blob):
            self.assertIn("SAMPLE", match.group(0), f"疑似真实券码: {match.group(0)}")
        # 曾误提交过的完整 couponId（拆开写，避免本测试文件自身命中）
        leaked_id = "".join(["8BA8C664", "3FA8580A", "2A2FF2E4", "6495F876"])
        self.assertNotIn(leaked_id, blob)
        self.assertIn("${MCD_MCP_TOKEN}", (ROOT / "mcp-config.example.json").read_text(encoding="utf-8"))


class TestCouponRank(unittest.TestCase):
    def test_demo_ranks_by_savings(self):
        coupons = json.loads((RAW / "store-coupons.sample.json").read_text(encoding="utf-8"))
        menu = json.loads((RAW / "menu-prices.sample.json").read_text(encoding="utf-8"))
        priced = json.loads((RAW / "calculate-price.sample.json").read_text(encoding="utf-8"))
        deals = coupon_rank.estimate_coupon_deals(coupons["data"], menu["meals"], priced)
        self.assertGreaterEqual(len(deals), 2)
        self.assertEqual(deals[0]["product_code"], "9900010371")
        self.assertAlmostEqual(deals[0]["save_yuan"], 20.6)
        self.assertAlmostEqual(deals[1]["pay_yuan"], 9.9)

    def test_cli_demo(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "coupon_rank.py"), "--demo"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("¥19.90", proc.stdout)
        self.assertIn("本店券", proc.stdout)


class TestPointsGuard(unittest.TestCase):
    def test_prefers_low_threshold_covering_expiry(self):
        doc = json.loads((RAW / "mall-redeem.sample.json").read_text(encoding="utf-8"))
        recs = points_guard.recommend(doc["account"], doc["products"])
        self.assertTrue(recs)
        self.assertEqual(recs[0]["point"], 50)
        self.assertEqual(recs[0]["skuId"], 17780)
        self.assertLessEqual(recs[0]["point"], float(doc["account"]["availablePoint"]))

    def test_cli_demo(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "points_guard.py"), "--demo"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("137.3", proc.stdout)
        self.assertIn("skuId=17780", proc.stdout)


class TestContestFiles(unittest.TestCase):
    def test_required_files(self):
        for name in (
            "README.md",
            "CONTEST_DECLARATION.md",
            "MCP_INTEGRATION.md",
            "mcp-config.example.json",
            "SKILL.md",
        ):
            self.assertTrue((ROOT / name).is_file(), name)

    def test_mcp_config_has_placeholder_only(self):
        cfg = json.loads((ROOT / "mcp-config.example.json").read_text(encoding="utf-8"))
        auth = cfg["mcpServers"]["mcd-mcp"]["headers"]["Authorization"]
        self.assertIn("${MCD_MCP_TOKEN}", auth)
        self.assertNotRegex(auth, r"Bearer\s+[A-Za-z0-9_\-]{20,}")

    def test_declaration_title(self):
        text = (ROOT / "CONTEST_DECLARATION.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# 参赛声明"))
        self.assertIn("信息安全声明", text)


if __name__ == "__main__":
    unittest.main()
