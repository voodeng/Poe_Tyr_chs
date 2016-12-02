import os
import sys
import xml.etree.ElementTree as ET

import pandas as pd
import numpy as np
import openpyxl
import xlrd

from config import *
from lib import *
'''
对多语合并文件打补丁ha
'''

m_key = 'merged'
f_key = 'merged_female'


def initxdf(targe_file, custom_file):
    targe_file = targe_file
    ldf = pd.read_excel(targe_file, index_col=[0])

    if os.path.exists(custom_file):
        cdf = pd.read_excel(custom_file, index_col=[0])
        xdf = ldf.join(cdf[['Custom', 'Custom_female']]).fillna('')
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


# glossary 名词表替换
def gloss_patch(Series, file):
    print('replace golssary use: {f}'.format(f=file))

    gloss_list = pd.read_excel(file).fillna('')

    en_key = 'en'
    chs_key = 'chs'
    oth_key = 'oth'
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
    print('replace name use: {f}'.format(f=file))
    new_ser = Series.copy()

    book = openpyxl.load_workbook(file)
    tr_list = {}
    for sheet in book:
        # print('read patch list:' + sheet.title)
        _sn = sheet.title
        pr = pd.read_excel(file, sheetname=_sn).fillna('')
        tr_list[_sn] = pr

    def _fix(data):
        # n_list = pd.read_excel(file).fillna('')
        n_list = data

        for i, row in n_list.iterrows():
            if row['Chs'] != '' and row['Rep'] != '':
                am = row['Rep'].split(',')
                if row['Eng'] != '':
                    am.append(row['Eng'])

                for k in am:
                    k = k.replace('[', '\\[').replace(']', '\\]')
                    new_ser = new_ser.str.replace(''.join(k), row['Chs'])

    for x in tr_list:
        print('apply patch:' + x)
        # _fix(tr_list[x])
        for i, row in tr_list[x].iterrows():
            if row['Chs'] != '' and row['Rep'] != '':
                am = row['Rep'].split(',')
                if row['Eng'] != '':
                    am.append(row['Eng'])

                for k in am:
                    k = k.replace('[', '\\[').replace(']', '\\]')
                    new_ser = new_ser.str.replace(''.join(k), row['Chs'])

    return new_ser


# fix ->
def gui_patch(Series, file):
    print('patch gui')
    patch_list = pd.read_excel(file, index_col=0).fillna('')

    new_s = Series.copy()
    for i, row in patch_list.iterrows():
        if row['Custom'] != '':
            new_s[i] = row['Custom']
    return new_s


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

        xdf[m_key] = name_list(xdf[m_key],
                               os.path.join(STORAGE_DIR, 'Poe_name.xlsx'))
        xdf[f_key] = name_list(xdf[f_key],
                               os.path.join(STORAGE_DIR, 'Poe_name.xlsx'))

        xdf[m_key] = gui_patch(xdf[m_key],
                               os.path.join(STORAGE_DIR, 'Poe_fix.xlsx'))

        final_file = os.path.join(TEMP_DIR, TYPE_NAME + '_final.xlsx')
        print('out:' + final_file)
        xdf[[m_key, f_key]].to_excel(final_file, index_label='index')
        # 参考用
        xdf.to_excel(os.path.join(TEMP_DIR, TYPE_NAME + '_tempcustom.xlsx'))
    else:
        print('Config error')


if __name__ == '__main__':
    begin()
