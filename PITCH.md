# 麦省心 · 一页介绍

**作品名**：麦省心（mcd-saver）  
**形态**：Cursor / Agent Skill + 零依赖 Python 决策脚本  
**一句话**：分清「可领 / 卡包 / 本店可用」三层券，算出实付，并拦住过期积分。

## 痛点 → 方案

| 痛点 | 方案 |
|------|------|
| 卡包有券 ≠ 本单能用 | 强制走 `query-store-coupons` 再算价 |
| 积分默默过期 | `query-my-account` → 低门槛兑换建议 |
| 演示不可复现 | `data/raw` 脱敏样例 + `scripts/*` 离线回放 |

## 证据数字（2026-10-10 脱敏）

- 薯条三重奏券后 **¥19.90**（省 ¥20.60）
- 冰美式中杯券后 **¥9.90**（省 ¥9.10）
- 本月将过期积分 **137.3** → 建议 50 分兑派券（`skuId=17780`，未代下）

## 必交文件

README · CONTEST_DECLARATION · MCP_INTEGRATION · mcp-config.example.json · SKILL/scripts 源码

## 金句

> 不是菜单浏览器，而是把 MCP 的券、店、价、积分打成一条「省钱决策链」。
