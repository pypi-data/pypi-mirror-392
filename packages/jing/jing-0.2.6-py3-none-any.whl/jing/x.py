#!/usr/bin/env python
# -*- encoding: utf8 -*-

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

from .data_center import DataCenter
from .stock_reference import Reference
from .rule_container import RuleContainer

from .rule_each import RuleSimple
from .rule_each import RulePriceBreakout

pd.set_option('display.max_columns', None)

class X:
    """
    股票选取器：
    - 支持指定市场、日期、股票代码进行分析
    - 可添加多种规则进行批量或单只股票分析
    - 结果以列表形式存储
    """
    def __init__(self, _market="cn", _date="", _code="") -> None:
        """
        初始化分析器
        :param _market: 市场（如"cn"、"us"）
        :param _date: 分析日期
        :param _code: 股票代码（可选，若为空则分析全市场）
        """
        self.market = _market
        self.date = _date
        self.data_center = DataCenter()  # 数据中心，负责数据获取
        self.rule_map = {}               # 规则映射表，存储已添加的规则
        self.result = []                 # 分析结果列表

        if len(_code) > 0:
            # 若指定单只股票，构造单股票DataFrame
            self.listing = pd.DataFrame({'code':[_code]})
        else:
            # 否则获取全市场股票列表
            self.listing = self.data_center.list(market=_market)

    def get_list(self):
        """返回当前分析的股票列表"""
        return self.listing

    def get_result(self):
        """返回分析结果"""
        return self.result

    def add_rule(self, _rule_class):
        """
        添加分析规则类
        :param _rule_class: 规则类（如RuleSimple）
        """
        #print(f'_rule_class.__name__: {_rule_class.__name__}')
        self.rule_map[_rule_class.__name__] = _rule_class

    def run(self, _lookBack=0):
        """
        批量运行分析，对列表中每只股票执行run_one_stock
        :param _lookBack: 回看天数（暂未用到）
        """
        for i, row in self.listing.iterrows():
            code = row['code']
            print(f"--{code}")
            self.run_one_stock(code, _lookBack)

    def run_one_stock(self, _code, _lookBack=0):
        """
        对单只股票执行分析流程
        :param _code: 股票代码
        :param _lookBack: 回看天数（暂未用到）
        """
        self.one = self.data_center.one(_code, self.date)  # 获取单只股票历史数据
        if len(self.one) < 400:
            # 数据量不足时跳过
            print(f"{_code} -- bye")
            return

        self.ref = Reference(self.one)  # 构建引用对象

        rs = RuleSet(_code, self.ref)   # 构建规则集
        for rule_name, rule_class in self.rule_map.items():
            rs.add_rule(rule_class)     # 添加所有规则
            #print(f"rule[{rule_name}]")
        rs.run()                       # 执行规则集
        results = rs.get_result()      # 获取结果
        if len(results) > 0:
            self.result.append(results)  # 有结果则加入总结果

if __name__=="__main__":
    # 用法示例：
    # x = X("us", "2023-10-30")

    # ma50 - ma200
    # x = X("us", "2023-10-30", "NFLX")
    # x = X("us", "2023-11-01", "AMD")
    # x.run()

    # breakout +
    # x = X("us", "2024-01-19", "SMCI") # breakout

    # x = X("us", "2023-05-24", "ANF", "volumeBreakout")
    # x = X("us", "2024-01-19", "SMCI", "volumeBreakout")
    # x.run()
    #x = X("us", "2024-02-16")

    #x = X("us", "2024-05-25")
    #x.run(5)

    # x = X("us", "2024-09-27", "IONQ")
    # x.add_rule(RuleSimple)
    # x.run()

    # x = X("us", "2024-09-27")
    # x.add_rule(RuleSimple)
    # x.run()

    # 当前示例：对美股2024-01-19的SMCI股票，应用两个规则
    x = X("us", "2024-01-19", "SMCI")
    x.add_rule(RulePriceBreakout)  # 添加价格突破规则
    x.add_rule(RuleSimple)         # 添加简单规则
    x.run()                       # 执行分析
    print(x.result)               # 输出结果

