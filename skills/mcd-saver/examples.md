# 麦省心 · 示例话术与演示

## 用户一句话 → Agent 行为

### 「附近麦当劳，一个人下午茶 30 以内最划算」

1. `now-time-info` + `available-coupons` → 可领则 `auto-bind-coupons`
2. `query-my-account`（带积分过期提醒）
3. `query-nearby-stores(beType=1, searchType=1)`；无收藏再问城市地标
4. 确认门店后 `query-meals` + `query-store-coupons`
5. 券商品优先；不足预算用促销小食/饮品填充
6. `calculate-price` 出 1–2 方案，等「下单」

### 「帮我把快过期的积分兑掉」

1. `query-my-account` → 读 `currentMouthExpirePoint`
2. `mall-points-products(catRuleIds="1>4")`
3. 推荐 `point` 接近过期额度、仍在兑换期的商品
4. 确认 → `mall-product-detail` → `mall-create-order`（串行）

### 「想吃麦辣鸡腿堡，别太贵，控一下热量」

1. 走模式 A 选店 + 菜单
2. `list-nutrition-foods` 对照堡/小食能量
3. 优先三件套促销或 500 大卡分区；算价后说明能量估算

### 「外送到家，两人 80 块」

1. `delivery-query-addresses` → 选地址
2. `delivery-query-stores(beType=2)`
3. 菜单 + 门店券 + 双人餐/分享餐优先
4. 算价含配送；确认后 `create-order` 带 `addressId`

---

## 真实 MCP 演示摘要（2026-10-10）

账号（脱敏）：可用积分约 **1715.8**，本月将过期 **137.3**。

### 1. 一键领券

`auto-bind-coupons` → 成功领取 6 张，含：

- 巧克力味厚松饼猪柳蛋套餐 ×3
- 免费脆薯饼
- 人气麦旋风买一送一
- 9.9 元中杯冰美式

### 2. 收藏门店（到店）

`query-nearby-stores(beType=1, searchType=1)` 示例：

| 门店 | storeCode |
|------|-----------|
| 麦当劳广州信息港广酒大厦餐厅 | 1400904 |
| 麦当劳广州华观路得来速餐厅 | 1400290 |
| 麦当劳广州伟城广场餐厅 | 1400066 |

### 3. 门店可用券 → 算价

门店 `1400904`，`query-store-coupons`：

- **薯条三重奏** → productCode `9900010371`，券后可用
- **9.9 元中杯冰美式** → productCode `507411`

`calculate-price`（薯条三重奏 + 券）：

| 项 | 金额 |
|----|------|
| 原价 | ¥40.50 |
| 现价 | **¥19.90** |
| 已省 | **¥20.60** |
| 取餐方式 | 堂食 `eat-in` / 外带 `locker-in` |

### 4. 积分过期建议（示例）

可用 1715.8、本月过期 137.3 时，优先低门槛仍在期商品，例如：

- 50 积分：6.9 元派 / 6.9 元可乐麦炫酷
- 100 积分：10.9 元指定小食 / 3.9 元圆筒
- 200 积分：10.9～16.9 元档小食组合券

（具体以当时 `mall-points-products` 返回的 `upTime`/`downTime`/`status` 为准。）

---

### 「积分快过期，先别下单，给我兑换方案」

1. `query-my-account` → 本月过期 137.3
2. `mall-points-products` → `mall-product-detail(17074)`
3. 展示：50 分兑派券，`skuId=17780`，`spuCategory=1`，`shopId=2`
4. **停住**；用户说「兑换」再 `mall-create-order`

### 「想喝咖啡，热量低一点」

1. 省钱路径领到「9.9 冰美式」券并 `query-store-coupons` 确认本店可用
2. `list-nutrition-foods`：冰美式中杯 ~13 kcal
3. `calculate-price` → **¥9.90**（原价 ¥19.00）

---

## 推荐对用户回复（短）

> 已帮你领了 6 张券。收藏店「信息港广酒大厦」：  
> - 薯条三重奏券后 **¥19.9**（省 ¥20.6）  
> - 冰美式中杯券后 **¥9.9**（省 ¥9.1，约 13 kcal）  
> 本月 **137.3** 积分将过期 → 建议 50 分兑「6.9 元派任选」（sku 已备好）。  
> 今天周六麦金喜可抽（24 分/次），要的话再说。  
> 回复「下单堂食薯条」/「兑换派券」/「换预算」。
