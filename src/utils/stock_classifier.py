# -*- coding: utf-8 -*-
"""
股票/指数分类模块

用途：
  自动识别股票列表中的符号类型，根据数据源兼容性分类

重要提示：
  - Tushare 仅支持 A股（不支持任何美股个股、ETF、指数）
  - YFinance 支持美股个股/ETF/指数
  - 美股个股/ETF（AAPL, SPY, QQQ）无法用 Tushare，仅能用 YFinance

设计：
  1. US_INDEX_SYMBOLS: 美股指数代码集合（SPX, IXIC, DJI 等）
  2. HK_INDEX_SYMBOLS: 港股指数代码集合（HSI, HSCEI 等）
  3. CN_INDEX_SYMBOLS: A股指数代码集合（000001, 000016, 399001 等）
  4. _is_us_stock_code(): 判断是否为美股个股/ETF（1-5位大写字母）
  5. classify_symbol(): 根据代码识别类型 → 返回 (类型, 描述)
  6. separate_stocks_and_indices(): 根据代码列表分离 → 返回 (股票, 指数)
  7. get_tushare_compatible_symbols(): 提取仅 Tushare 兼容的 A股代码
"""

import logging
import re
from typing import List, Set, Tuple

logger = logging.getLogger(__name__)


# 美股指数代码（仅 YFinance 支持）
US_INDEX_SYMBOLS: Set[str] = {
    'SPX',      # 标普500指数
    'IXIC',     # 纳斯达克100指数
    'DJI',      # 道琼斯工业平均指数
    'VIX',      # 波动率指数
}

# 港股指数代码（仅 YFinance 支持）
HK_INDEX_SYMBOLS: Set[str] = {
    'HSI',      # 恒生指数
    'HSCEI',    # 恒生中企指数
}

# A股指数代码（仅 YFinance 或 AKShare 支持）
CN_INDEX_SYMBOLS: Set[str] = {
    '000001',   # 上证指数
    '000016',   # 上证50
    '000300',   # 沪深300
    '000905',   # 中证500
    '399001',   # 深证成指
    '399006',   # 创业板指
    '399300',   # 沪深300
    '399500',   # 中证500
}

# 所有指数的并集
ALL_INDEX_SYMBOLS: Set[str] = US_INDEX_SYMBOLS | HK_INDEX_SYMBOLS | CN_INDEX_SYMBOLS


def _is_us_stock_code(code: str) -> bool:
    """
    判断是否为美股个股/ETF代码
    
    美股代码规则：1-5 个大写字母（可能包含 '.'）
    示例：AAPL, TSLA, SPY, QQQ, BRK.B
    
    参数:
      code: 代码字符串
    
    返回值:
      是否为美股代码
    """
    code = (code or "").strip().upper()
    if code in US_INDEX_SYMBOLS or code in HK_INDEX_SYMBOLS or code in CN_INDEX_SYMBOLS:
      return False
    return bool(re.match(r'^[A-Z]{1,5}(\.[A-Z])?$', code))


def is_index(symbol: str) -> bool:
    """判断符号是否为指数代码"""
    code = (symbol or "").strip().upper()
    return code in ALL_INDEX_SYMBOLS


def classify_symbol(symbol: str) -> Tuple[str, str]:
    """
    分类单个符号
    
    返回值: (类型, 描述)
      - ('index_us', '美股指数 - 仅YFinance')
      - ('index_hk', '港股指数')
      - ('index_cn', 'A股指数')
      - ('stock_us', '美股个股/ETF - 仅YFinance')
      - ('stock_cn_or_hk', 'A股/港股股票 - YFinance/Tushare')
    """
    code = (symbol or "").strip().upper()
    
    if code in US_INDEX_SYMBOLS:
        return ('index_us', f'美股指数: {code} (仅YFinance)')
    if code in HK_INDEX_SYMBOLS:
        return ('index_hk', f'港股指数: {code}')
    if code in CN_INDEX_SYMBOLS:
        return ('index_cn', f'A股指数: {code}')
    
    # 检查是否为美股个股/ETF（不支持 Tushare）
    if _is_us_stock_code(code):
        return ('stock_us', f'美股个股/ETF: {code} (仅YFinance)')
    
    # 其他为 A股或港股股票
    return ('stock_cn_or_hk', f'A股/港股股票: {code}')


def separate_stocks_and_indices(symbols: List[str]) -> Tuple[List[str], List[str]]:
    """
    将符号列表分离为股票/ETF 和指数两类
    
    参数:
      symbols: 符号列表 (如 ['SPY', 'SPX', 'QQQ', 'IXIC'])
    
    返回值:
      (股票_etf列表, 指数列表)
      (如 (['SPY', 'QQQ'], ['SPX', 'IXIC']))
    
    举例:
      >>> separate_stocks_and_indices(['SPY', 'SPX', 'QQQ', 'IXIC', 'VTI', 'DJI'])
      (['SPY', 'QQQ', 'VTI'], ['SPX', 'IXIC', 'DJI'])
    """
    stocks = []
    indices = []
    
    for symbol in symbols:
        code = (symbol or "").strip().upper()
        if not code:
            continue
        
        if is_index(code):
            indices.append(code)
        else:
            stocks.append(code)
    
    return stocks, indices


def get_tushare_compatible_symbols(symbols: List[str]) -> List[str]:
    """
    从列表中提取 Tushare 兼容的符号
    
    重要：Tushare 仅支持 A股（不支持任何美股个股、ETF、指数）
    
    Tushare 支持: A股股票/ETF（如 600519, 510050）
    Tushare 不支持: 美股个股/ETF（AAPL, SPY 等）、任何指数
    
    参数:
      symbols: 符号列表
    
    返回值:
      仅包含 A股股票代码的列表（去除所有指数和美股代码）
    """
    stocks, _ = separate_stocks_and_indices(symbols)
    # 过滤出 A 股代码（6位数字）并排除美股代码（1-5 个大写字母）
    return [s for s in stocks if not _is_us_stock_code(s)]


def get_index_only_symbols(symbols: List[str]) -> List[str]:
    """
    从列表中提取纯指数符号
    
    这些符号只能用 YFinance 取数据，不能用 Tushare
    
    参数:
      symbols: 符号列表
    
    返回值:
      仅包含指数的列表
    """
    _, indices = separate_stocks_and_indices(symbols)
    return indices


def log_classification_summary(symbols: List[str]) -> None:
    """
    打印分类总结日志
    
    参数:
      symbols: 符号列表
    """
    stocks, indices = separate_stocks_and_indices(symbols)
    
    # 进一步分类美股和 A股
    us_stocks = [s for s in stocks if _is_us_stock_code(s)]
    cn_stocks = [s for s in stocks if not _is_us_stock_code(s)]
    us_indices = [i for i in indices if i in US_INDEX_SYMBOLS]
    other_indices = [i for i in indices if i not in US_INDEX_SYMBOLS]
    
    logger.info(f"📊 股票/指数分类结果:")
    logger.info(f"   总数: {len(symbols)}")
    
    if cn_stocks:
        logger.info(f"   A股股票: {len(cn_stocks)} 个 → {cn_stocks} → 数据源: YFinance / Tushare")
    if us_stocks:
        logger.info(f"   美股个股/ETF: {len(us_stocks)} 个 → {us_stocks} → 数据源: YFinance 仅")
    if other_indices:
        logger.info(f"   其他指数: {len(other_indices)} 个 → {other_indices} → 数据源: YFinance / AKShare")
    if us_indices:
        logger.info(f"   美股指数: {len(us_indices)} 个 → {us_indices} → 数据源: YFinance 仅")
    
    # 分析配置
    if not stocks and indices:
        logger.warning("⚠️  仅包含指数，没有股票！建议检查 STOCK_LIST 配置")
    elif not indices and stocks:
        if cn_stocks and not us_stocks:
            logger.info("✅ 仅包含 A股股票，Tushare 兼容")
        elif us_stocks and not cn_stocks:
            logger.info("✅ 仅包含美股，需要 YFinance")
        else:
            logger.info("✅ 混合 A股和美股，已自动分离")
    elif stocks and indices:
        logger.info("✅ 混合配置，已自动分离")
