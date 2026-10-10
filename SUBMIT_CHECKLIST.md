# 交卷自检清单

对照 [活动规则](https://github.com/M-China/mcd-developer-innovation-challenge) / `activityGuidelines.md`。

## 仓库必过项

- [x] `README.md`（介绍 / 安装 / 示例 / 目标用户）
- [x] `CONTEST_DECLARATION.md`（官方原文，未改）
- [x] `MCP_INTEGRATION.md`
- [x] `mcp-config.example.json`（仅 `${MCD_MCP_TOKEN}` 占位）
- [x] 源代码：`SKILL.md` + `scripts/` + `tests/`
- [x] 无真实 Token / 无完整生产券码
- [x] GitHub **Public** 仓库：https://github.com/jackylany/mcd-saver
- [x] 仓库创建时间在 2025-12-25 ~ 2026-10-25（2026-10-10 创建）
- [x] 报名 Issue：https://github.com/M-China/mcd-developer-innovation-challenge/issues/268

## 本地验收

```bash
python tests/test_smoke.py
python scripts/demo_replay.py
python scripts/coupon_rank.py --demo
python scripts/points_guard.py --demo
```

## 排名提示

排行榜按公开 **Star** 数；Star=0 不进榜。交卷后可适当传播 README 钩子与 `assets/poster.png`。

本项目**不参加** WorkBuddy 专项（无 `workbuddy.md`）。
