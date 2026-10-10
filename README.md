# 麦省心 · MCD Saver

### 卡包里有券，不代表这一单能用。

同一家店、同一张「薯条三重奏」券，算完价是：

**原价 ¥40.50 → 实付 ¥19.90（省 ¥20.60）**

但如果你拿错了「卡包券」而不是「本店可用券」，链路会直接失败。  
差的不是运气，是**券的三层语义**没人帮你分清。

![麦省心](assets/poster.png)

麦当劳 MCP 能领券、能查卡包、能下单——真正难的是把

**可领 → 已领 → 本店本单可用 → 算价 → 确认下单**

收成一条决策链，并顺手拦住**即将过期的积分**。

> 本项目是「2026 麦当劳程序员创意开发大赛」参赛作品，由参赛者独立开发，非麦当劳官方产品。

---

## 它解决什么问题

| 现实摩擦 | 后果 |
|----------|------|
| 可领券 / 卡包券 / 本店可用券混为一谈 | 以为省了，结账才发现不能用 |
| 积分静默过期 | 资产蒸发（演示样例本月过期 **137.3**） |
| 菜单促销、活动、随单购叠在一起 | 决策瘫痪，随便点、多花钱 |

**麦省心**是一个 Agent Skill：教 AI 按正确顺序调 MCP，并给出可离线复现的本地决策脚本。

它不劝你多吃，也不替你付钱——**算清楚，你确认，再下单。**

---

## 30 秒快速体验（不需要 Token）

环境：Python 3.8+，零第三方依赖。

```bash
git clone https://github.com/jackylany/mcd-saver.git
cd mcd-saver
python scripts/demo_replay.py
python scripts/coupon_rank.py --demo
python scripts/points_guard.py --demo
python tests/test_smoke.py
```

样例来自 2026-10-10 真实 MCP 调用的**脱敏回放**（见 `data/raw/`、`demos/`）。

预期你会看到：薯条三重奏券后 **¥19.90**、冰美式 **¥9.90**、积分过期提醒与 `skuId` 级兑换建议。

---

## 装成 Skill（推荐）

把本仓库放到客户端的 skills 目录（或复制 `SKILL.md` + `scripts/` + `skills/` + `data/`）：

| 客户端 | 路径示例 |
|--------|----------|
| Cursor（项目级） | `<repo>/.cursor/skills/mcd-saver/` |
| Cursor（用户级） | `~/.cursor/skills/mcd-saver/` |
| 其他支持 Agent Skills 的客户端 | 按其文档放置，根目录 `SKILL.md` 可直接作为入口 |

然后在对话里说：

```text
按 mcd-saver skill：到店自取，用收藏门店，
给我一个下午茶最划算方案；先说明再领券，算完价等我确认。
顺带看看本月快过期的积分能兑什么。
```

---

## 接上麦当劳 MCP（要真门店 / 真价格 / 真下单时）

1. 在 [open.mcd.cn/mcp](https://open.mcd.cn/mcp) 申请 Token  
2. 将 [`mcp-config.example.json`](mcp-config.example.json) 合并进你的 MCP 客户端配置，把 `${MCD_MCP_TOKEN}` 换成自己的 Token  
3. **不要把真实 Token 提交进任何仓库**

详细 Tool 列表、调用顺序与踩坑见 [`MCP_INTEGRATION.md`](MCP_INTEGRATION.md)。

---

## 两个核心能力

### 1. 本店券驱动的省钱组单

```bash
python scripts/coupon_rank.py --demo
```

```
[1] 薯条三重奏 → 薯条三重奏
    现价 ¥19.90（原价 ¥40.50，已省 ¥20.60）· 证据:calculate-price
[2] 9.9元中杯冰美式 → 麦咖啡™冰美式中杯
    现价 ¥9.90（原价 ¥19.00，已省 ¥9.10）· 证据:calculate-price
```

Live 路径：`available-coupons` →（同意后）`auto-bind-coupons` → 选店 → `query-store-coupons` → `calculate-price` → 确认 → `create-order`。

### 2. 积分到期守护

```bash
python scripts/points_guard.py --demo
```

读出将过期积分，给出低门槛、仍在兑换期、`shopId=2` 的候选，并打印待确认的 `mall-create-order` 参数——**默认不代兑**。

---

## 目录结构

```
mcd-saver/
├── README.md
├── SKILL.md                    # Skill 入口（给 Agent）
├── CONTEST_DECLARATION.md      # 参赛声明（官方原文，勿改）
├── MCP_INTEGRATION.md          # MCP 用法与业务价值
├── mcp-config.example.json     # 脱敏配置（仅占位符）
├── PITCH.md                    # 一页介绍
├── DEMO-SCRIPT.md              # 90 秒演示脚本
├── REGISTRATION.md             # Issue 报名文案草稿
├── LICENSE
├── assets/poster.png           # 宣传图
├── data/raw/                   # 脱敏 MCP 样例（可复现）
├── demos/                      # 真实跑通记录
├── scripts/                    # 离线决策 / 回放（标准库）
├── tests/test_smoke.py
└── skills/mcd-saver/           # reference + examples
```

---

## 设计取舍

1. **主路径做「钱」不做「说教」**——官方示例里点餐/省钱场景很常见，我们把差异放在「券三层语义 + 积分过期」的工程化决策上。  
2. **Skill 写规则，脚本写可复现**——Agent 负责调 MCP；本地脚本保证别人 clone 下来也能看到同样的排序逻辑。  
3. **默认停在确认价**——保护用户账号；演示不强制支付/兑换/抽奖。  
4. **不写死商品 ID**——Live 每次现查菜单与本店券；样例只用于离线证据。

---

## 目标用户

- 经常点麦当劳、嫌券规则绕的人  
- 积分余额不低、却总忘记兑的人  
- 想基于 MCP 做 Agent Skill、需要可复现样例的开发者  

---

## 数据与免责

- 演示数字来自麦当劳中国 MCP 真实调用后的脱敏回放；门店/价格/券以官方实时结果为准  
- 输出为点餐决策参考，不构成任何专业建议  
- 仅使用官方公开 MCP 接口，无逆向、无破解  
- 详见 [CONTEST_DECLARATION.md](CONTEST_DECLARATION.md)

## 许可证

[MIT](LICENSE)

---

如果麦省心帮你少踩一次「券不能用」或少浪费一笔过期积分，欢迎点个 Star。
