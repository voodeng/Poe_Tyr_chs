import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
import openpyxl
import pandas as pd
import xlrd

from config import *


# 使用自定的名词表打补丁
# 分词，用 ' - '  两边带有空格
# merged_result = os.path.join(HOME_DIR, OUTPUT_DIR, u"trans_use.xlsx")
patch_result = patch_filename

xmdf = pd.read_excel(merge_result_output_filename).fillna('')
tmdf = xmdf.copy()

def _map(data):
    print('===strat replace')
    for index, row in data.iterrows():   # 获取每行的index、row
        if row['Rep'] == '' or row['Rep'] is None or row['Chs'] == '' or row['Chs'] is None:
            continue
        else:
            tuidao(row)
    print('===patch end')
    return data

def _fix(data):
    print('===strat fix')
    for index, row in data.iterrows():   # 获取每行的index、row
        if row['Chs'] == '' or row['Chs'] is None:
            continue
        else:
            im = tmdf[(tmdf['Name']==row['Name']) & (tmdf['ID']==row['ID'])].index
            tmdf.ix[im,'Custom'] = row['Chs']
#             tmdf.ix[ tmdf[tmdf['Name']==row['Name']].iloc[row['ID']]['Refer'],'Custom' ] = row['Chs']
    print('===patch end')
    return data

def tuidao(pre):
    chs = pre['Chs']
    eng = pre['Eng']
    rep = pre['Rep'].split(',')
    r_count = 0
    if chs == '' or chs is None:
        return
    items = tmdf[tmdf['DefaultText'].str.contains(eng, case=False)]

    for i,row in items.iterrows():
        if len(rep) < 2:
            row['Custom'] = row['Custom'].replace(rep[0],chs)
        else:
            for k in rep:
                row['Custom'] = row['Custom'].replace(k,chs)
        r_count +=1
        tmdf.ix[i,'Custom'] = row['Custom']
    print('{co} replaced: {e} {s} ==> {b}'.format(co = r_count, e=eng, s = rep, b = chs))


def patch():

    # 检测英文相等部分 > 检测翻译部分类同部分 > 替换为指定表格的文字
    # mr[mr['DefaultText'].str.contains('Engwithan')]
    # 需要遍历 DataFrame 所有行

    book = openpyxl.load_workbook(patch_filename)
    tr_list = {}
    for sheet in book:
        print('read patch list:' + sheet.title)
        _sn = sheet.title
        pr = pd.read_excel(patch_filename,sheetname=_sn).fillna('')
        tr_list[_sn]=pr

    for x in tr_list:
        if x == 'fix':
            _fix(tr_list[x])
        else:
            _map(tr_list[x])

    tmdf.to_excel(merge_patched,index=False)
    print(merge_patched)
    print('===== file patched and out')

patch()
