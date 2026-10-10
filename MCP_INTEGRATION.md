# MCP 接入说明

本项目真实接入并使用麦当劳中国官方 MCP Server，把「领券 / 本店可用券 / 算价 / 积分过期」串成一条省钱决策链。

## 1. 接入的 MCP Server

| 项 | 值 |
|---|---|
| 服务名称 | 麦当劳中国 MCP Server（`mcd-mcp`） |
| 提供方 | 麦当劳中国（金拱门（中国）有限公司） |
| 接入地址 | `https://mcp.mcd.cn` |
| 传输协议 | Streamable HTTP |
| 认证方式 | 请求头 `Authorization: Bearer <MCD_MCP_TOKEN>` |
| Token 申请 | [open.mcd.cn/mcp](https://open.mcd.cn/mcp) 登录 → 控制台 → 激活 |

配置示例见 [`mcp-config.example.json`](mcp-config.example.json)，**仅使用环境变量占位符**。本仓库不含任何真实 Token。

在 Cursor 等客户端中，连接成功后工具可能出现在 `mcd-mcp` / `user-mcd-mcp` 等命名空间下；工具名以短横线为准（如 `query-store-coupons`）。

## 2. 实际使用的 Tool 与业务价值

### 2.1 省钱主路径（必须）

| Tool | 解决什么问题 | 在流程中的位置 |
|------|--------------|----------------|
| `now-time-info` | 对齐早餐/下午茶等时段券 | 开场 |
| `available-coupons` | 有哪些可领 | 资产预热 |
| `auto-bind-coupons` | 一键领取可领券 | 用户同意省钱时 |
| `query-nearby-stores` | 到店/得来速选店，拿 `storeCode`/`beCode` | 选店 |
| `delivery-query-addresses` / `delivery-query-stores` | 外送地址与可配送门店 | 外送分支 |
| `query-meals` | 门店在售与现价 | 组单 |
| `query-meal-detail` | 套餐组成与特制 key | 需改配时 |
| `query-my-coupons` | 卡包总览（**不保证**本单可用） | 对照用 |
| `query-store-coupons` | **本店+订单类型**真正可用的券 | 组单核心 |
| `calculate-price` | 实付金额（单位：**分**）与取餐方式 | 比价 |
| `create-order` | 创建订单（须用户确认） | 收尾 |
| `query-order` / `order-list` | 支付后查单 | 收尾 |

### 2.2 积分守护（主增强）

| Tool | 解决什么问题 |
|------|--------------|
| `query-my-account` | 读 `availablePoint` / `currentMouthExpirePoint` |
| `mall-points-products` | 可兑商品券列表（常用 `catRuleIds=1>4`） |
| `mall-product-detail` | 取 `skuId` / `shopId` / `spuCategory` |
| `mall-create-order` | 积分兑换（仅 `shopId=2`；一单一商品且须串行） |

### 2.3 可选增强

| Tool | 用途 |
|------|------|
| `campaign-calendar` | 今日活动上下文 |
| `list-nutrition-foods` | 用户主动提控热量时交叉推荐 |
| `query-lottery-info` / `draw-lottery` | 彩蛋提醒；**不自动抽** |

派对 / 企业团餐相关 Tool 未作为本项目主路径（见 `skills/mcd-saver/reference.md`）。

## 3. 调用流程

```
now-time-info
    │
    ├─ available-coupons ──► (用户同意) auto-bind-coupons
    ├─ query-my-account     ──► 若有将过期积分：准备积分建议
    └─ campaign-calendar    ──► 可选
            │
            ▼
query-nearby-stores / delivery-*   ──► 确认门店 storeCode[, beCode]
            │
            ▼
query-meals  +  query-store-coupons
            │
            ▼
券驱动组单（本店可用券优先）+ 预算填充
            │
            ▼
calculate-price × N 候选   ──► 分÷100 展示元
            │
            ▼
用户确认 ──► create-order（到店带 takeWayCode）
            │
            └─ 可选并行：mall-product-detail → (确认) mall-create-order
```

## 4. 关键约定与实测坑

### 4.1 beType ↔ orderType / beCode

| beType | 场景 | orderType | beCode |
|--------|------|-----------|--------|
| 1 | 到店自取 | 1 | 不传 |
| 5 | 得来速 | 1 | 必传（来自 nearby-stores） |
| 2 | 麦乐送 | 2 | 必传（来自 delivery-stores） |
| 6 | 企业团餐 | 2 | 必传 + `gmServiceCode` |

### 4.2 券的三层语义（本项目核心洞见）

1. `available-coupons` / `auto-bind-coupons`：可领 / 已领  
2. `query-my-coupons`：卡包资产 ≠ 本单可用  
3. `query-store-coupons`：当前门店 + 订单类型可用 → 下单必须用这里的 `couponId` + `couponCode`

把第 2 层券直接带进 `calculate-price` / `create-order`，是省钱链路最常见的失败原因。

### 4.3 金额单位

`calculate-price` 返回值为**分**。对用户展示时必须 ÷100 为**元**。

### 4.4 选店搜索

`query-nearby-stores` 在 `searchType=2` 时必须同时传 `city` + `keyword`；只传城市会失败。优先 `searchType=1` 走收藏。

### 4.5 积分兑换

- 仅 `shopId=2` 可走 `mall-create-order`  
- 一单一商品；多件必须等前单成功再下下一单  
- 任何兑换 / 点餐下单前必须显式确认

## 5. 真实调用证据（脱敏）

2026-10-10 实跑摘要（完整记录见 `demos/`，样例 JSON 见 `data/raw/`）：

| 步骤 | 结果 |
|------|------|
| `auto-bind-coupons` | 成功领取 6 张 |
| `query-nearby-stores` | 收藏到店门店含 `1400904` 等 |
| `query-store-coupons` | 薯条三重奏 / 9.9 冰美式对本店可用 |
| `calculate-price` 薯条三重奏+券 | 原价 4050 分 → 现价 **1990 分（¥19.90）**，省 2060 分 |
| `calculate-price` 冰美式+券 | 原价 1900 分 → 现价 **990 分（¥9.90）** |
| `query-my-account` | 可用约 1715.8，本月将过期 **137.3** |
| `mall-product-detail(17074)` | 50 分兑派券，`skuId=17780`，`shopId=2`（未代下兑换单） |

本地决策逻辑可离线复现：

```bash
python scripts/coupon_rank.py --demo
python scripts/points_guard.py --demo
python tests/test_smoke.py
```

## 6. 安全与合规

- 仓库内无 Token、无完整券码明文（样例已脱敏）  
- Skill / Agent **默认停在确认价**；`create-order` / `mall-create-order` / `draw-lottery` 仅在用户明确确认后调用  
- 输出为点餐决策参考，餐品与价格以官方实时结果为准  
