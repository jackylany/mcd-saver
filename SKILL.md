---
name: mcd-saver
description: >-
  麦省心：基于麦当劳 MCP 的省钱点餐与积分到期守护 Skill。
  把「可领券 / 卡包券 / 本店可用券」三层语义分清，按门店可用券组单、
  calculate-price 比价，并在下单前提醒即将过期的积分。
  在用户说「点麦当劳」「最划算」「帮我领券」「积分快过期」「附近麦当劳」
  「下午茶怎么点」或需要走完领券→选店→组单→算价→确认下单时使用。
---

# 麦省心 (mcd-saver)

用麦当劳 MCP 把「想吃 → 最划算下单」变成可执行工作流。默认**到店自取**。

路径约定：下文 `scripts/`、`data/`、`skills/` 均相对于**本文件所在目录**（仓库根）。

## 硬性规则

1. **先确认再下单**：`create-order` / `mall-create-order` / `draw-lottery` 前必须展示方案，等用户明确确认。
2. **金额单位**：`calculate-price` 返回值为**分**，展示时 ÷100 成**元**。
3. **beType ↔ orderType / beCode**：

| beType | 场景 | orderType | beCode |
|--------|------|-----------|--------|
| 1 | 到店自取 | 1 | 不传 |
| 5 | 得来速 | 1 | 必传 |
| 2 | 麦乐送 | 2 | 必传 |
| 6 | 企业团餐 | 2 | 必传 + `gmServiceCode` |

4. **券三层语义不可混**：
   - `available-coupons` / `auto-bind-coupons`：可领 / 领取（领券前先告知用户）
   - `query-my-coupons`：卡包资产（未必本单可用）
   - `query-store-coupons`：**本店+订单类型**可用 → 下单只用这里的 `couponId`+`couponCode`
5. 工具名以短横线为准；客户端命名空间可能是 `mcd-mcp` / `user-mcd-mcp`。

## 模式

| 模式 | 目标 |
|------|------|
| A 省钱下单 | 最低实付可达方案（主路径） |
| B 积分守护 | 优先消化 `currentMouthExpirePoint` |
| C 轻量健康 | 仅用户主动提热量时增强 |
| D 彩蛋 | 抽奖只提醒，不自动抽 |

细节、参数与话术：`skills/mcd-saver/reference.md`、`skills/mcd-saver/examples.md`。

## 模式 A：省钱下单

1. 澄清：取餐方式、人数/预算/偏好；有收藏先用收藏店。
2. 并行：`now-time-info`、可领券（征得同意后再 `auto-bind-coupons`）、`query-my-account`。
3. 选店：`query-nearby-stores` 或外送地址链路；展示并确认 `storeCode`。
4. `query-meals` + `query-store-coupons` → **券驱动组单**，预算内填充。
5. 对 1–3 个候选 `calculate-price`，展示原价/现价/已省（元）与 `takeWayList`。
6. 用户确认后 `create-order`（到店必带 `takeWayCode`）。

离线核对排序（不联网）：

```bash
python scripts/coupon_rank.py --demo
```

## 模式 B：积分守护

```
query-my-account
→ 警告 currentMouthExpirePoint
→ mall-points-products(catRuleIds="1>4")
→ mall-product-detail → 展示 skuId
→ 用户确认后 mall-create-order（shopId=2；一单一商品；串行）
```

```bash
python scripts/points_guard.py --demo
```

## 输出模板

```markdown
## 麦省心方案
- 门店：{name}（{storeCode}）· {到店|外送|得来速}
- 篮子 / 券：…
- 价格：现价 ¥X.XX（原价 ¥Y.YY，已省 ¥Z.ZZ）
- 积分：本月将过期 {n}，建议 {兑换项}（skuId=…，等确认）
- 下一步：回复「下单」/「兑换」/「换方案」
```

## 失败降级

- 无收藏店 → `searchType=2` 要 `city`+`keyword`
- 无本店券 → 用菜单促销价仍算价
- 算价失败 → 去券/去特制重试
- 用户只看不买 → 停在方案
