# -*- coding: utf-8 -*-
"""
测试 stock_classifier 模块的功能
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.stock_classifier import (
    is_index,
    classify_symbol,
    separate_stocks_and_indices,
    get_tushare_compatible_symbols,
    get_index_only_symbols,
    US_INDEX_SYMBOLS,
    HK_INDEX_SYMBOLS,
    CN_INDEX_SYMBOLS,
)

class TestStockClassifier(unittest.TestCase):
    """测试股票分类模块"""

    def test_us_indices_recognized(self):
        """测试美股指数识别"""
        for symbol in US_INDEX_SYMBOLS:
            self.assertTrue(is_index(symbol), f"{symbol} should be recognized as index")

    def test_hk_indices_recognized(self):
        """测试港股指数识别"""
        for symbol in HK_INDEX_SYMBOLS:
            self.assertTrue(is_index(symbol), f"{symbol} should be recognized as index")

    def test_cn_indices_recognized(self):
        """测试A股指数识别"""
        for symbol in CN_INDEX_SYMBOLS:
            self.assertTrue(is_index(symbol), f"{symbol} should be recognized as index")

    def test_stocks_not_recognized_as_indices(self):
        """测试股票不被认为是指数"""
        stocks = ['SPY', 'AAPL', 'MSFT', 'QQQ', 'VTI', '600519', '000001']
        # Note: 000001 is in CN_INDEX_SYMBOLS, so it IS an index
        non_indices = ['SPY', 'AAPL', 'MSFT', 'QQQ', 'VTI', '600519']
        for stock in non_indices:
            self.assertFalse(is_index(stock), f"{stock} should NOT be recognized as index")

    def test_classify_us_index(self):
        """测试美股指数分类"""
        result = classify_symbol('SPX')
        self.assertEqual(result[0], 'index_us')
        self.assertIn('美股指数', result[1])

    def test_classify_stock(self):
        """测试股票分类"""
        result = classify_symbol('AAPL')
        self.assertEqual(result[0], 'stock_or_etf')
        self.assertIn('股票/ETF', result[1])

    def test_separate_mixed_list(self):
        """测试分离混合列表"""
        symbols = ['SPY', 'SPX', 'QQQ', 'IXIC', 'AAPL', 'DJI']
        stocks, indices = separate_stocks_and_indices(symbols)
        
        self.assertEqual(set(stocks), {'SPY', 'QQQ', 'AAPL'})
        self.assertEqual(set(indices), {'SPX', 'IXIC', 'DJI'})

    def test_separate_only_stocks(self):
        """测试仅有股票的列表"""
        symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT']
        stocks, indices = separate_stocks_and_indices(symbols)
        
        self.assertEqual(set(stocks), set(symbols))
        self.assertEqual(len(indices), 0)

    def test_separate_only_indices(self):
        """测试仅有指数的列表"""
        symbols = ['SPX', 'IXIC', 'DJI']
        stocks, indices = separate_stocks_and_indices(symbols)
        
        self.assertEqual(len(stocks), 0)
        self.assertEqual(set(indices), set(symbols))

    def test_get_tushare_compatible(self):
        """测试获取 Tushare 兼容符号"""
        symbols = ['SPY', 'SPX', 'QQQ', 'IXIC', 'AAPL']
        result = get_tushare_compatible_symbols(symbols)
        
        self.assertEqual(set(result), {'SPY', 'QQQ', 'AAPL'})
        self.assertNotIn('SPX', result)
        self.assertNotIn('IXIC', result)

    def test_get_index_only(self):
        """测试获取纯指数符号"""
        symbols = ['SPY', 'SPX', 'QQQ', 'IXIC', 'AAPL', '000001', '399001']
        result = get_index_only_symbols(symbols)
        
        # 000001 and 399001 are CN indices
        self.assertEqual(set(result), {'SPX', 'IXIC', '000001', '399001'})
        self.assertNotIn('SPY', result)
        self.assertNotIn('QQQ', result)
        self.assertNotIn('AAPL', result)

    def test_case_insensitive(self):
        """测试大小写不敏感"""
        self.assertTrue(is_index('spx'))
        self.assertTrue(is_index('SpX'))
        self.assertTrue(is_index('SPX'))

    def test_whitespace_handling(self):
        """测试空格处理"""
        result = classify_symbol('  AAPL  ')
        self.assertEqual(result[0], 'stock_or_etf')

    def test_empty_symbol(self):
        """测试空符号"""
        result = classify_symbol('')
        self.assertEqual(result[0], 'stock_or_etf')

    def test_mixed_market_separation(self):
        """测试混合市场分离"""
        # Mix of US stocks, US indices, A-share stocks, A-share indices
        symbols = ['SPY', 'SPX', 'AAPL', 'IXIC', '600519', '000001', '399001']
        stocks, indices = separate_stocks_and_indices(symbols)
        
        # 000001 and 399001 are indices
        self.assertEqual(set(stocks), {'SPY', 'AAPL', '600519'})
        self.assertEqual(set(indices), {'SPX', 'IXIC', '000001', '399001'})


if __name__ == '__main__':
    unittest.main()
