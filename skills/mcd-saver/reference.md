# 麦省心 · MCP 参考

工具均在 `user-mcd-mcp`（或配置中的 mcd-mcp）命名空间。

## 工具速查

### 账户 / 时间 / 活动

| 工具 | 用途 | 关键字段 |
|------|------|----------|
| `now-time-info` | 服务器时间，判断早餐/下午茶/夜市 | `formatted`, `dayOfWeek` |
| `query-my-account` | 积分余额与过期 | `availablePoint`, `currentMouthExpirePoint` |
| `campaign-calendar` | 当月/指定日活动 | 今日活动作推荐上下文 |
| `query-lottery-info` | 查抽奖是否进行中、消耗规则 | `drawDecision.resourceEligible` |
| `draw-lottery` / `query-my-prizes` | 抽奖 / 查奖品（非主路径） | **仅用户明确说抽**再调 |

### 券

| 工具 | 何时用 |
|------|--------|
| `available-coupons` | 有什么可领 |
| `auto-bind-coupons` | 一键领完可领券 |
| `query-my-coupons` | 卡包总览（**不保证**当前订单可用） |
| `query-store-coupons` | **下单前必查**：门店+orderType 可用券，拿 `couponId`+`couponCode`+适用 `productCode` |

### 门店 / 地址

| 工具 | 场景 |
|------|------|
| `query-nearby-stores` | 到店 `beType=1` / 得来速 `beType=5` |
| `delivery-query-addresses` | 外送地址列表 |
| `delivery-query-stores` | 地址可配送门店（`beType=2` 或 `6`） |
| `delivery-create-address` | 新建地址（用户明确要求） |

`query-nearby-stores` 参数：

- `searchType=1`：收藏（默认路径）
- `searchType=2`：位置搜，必填 `city` + `keyword`
- 返回务必保留完整 `storeCode`；`beType=5` 时保留 `beCode`
- `reservation=true` 时完整展示 `reservationTimeOptions`（含 `today`）

### 菜单 / 算价 / 下单

| 工具 | 用途 |
|------|------|
| `query-meals` | 菜单分类 + `meals[code]` 价格 |
| `query-meal-detail` | 套餐组成、特制 `modification` |
| `calculate-price` | 实付（**分**）；拿 `takeWayList` |
| `create-order` | 正式下单（需确认） |
| `query-order` / `order-list` / `cancel-order` | 支付后查询 / 取消 |

`calculate-price` / `create-order` 商品项常用字段：

- `productCode`, `quantity`
- `couponId`, `couponCode`（成对）
- `modification.values[]`：`code` / `key` / `quantity`
- `roundList`：套餐子项
- `withOrder`：随单购（菜单里 `canWithOrder` + 优惠价时往往必须带）

特制 key 规则（来自 meal-detail）：

- 选中项：`key = selectedKey`
- 未选中但有 `unselectedKey`：也必须传，`key = unselectedKey`

### 积分商城

| 工具 | 用途 |
|------|------|
| `mall-points-products` | 可兑列表；商品券用 `catRuleIds="1>4"` |
| `mall-product-detail` | SKU / `shopId` |
| `mall-create-order` | 兑换；仅 `shopId=2`；一单一商品且串行 |
| `mall-order-list` / `mall-order-detail` | 兑换订单 |

### 营养 / 团餐 / 派对（扩展）

| 工具 | 用途 |
|------|------|
| `list-nutrition-foods` | 常见餐品营养 |
| `query-promotions` / `query-meal-assistance` | 仅企业团餐 `beType=6` |
| `query-party-city` → `query-party-store` → `query-party-store-date` → `query-party-store-session` → `party-order-create` | 派对链路（非麦省心主路径） |

## 推荐决策启发式

省钱排序（从高到低）：

1. `query-store-coupons` 命中的用券价
2. 菜单 `currentPrice` 相对 `originalPrice` 折扣大的促销/活动品
3. 积分兑换券（若用户接受先兑再点）
4. 原价补齐预算

积分守护：

1. `currentMouthExpirePoint > 0` 优先消化
2. 在 `point ≤ availablePoint` 中选仍有效、门槛低、与本次饮食相关的券
3. 过期窗口紧时，宁可兑低门槛券，也不要空过期

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| 工具报 beCode | 得来速/外送忘传或到店误传 | 按 beType 表纠正 |
| 券下单失败 | 用了卡包券但非门店可用 | 改用 `query-store-coupons` |
| 价格对不上 | 把「分」当「元」 | ÷100 |
| 随单购价失效 | 促销价依赖 `withOrder` 未传 | 按菜单 withOrder 带上 |
| 积分兑换连下多单失败 | 未串行 | 等成功再下一单 |
