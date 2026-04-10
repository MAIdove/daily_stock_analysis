# 股票和指数配置指南

## 问题背景

**Tushare Pro API 只支持股票/ETF 数据，不支持纯指数数据。**

当你在 `STOCK_LIST` 中混合配置股票（如 SPY, QQQ）和指数（如 SPX, IXIC, DJI）时，系统会试图从 Tushare 获取指数数据，导致格式错误。

---

## 解决方案

项目现已自动分类符号，根据类型选择合适的数据源：

### 数据源分配规则

| 类型 | 示例 | 数据源 | 说明 |
|------|------|--------|------|
| **股票/ETF** | SPY, QQQ, AAPL, 600519 | YFinance / Tushare | 可用多个数据源 |
| **美股指数** | SPX, IXIC, DJI, VIX | YFinance 仅 | ⚠️ Tushare 不支持 |
| **港股指数** | HSI, HSCEI | YFinance 仅 | ⚠️ Tushare 不支持 |
| **A股指数** | 000001, 399001, 000300 | YFinance / AKShare | ⚠️ Tushare 不支持 |

---

## 配置示例

### ✅ 推荐配置（自动分离处理）

```env
# .env 中的 STOCK_LIST 可以混合配置，系统自动分类

# 示例 1: 纯美股 ETF + 指数
STOCK_LIST=SPY,QQQ,VTI,VGT,XLK,SPX,IXIC,DJI

# 系统自动识别：
# - 股票/ETF：SPY, QQQ, VTI, VGT, XLK → Tushare/YFinance
# - 指数：SPX, IXIC, DJI → YFinance 仅

# 示例 2: 混合 A股 + 美股
STOCK_LIST=600519,000001,000300,SPY,QQQ,SPX,IXIC

# 系统自动识别：
# - A股股票：600519 → Tushare/YFinance
# - A股指数：000001, 000300 → YFinance/AKShare
# - 美股 ETF：SPY, QQQ → Tushare/YFinance
# - 美股指数：SPX, IXIC → YFinance 仅
```

### 运行日志示例

```
📊 股票/指数分类结果:
   总数: 8
   股票/ETF: 5 个 → ['SPY', 'QQQ', 'VTI', 'VGT', 'XLK'] → 数据源: YFinance / Tushare
   指数: 3 个 → ['SPX', 'IXIC', 'DJI'] → 数据源: YFinance 仅
✅ 混合配置，已自动分离
```

---

## 支持的指数代码

### 美股指数（US_INDEX）
- `SPX` - 标普500指数
- `IXIC` - 纳斯达克100指数
- `DJI` - 道琼斯工业平均指数
- `VIX` - 波动率指数

### 港股指数（HK_INDEX）
- `HSI` - 恒生指数
- `HSCEI` - 恒生中企指数

### A股指数（CN_INDEX）
- `000001` - 上证指数
- `000016` - 上证50
- `000300` - 沪深300
- `000905` - 中证500
- `399001` - 深证成指
- `399006` - 创业板指

---

## Tushare 不支持指数的原因

Tushare Pro 文档明确说明：

> **美股指数数据**：Tushare 仅提供 `us_adjfactor`（美股复权因子）和个股数据
> 
> ❌ 不支持：SPX, IXIC, DJI 等纯指数代码
> ✅ 支持：AAPL, SPY, MSFT 等个股和 ETF

### 查证链接
- https://tushare.pro/document/2?doc_id=402 - 美股复权因子（仅个股）
- https://tushare.pro/document/2?doc_id=254 - 美股日线行情（仅个股）

---

## 故障排除

### Q: 为什么收不到指数数据？
**A:** 系统已自动使用 YFinance 获取指数数据，无需配置。如果出现错误，检查网络连接。

### Q: 可以只分析指数吗？
**A:** 可以，但会跳过 Tushare 初始化。系统会自动用 YFinance 获取：
```env
STOCK_LIST=SPX,IXIC,DJI
# 日志输出：仅包含指数，没有股票！建议检查 STOCK_LIST 配置 ⚠️
```

### Q: 能否添加新的指数？
**A:** 可以。编辑 `src/utils/stock_classifier.py`，在对应的集合中添加代码：
```python
US_INDEX_SYMBOLS.add('NEW_INDEX')
```

---

## 技术实现

### 分类逻辑流程

```
STOCK_LIST (用户输入)
    ↓
stock_classifier.separate_stocks_and_indices()
    ├→ 检查是否在 US_INDEX_SYMBOLS
    ├→ 检查是否在 HK_INDEX_SYMBOLS
    ├→ 检查是否在 CN_INDEX_SYMBOLS
    └→ 其他视为股票/ETF
    ↓
分离结果 (stocks, indices)
    ├→ 股票/ETF: 优先 Tushare，降级 YFinance
    └→ 指数: YFinance 仅
```

### 核心代码

```python
from src.utils.stock_classifier import separate_stocks_and_indices, log_classification_summary

# 分离
stocks, indices = separate_stocks_and_indices(['SPY', 'SPX', 'QQQ', 'IXIC'])
# → (['SPY', 'QQQ'], ['SPX', 'IXIC'])

# 日志
log_classification_summary(['SPY', 'SPX', 'QQQ', 'IXIC'])
# → 📊 股票/指数分类结果: ...
```

---

## 最佳实践

1. **混合配置最佳** - 不要刻意分离，系统自动处理：
   ```env
   STOCK_LIST=SPY,QQQ,VTI,SPX,IXIC,DJI  ✅
   ```

2. **监控日志输出** - 每次运行检查分类结果：
   ```
   📊 股票/指数分类结果:
      总数: 8
      股票/ETF: 5 个 → [...]
      指数: 3 个 → [...]
   ```

3. **保持配置简洁** - 只配置需要的符号，系统自动优化：
   ```env
   # 推荐
   STOCK_LIST=SPY,QQQ,VTI,SPX,IXIC
   
   # 不推荐（重复或过多）
   STOCK_LIST=SPY,SPY,QQQ,QQQ,VTI,VTI,SPX,IXIC,DJI,DJI
   ```
