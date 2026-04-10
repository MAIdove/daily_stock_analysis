# -*- coding: utf-8 -*-
"""
股票/指数分类模块

用途：
  自动识别股票列表中的股票/ETF（可用 Tushare）和指数（仅用 YFinance）
  根据不同类型使用合适的数据源，避免混淆导致的错误

设计：
  1. US_INDEX_SYMBOLS: 美股指数代码集合（SPX, IXIC, DJI 等）
  2. HK_INDEX_SYMBOLS: 港股指数代码集合（HSI, HSCEI 等）
  3. CN_INDEX_SYMBOLS: A股指数代码集合（000001, 000016, 399001 等）
  4. classify_symbol(): 根据代码识别类型 → 返回 (类型, 描述)
  5. separate_stocks_and_indices(): 根据代码列表分离 → 返回 (股票, 指数)
"""

import logging
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


def is_index(symbol: str) -> bool:
    """判断符号是否为指数代码"""
    code = (symbol or "").strip().upper()
    return code in ALL_INDEX_SYMBOLS


def classify_symbol(symbol: str) -> Tuple[str, str]:
    """
    分类单个符号
    
    返回值: (类型, 描述)
      - ('index_us', '美股指数')
      - ('index_hk', '港股指数')
      - ('index_cn', 'A股指数')
      - ('stock_or_etf', '股票或ETF - 需用 Tushare/YFinance')
    """
    code = (symbol or "").strip().upper()
    
    if code in US_INDEX_SYMBOLS:
        return ('index_us', f'美股指数: {code}')
    if code in HK_INDEX_SYMBOLS:
        return ('index_hk', f'港股指数: {code}')
    if code in CN_INDEX_SYMBOLS:
        return ('index_cn', f'A股指数: {code}')
    
    return ('stock_or_etf', f'股票/ETF: {code}')


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
    从列表中提取 Tushare 兼容的符号（股票/ETF）
    
    Tushare 支持: 股票/ETF（如 AAPL, SPY）
    Tushare 不支持: 指数（如 SPX, IXIC, DJI）
    
    参数:
      symbols: 符号列表
    
    返回值:
      仅包含股票/ETF 的列表（去除所有指数）
    """
    stocks, _ = separate_stocks_and_indices(symbols)
    return stocks


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
    
    logger.info(f"📊 股票/指数分类结果:")
    logger.info(f"   总数: {len(symbols)}")
    logger.info(f"   股票/ETF: {len(stocks)} 个 → {stocks} → 数据源: YFinance / Tushare")
    logger.info(f"   指数: {len(indices)} 个 → {indices} → 数据源: YFinance 仅")
    
    if not stocks and indices:
        logger.warning("⚠️  仅包含指数，没有股票！建议检查 STOCK_LIST 配置")
    elif not indices and stocks:
        logger.info("✅ 仅包含股票/ETF，Tushare 兼容")
    elif stocks and indices:
        logger.info("✅ 混合配置，已自动分离")
