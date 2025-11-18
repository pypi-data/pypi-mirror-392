#!/usr/bin/env python
# -*- encoding: utf8 -*-

from .data_center import DataCenter
from .stock_reference import Reference

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

pd.set_option('display.max_columns', None)

class Y:
    """
    股票单只分析类：
    - 支持指定股票代码、日期、市场进行数据加载
    - 便于直接获取Reference对象进行各类指标分析
    """
    def __init__(self, code, _date="", _market="us") -> None:
        """
        初始化分析器
        :param code: 股票代码
        :param _date: 分析日期
        :param _market: 市场（默认美股us）
        """
        self.market = _market
        self.date = _date
        self.code = code

        self.data_center = DataCenter(self.market)  # 数据中心，负责数据获取
        self.df = self.data_center.one(self.code, self.date)  # 获取单只股票历史数据
        self.ref = Reference(self.df)  # 构建引用对象，便于后续指标分析

if __name__=="__main__":
    # 用法示例：分析IONQ股票在2024-09-27的各类指标
    y = Y("IONQ", _date="2024-09-27")
    ref = y.ref
    # 输出指定日期的各类技术指标
    print(ref.date(0), ref.ma20(0), ref.ma50(0), ref.ma200(0), ref.vma50(0), ref.macd(0), ref.diff(0), ref.dea(0))
