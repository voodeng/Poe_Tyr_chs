import os
import sys
import xml.etree.ElementTree as ET

import pandas as pd
import numpy as np
import openpyxl
import xlrd
import datetime

from config import *
from lib import *
'''
对多语合并文件打补丁ha
'''

m_key = 'merged'
f_key = 'merged_female'


def e2df(file):
    df = pd.read_excel(file).fillna('')

    try:
        df = df.set_index('index')
    except:
        df.index = [df['Name'] + '_' + df['ID'].astype('str')]
        df.index.name = 'index'

    # 清除重复索引
    df = df[~df.index.duplicated()] # 原有基础上改，不会重排序索引
    # idx = np.unique(df.index, return_index=True)[1]
    # df = df.ix[idx]
    return df


def initxdf(targe_file, custom_file):
    ldf = e2df(targe_file)
    xdf = ldf.copy()

    if os.path.exists(custom_file):
        cdf = e2df(custom_file)
        xdf = xdf.join(cdf[['Custom', 'Custom_female']], how='left').fillna('')
    else:
        xdf[m_key] = ''
        xdf[f_key] = ''

    print(xdf.index)
    print('Start fix and Comprese file')
    print('Targe file: ' + targe_file)
    print('Custom file: ' + custom_file)
    return xdf


# 遍历行，按相应方式合并到 merged cell
def new_merge(xdf):
    print('merge cell hadle')
    merges = []
    merges_female = []

    for i, row in xdf.iterrows():
        new_cell = row['DefaultText']
        new_f_cell = row['FemaleText']

        if row['Custom'] != '':
            new_cell = row['Custom']
        if row['Custom_female'] != '':
            new_f_cell = row['Custom_female']

        for k in translated_result_list[TYPE_NAME]:
            dk = '[{n}]DefaultText'.format(n=k['group_name'])
            fk = '[{n}]FemaleText'.format(n=k['group_name'])

            d_text = row[dk]
            f_text = row[fk]

            if has_ch(d_text) and row['Custom'] == '':
                new_cell = d_text
                break
            if has_ch(f_text) and row['Custom_female'] == '':
                new_f_cell = f_text
                break

        merges.append(new_cell)
        merges_female.append(new_f_cell)

    xdf[m_key] = merges
    xdf[f_key] = merges_female
    return xdf


def patch_result_list(patch_filename):
    # 读取替换表，并依照表格顺序，依次转化为df并有序添加到array中
    book = openpyxl.load_workbook(patch_filename)

    tr_list = {}  # 无序
    tr2_list = []  # 有序 [{'name':工作表名,'data':工作表DF数据}]

    for sheet in book:
        # print(sheet.title)
        _sn = sheet.title
        pr = pd.read_excel(patch_filename, sheetname=_sn).fillna('')
        tr2_list.append({'name': _sn, 'data': pr})
        tr_list[_sn] = pr

    print(u'替换表读取完毕')
    return tr2_list


# glossary 名词表替换
def gloss_patch(Series, file):
    print('replace golssary use: {f}'.format(f=file))

    gloss_list = pd.read_excel(file).fillna('')

    en_key = 'Eng'
    chs_key = 'Chs'
    oth_key = 'Rep'
    # code key
    reg = '\[url=glossary:(.*?)\]'
    gloss_list['code'] = gloss_list[en_key].str.extract(reg, expand=False)
    gloss_list['chs_code'] = gloss_list[chs_key].str.extract(
        '\[url=.*?\](.*?)(?=\[/url\])', expand=False)
    gloss_list = gloss_list.fillna('')
    # gloss_list.ix[57]

    for i, row in gloss_list.iterrows():
        if row[chs_key] != '':
            re = '(\[url=glossary:' + row['code'] + '\].*?\[/url\])'
            repl = '[url=glossary:{chs}]{chs}[/url]'.format(
                chs=row['chs_code'])
            # print('repl: ' + re + ' to ' + repl)
            Series = Series.str.replace(re, repl)
            if row[oth_key] != '':
                for k in row[oth_key].split(','):
                    re2 = '(\[url=glossary:' + k + '\].*?\[/url\])'
                    # print('repl2: ' + re2 + ' to ' + repl)
                    Series = Series.str.replace(re2, repl)
    return Series


# name 替换
def name_list(Series, file):
    begin = datetime.datetime.now()
    print('replace name use: {f}'.format(f=file))
    # new_ser = Series.copy()

    book = openpyxl.load_workbook(file)
    tr_list = {}
    for sheet in book:
        # print('read patch list:' + sheet.title)
        _sn = sheet.title
        pr = pd.read_excel(file, sheetname=_sn).fillna('')
        tr_list[_sn] = pr

    for x in tr_list:
        print('apply patch:' + x)
        # _rep(tr_list[x])
        for i, row in tr_list[x].iterrows():
            if row['Chs'] != '' and row['Rep'] != '':
                am = row['Rep'].split(',')
                if row['Eng'] != '':
                    am.append(row['Eng'])

                for k in am:
                    k = k.replace('[', '\\[').replace(']', '\\]')
                    Series = Series.str.replace(''.join(k), row['Chs'])

    end = datetime.datetime.now()
    print('Time: {s}'.format(s = end - begin))
    return Series


# fix ->
def gui_patch(Series, file):
    print('patch gui')
    patch_list = e2df(file)

    new_s = Series.copy()
    for i, row in patch_list.iterrows():
        if row['Custom'] != '':
            new_s[i] = row['Custom']
    return new_s


# tmdf is DataFrame
def rep_name(df, file, type):
    begin = datetime.datetime.now()

    tmdf = df.copy()

    def tuidao(pre):
        chs = pre['Chs']
        eng = pre['Eng']
        rep = pre['Rep'].split(',')
        r_count = 0
        if chs == '' or chs is None:
            return

        # way 先搜索对应的英文
        def rep1():
            items = tmdf[tmdf['DefaultText'].str.contains(eng, case=False)]
            for i, row in items.iterrows():
                if len(rep) < 2:
                    row[m_key] = row[m_key].replace(rep[0], chs)
                    if row['FemaleText'] != '':
                        # 使男女用一样的对话，不区分 - -'
                        row[f_key] = row[m_key]
                else:
                    for k in rep:
                        row[m_key] = row[m_key].replace(k, chs)
                        if row['FemaleText'] != '':
                            row[f_key] = row[m_key]
                tmdf.ix[i, [m_key, f_key]] = [row[m_key], row[f_key]]

        # 列Rep
        def rep2():
            for k in rep:
                k = k.replace('[', '\\[').replace(']', '\\]')
                tmdf[m_key] = tmdf[m_key].str.replace(''.join(k), row['Chs'])
                tmdf[f_key] = tmdf[f_key].str.replace(''.join(k), row['Chs'])


        print('{co} replaced: {e} {s} ==> {b}'.format(
            co='', e=eng, s=rep, b=chs))

        if type == 2:
            rep2() # 2m20s
        if type == 1:
            rep1() # 4m12s

    tr2_list = patch_result_list(file)

    for x in tr2_list:
        print('apply patch: ' + x['name'])
        data = x['data']
        for index, row in data.iterrows():
            if row['Rep'] == '' or row['Rep'] is None or row[
                    'Chs'] == '' or row['Chs'] is None:
                continue
            else:
                tuidao(row)

    end = datetime.datetime.now()
    print('Time: {s}'.format(s = end - begin))
    return tmdf


def wrquote(xdf):
    print('wrong quote')
    # 不对称或缺失引号，fix_text 处理后，未对称的引号会使用全角符号，方便查找
    # ＇ ＂
    doub = xdf[xdf[m_key].str.contains('＂.*?')]
    sign = xdf[xdf[m_key].str.contains('＇.*?')]
    tign = pd.merge(doub, sign, how='outer')
    tign.index = [tign['Name'] + '_' + tign['ID'].astype('str')]
    tign[['Name', 'ID', 'DefaultText', m_key]].to_excel(
        os.path.join(TEMP_DIR, 'quote.xlsx'), index_label='index')

    # 后期依次修改，先期转换为英文标点使用
    xdf[m_key] = xdf[m_key].str.replace('＂', '"')
    xdf[m_key] = xdf[m_key].str.replace('＇', "'")


def begin():
    import timeit

    target_file = merge_result_output_filename

    if TYPE_NAME == 'Tyranny':
        custom_file = os.path.join(STORAGE_DIR, 'Tyr_custom.xlsx')
    else:
        custom_file = os.path.join(STORAGE_DIR, 'Poe_en-chs.xlsx')

    xdf = initxdf(target_file, custom_file)

    xdf = new_merge(xdf)

    if TYPE_NAME == 'Tyranny':
        # 未翻译的行
        def not_ch(text):
            return not has_ch(text)

        xdf[xdf[m_key].apply(not_ch)].drop_duplicates(m_key).to_excel(
            os.path.join(TEMP_DIR, 'notrans.xlsx'))

        xdf[m_key] = gloss_patch(
            xdf[m_key], os.path.join(STORAGE_DIR,
                                     'Tyr_gloss.xlsx')).apply(fix_text)
        xdf[f_key] = gloss_patch(
            xdf[f_key], os.path.join(STORAGE_DIR,
                                     'Tyr_gloss.xlsx')).apply(fix_text)

        # 测下时间
        xdf[m_key] = name_list(xdf[m_key],
                               os.path.join(STORAGE_DIR, 'Tyr_name.xlsx'))
        xdf[f_key] = name_list(xdf[f_key],
                               os.path.join(STORAGE_DIR, 'Tyr_name.xlsx'))

        xdf[m_key] = gui_patch(xdf[m_key],
                               os.path.join(STORAGE_DIR, 'Tyr_guifix.xlsx'))

        # 标点
        wrquote(xdf)

        # 生成处理后的文件，只包含merged cell
        final_file = os.path.join(TEMP_DIR, 'Tyr_final.xlsx')
        print('out:' + final_file)
        xdf[[m_key, f_key]].to_excel(final_file, index_label='index')
        # 参考用
        xdf.to_excel(os.path.join(TEMP_DIR, 'Tyr_tempcustom.xlsx'))
    elif TYPE_NAME == 'Poe':
        xdf[m_key] = xdf[m_key].apply(fix_text)
        xdf[f_key] = xdf[f_key].apply(fix_text)

        # xdf = rep_name(xdf, os.path.join(STORAGE_DIR, 'Poe_name.xlsx', 1))

        # xdf[m_key] = gui_patch(xdf[m_key],
        #                        os.path.join(STORAGE_DIR, 'Poe_fix.xlsx'))

        final_file = os.path.join(TEMP_DIR, TYPE_NAME + '_final.xlsx')
        print('out:' + final_file)
        xdf[[m_key, f_key]].to_excel(final_file, index_label='index')
        # 参考用
        xdf.to_excel(os.path.join(TEMP_DIR, TYPE_NAME + '_tempcustom.xlsx'))
    else:
        print('Config error')


if __name__ == '__main__':
    begin()
