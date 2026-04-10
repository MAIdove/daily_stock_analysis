# 📊 股票/指数快速分类参考

## 问题解决

**之前的问题：** Tushare 不支持指数数据，导致混合配置时出错

**解决方案：** ✅ 系统已自动分离，根据类型选择数据源

---

## 配置方法

### 最简单的方式 - 直接混合配置

```env
# 在 .env 中，可以直接混合配置，无需分离！
STOCK_LIST=SPY,QQQ,VTI,VGT,XLK,SPX,IXIC,DJI
```

系统会自动识别并处理：
- ✅ **美股个股/ETF**（SPY, QQQ, VTI, VGT, XLK） → 数据源：YFinance 仅
- ✅ **指数**（SPX, IXIC, DJI） → 数据源：YFinance 仅

---

## 支持的指数代码

### 美股指数
| 代码 | 名称 | 数据源 |
|------|------|--------|
| `SPX` | 标普500指数 | YFinance |
| `IXIC` | 纳斯达克100指数 | YFinance |
| `DJI` | 道琼斯工业平均指数 | YFinance |
| `VIX` | 波动率指数 | YFinance |

### 港股指数
| 代码 | 名称 | 数据源 |
|------|------|--------|
| `HSI` | 恒生指数 | YFinance |
| `HSCEI` | 恒生中企指数 | YFinance |

### A股指数
| 代码 | 名称 | 数据源 |
|------|------|--------|
| `000001` | 上证指数 | YFinance / AKShare |
| `000016` | 上证50 | YFinance / AKShare |
| `000300` | 沪深300 | YFinance / AKShare |
| `000905` | 中证500 | YFinance / AKShare |
| `399001` | 深证成指 | YFinance / AKShare |
| `399006` | 创业板指 | YFinance / AKShare |

---

## 配置示例

### 示例 1: 纯美股 ETF + 指数
```env
STOCK_LIST=SPY,QQQ,VTI,VGT,XLK,SPX,IXIC,DJI
```
**分类结果：**
- 美股个股/ETF: 5 个 (SPY, QQQ, VTI, VGT, XLK)
- 指数: 3 个 (SPX, IXIC, DJI)

### 示例 2: 混合 A股股票 + 美股 ETF
```env
STOCK_LIST=600519,000001,SPY,QQQ,SPX,IXIC
```
**分类结果：**
- A股股票: 1 个 (600519)
- 美股个股/ETF: 2 个 (SPY, QQQ)
- 指数: 3 个 (000001, SPX, IXIC)

### 示例 3: 仅指数（用于市场复盘）
```env
STOCK_LIST=SPX,IXIC,DJI,000001,000300
```
**分类结果：**
- 股票/ETF: 0 个
- 指数: 5 个 (全部)

---

## 运行日志

每次运行时，系统会输出分类摘要：

```
📊 股票/指数分类结果:
   总数: 8
   美股个股/ETF: 5 个 → ['SPY', 'QQQ', 'VTI', 'VGT', 'XLK'] → 数据源: YFinance 仅
   美股指数: 3 个 → ['SPX', 'IXIC', 'DJI'] → 数据源: YFinance 仅
✅ 混合配置，已自动分离
```

---

## 常见问题

### Q: 指数数据从哪来？
**A:** YFinance。无需配置，系统自动处理。

### Q: 为什么还要配置 Tushare Token？
**A:** 用于 A 股股票/ETF 的增强数据（如筹码分布），美股与指数不走 Tushare。

### Q: 能否只分析指数？
**A:** 可以，系统会跳过 Tushare 初始化，仅用 YFinance。

### Q: 能否添加新指数？
**A:** 可以。编辑 `src/utils/stock_classifier.py` 的 `US_INDEX_SYMBOLS` 等集合。

---

## 技术细节

### 分类优先级
1. **检查美股指数** - 在 `US_INDEX_SYMBOLS` 中？
2. **检查港股指数** - 在 `HK_INDEX_SYMBOLS` 中？
3. **检查A股指数** - 在 `CN_INDEX_SYMBOLS` 中？
4. **检查是否美股代码** - 是则归类为美股个股/ETF（YFinance）
5. **其他** - 视为 A股/港股股票

### 代码示例
```python
from src.utils.stock_classifier import separate_stocks_and_indices

symbols = ['SPY', 'SPX', 'QQQ', 'IXIC']
stocks, indices = separate_stocks_and_indices(symbols)
# 结果: (
#   ['SPY', 'QQQ'],  # 股票/ETF
#   ['SPX', 'IXIC']  # 指数
# )
```

---

## 相关文档

- 完整指南：[STOCK_CLASSIFICATION_GUIDE.md](../docs/STOCK_CLASSIFICATION_GUIDE.md)
- 模块代码：[stock_classifier.py](../src/utils/stock_classifier.py)
- 单元测试：[test_stock_classifier.py](../tests/test_stock_classifier.py)
