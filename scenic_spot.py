#!/usr/bin/env python3
#-*- coding:utf-8 -*-
# author:mirco
# datetime:2019/6/18 21:24
# software: PyCharm

#找到一个城市最有趣的地方

#思维逻辑

#1.解析“去哪儿”网站景点网址，找出迭代或循环爬取的方法机制

#2.函数式编程实现：1）自动获取爬取url 2）获取指定页面的源数据 3）对源数据进行结构化处理提取目标元素 4）清洗和整理元素


import requests
from bs4 import BeautifulSoup
import pandas as pd
import  numpy as np

#函数编程

#1.定义获取前N页的url
def get_urls(url,n):
    urllst = []
    for i in range(1,n+1):
        urllst.append(url+str(i))
    return urllst

#2.获取源数据并解析提取目标元素
def get_data(urli):
    r = requests.get(urli)
    soup = BeautifulSoup(r.text, 'lxml')
    ul = soup.find('ul', class_="list_item clrfix")      #获取包含当前页面信息list的块，并返回字符串类型
    li = ul.find_all('li')      #从ul块下钻到li每个景点list,并返回对象是列表

    datai = []
    n = 0
    #循环获取li景点列表中的单个景点信息并提取
    for i in li:
        n += 1
        # print(i.text)
        dic = {}
        dic['lat'] = i['data-lat']
        dic['lng'] = i['data-lng']
        dic['景点名称'] = i.find('span', class_="cn_tit").text
        dic['攻略提到数量'] = i.find('div', class_="strategy_sum").text
        dic['点评数量'] = i.find('div', class_="comment_sum").text
        dic['景点排名'] = i.find('span', class_="ranking_sum").text
        dic['星级'] = i.find('span', class_="total_star").find('span')['style'].split(':')[1]
        datai.append(dic)
    return datai

#3.构建函数实现字段标准化
def nordata(dfi,*cols):
    for col in cols:
        dfi[col + '_nor'] = (dfi[col] - dfi[col].min())/(dfi[col].max() - dfi[col].min())

def main():
    #调用get_urls得到网址列表
    urllsti = get_urls('https://travel.qunar.com/p-cs299937-%s-jingdian-1-'%'suzhou',10)
    jd_data = []
    for i in urllsti:
        jd_data.extend(get_data(i))
        print('成功采集%i'%len(jd_data))

    #数据清洗，输出
    df = pd.DataFrame(jd_data)

    # 1.字段类型处理
    df.index = df['景点名称']
    del df['景点名称']
    df['lng'] = df['lng'].astype(np.float)
    df['lat'] = df['lat'].astype(np.float)
    df['点评数量'] = df['点评数量'].astype(np.int)
    df['攻略提到数量'] = df['攻略提到数量'].astype(np.int)

    # 2.星级字段处理
    df['星级'] = df['星级'].str.replace('%', '').astype(np.float)

    # 3.景点排名处理
    df['景点排名'] = df['景点排名'].str.split('第').str[1]
    df['景点排名'].fillna(value=0, inplace=True)

    #4.满意度
    df['满意度'] = df['攻略提到数量']/df['点评数量']

    #4.构建指标体系做评价-景点筛选机制和评价方法：如-满意度指标
    #指标体系：可观评价：评分字段标准化；人气指标-点评数量字段，标准化；满意度指标：攻略数量/点评数量，标准化
    nordata(df, '满意度', '星级', '点评数量')

    #df['满意度'] = df['攻略提到数量'] / df['点评数量']
    #标准化：量级不同，去纲量化0-1标准化
    #df['满意度_nor'] = (df['满意度'] - df['满意度'].min()) / (df['满意度'].max() - df['满意度'].min())

    print(df.head())
    df.to_excel(r'C:\Users\mirco\Desktop\test.xls',sheet_name='Sheet1',na_rep='')

if __name__ == '__main__':
    main()