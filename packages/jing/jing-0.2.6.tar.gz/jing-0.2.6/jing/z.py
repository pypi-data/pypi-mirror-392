#!/usr/bin/env python
# -*- encoding: utf8 -*-
"""
股票数据下载统一接口
支持多个市场的股票数据下载：
- us: 美股市场，使用 Yahooer 下载器
- hk: 港股市场，使用 AKER 下载器
- cn: 中国A股市场，使用 BAOSTOCK 下载器
"""

    # 作为模块导入时使用相对导入
from .downloader_yahooer import Yahooer
from .downloader_aker import AKER
from .downloader_baostock import BAOSTOCK

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

# 设置 pandas 显示所有列
pd.set_option('display.max_columns', None)

class Z:
    """
    股票数据下载统一接口类
    
    根据不同的市场类型自动选择对应的数据下载器：
    - 美股(us): 使用 Yahooer
    - 港股(hk): 使用 AKER
    - A股(cn): 使用 BAOSTOCK
    """
    
    def __init__(self, _market="us") -> None:
        """
        初始化下载器
        
        参数:
            _market (str): 市场类型，可选值：
                - 'us': 美股市场（默认）
                - 'hk': 港股市场
                - 'cn': 中国A股市场
                其他值默认使用美股下载器
        """
        self.market = _market
        
        # 根据市场类型选择对应的下载器
        if self.market == 'us':
            # 美股使用 Yahooer 下载器
            self.inst = Yahooer()
        elif self.market == 'hk':
            # 港股使用 AKER 下载器
            self.inst = AKER(self.market)
        elif self.market == 'cn':
            # A股使用 BAOSTOCK 下载器
            self.inst = BAOSTOCK(self.market)
        else:
            # 默认使用美股下载器
            self.inst = Yahooer()

    def download(self, _code=""):
        """
        下载股票数据
        
        参数:
            _code (str): 股票代码
                - 如果提供代码，则下载指定股票的数据
                - 如果为空字符串，则批量下载列表中的所有股票
        
        示例:
            # 下载单只股票
            z.download("PLTR")      # 美股
            z.download("600863")    # A股
            
            # 批量下载
            z.download()            # 下载列表中的所有股票
        """
        self.code = _code
        
        if len(_code) > 0:
            # 下载指定股票代码的数据
            self.inst.getK(self.code)
        else:
            # 批量下载列表中的所有股票
            self.inst.getKFromList()

if __name__=="__main__":
    # 使用示例
    
    # 美股下载示例
    # z = Z()
    # z.download("PLTR")
    
    # A股下载示例
    z2 = Z(_market='cn')
    #z2.download('sh.600863')
    z2.download()