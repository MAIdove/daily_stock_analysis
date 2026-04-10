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


# 导入内部函数进行测试
from src.utils.stock_classifier import _is_us_stock_code

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
        self.assertEqual(result[0], 'stock_us')
        self.assertIn('美股', result[1])

    def test_classify_us_stock(self):
        """测试美股分类"""
        for stock in ['SPY', 'QQQ', 'AAPL', 'VTI', 'VGT', 'XLK']:
            result = classify_symbol(stock)
            self.assertEqual(result[0], 'stock_us', f"{stock} should be classified as 美股")
            self.assertIn('美股', result[1])

    def test_is_us_stock_code(self):
        """测试美股代码识别"""
        # 正确的美股代码
        us_codes = ['SPY', 'AAPL', 'MSFT', 'QQQ', 'VTI', 'BRK.B', 'BRK.A', 'F']
        for code in us_codes:
            self.assertTrue(_is_us_stock_code(code), f"{code} should be recognized as US stock code")
        
        # 不是美股代码
        non_us_codes = ['600519', '000001', 'SPX', 'IXIC', 'DJI', '']
        for code in non_us_codes:
            self.assertFalse(_is_us_stock_code(code), f"{code} should NOT be recognized as US stock code")

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
        
        self.assertEqual(set(result), set())
        self.assertNotIn('SPX', result)
        self.assertNotIn('IXIC', result)

    def test_tushare_excludes_us_stocks(self):
        """测试 Tushare 排除所有美股（包括个股和 ETF）"""
        # 美股个股和 ETF 不应该在 Tushare 兼容列表中
        symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'VTI', 'VGT', 'XLK', '600519', '510050']
        result = get_tushare_compatible_symbols(symbols)
        
        # 仅 A股应该在列表中
        self.assertEqual(set(result), {'600519', '510050'})
        for us_stock in ['SPY', 'QQQ', 'AAPL', 'MSFT', 'VTI', 'VGT', 'XLK']:
            self.assertNotIn(us_stock, result, f"{us_stock} should NOT be in Tushare compatible list")
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
        self.assertEqual(result[0], 'stock_us')

    def test_empty_symbol(self):
        """测试空符号"""
        result = classify_symbol('')
        self.assertEqual(result[0], 'stock_cn_or_hk')

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
