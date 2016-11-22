# -*- coding: utf-8 -*-
import os

import pandas as pd

from config import *
from lib import *
import StringTable
'''
1. 指定文件夹，遍历目录，对.string后缀文件进行处理。 整理导出至excel文件中，保留ID，Name等
2. 遍历对象，指定汉化文件夹，遍历，导出到excel，合并索引为Name_ID
   建立处理多家汉化的方式
3. 生成中英对照表，已便之后更新文本
4. 处理对照文本，额外补丁，名词替换，符号修复等等
5. 根据原string文档结构，再通过对照表生成string文本
'''

# code:
STB = StringTable.StringTable()


def string2excel(path, outfile):
    data = STB.parse_dir(path)
    df = STB.create_df(data=data, index=False)
    df.to_excel(outfile, index=False)


def origin2excel(outfile):
    path = STRING_DIR
    string2excel(path, outfile)


def trans2excel(outfile):
    translated_df_list = []
    trans_group = translated_result_list[TYPE_NAME]
    for result in trans_group:
        group_name = result["group_name"]
        path = os.path.join(HOME_DIR, TRANDS_GROUP_DIR, result["path"])
        print(group_name, path)

        default_text_key = u"[{group_name}]{col_tilte}".format(
            group_name=group_name, col_tilte=STR_DEFAULT_TEXT)

        female_text_key = u"[{group_name}]{col_tilte}".format(
            group_name=group_name, col_tilte=STR_FEMALE_TEXT)

        res = STB.parse_dir(path)
        translated_df = STB.create_df(
            data=res,
            index=True,
            d_key=default_text_key,
            f_key=female_text_key)
        translated_df_list.append(translated_df)

    translated_df_merge_result = translated_df_list[0]

    # join合并
    for df in translated_df_list[1:]:
        translated_df_merge_result = translated_df_merge_result.join(
            df, how='outer')

    translated_df_merge_result.fillna(value="")
    translated_df_merge_result.to_excel(outfile)


def merge2excel(outfile):
    # string_excel = os.path.join(TEMP_DIR, 'Tyranny_string_result.xlsx')
    # trans_excel = os.path.join(TEMP_DIR, 'Tyranny_trans_result.xlsx')

    string_excel = string_result_output_filename
    trans_excel = trans_result_output_filename

    print('l-excel: ' + string_excel)
    print('r-excel: ' + trans_excel)
    # custom_excel = os.path.join(STORAGE_DIR,'Tyr_custom.xlsx')

    ldf = pd.read_excel(string_excel).fillna('')
    # ldf = ldf[['Name','ID','DefaultText','FemaleText','Custom','Custom_female']]
    ldf.index = [ldf['Name'] + '_' + ldf['ID'].astype('str')]
    ldf.index.name = 'index'

    rdf = pd.read_excel(trans_excel, index_col='index').fillna('')

    xdf = ldf.join(rdf).drop_duplicates()

    xdf.to_excel(outfile)


def use_custom():
    custom_file = os.path.join(SOTRAGE_DIR, 'Tyr_custom.xlsx')
    cdf = pd.DataFrame(custom_file)


def start(**args):
    '''

    '''
    override = False if 'override' not in args else args['override']

    def exist(anyfile):
        return os.path.exists(anyfile)

    def handle(anyfile, callback):
        if exist(anyfile):
            print('has file: ' + anyfile)
            if override:
                print('override this')
                callback(anyfile)
            # pass
        else:
            print('creat file')
            callback(anyfile)

    # 显示基本设置
    print('Config: {t}'.format(t=TYPE_NAME))

    # Original StringTable
    print('StringTable to Excel')

    print('\nString:\n{org} \n ==> {out}'.format(
        org=STRING_DIR, out=string_result_output_filename))
    handle(string_result_output_filename, origin2excel)

    # Translated StringTable
    print('\nTrans:')
    print(' ==> {out}'.format(out=trans_result_output_filename))
    handle(trans_result_output_filename, trans2excel)

    # Compres eng and chs file
    print('\nCompres: {org} \n ==> {out}'.format(
        org='', out=merge_result_output_filename))
    handle(merge_result_output_filename, merge2excel)

    # Use Custom files patch
    print('\nPatched: \n ==> {out}'.format(out=merge_patched))
    import patch
    patch.begin()


if __name__ == '__main__':
    '''
    y / n : 是否覆盖已有的excel文件
    '''
    str = input("want *Override* file? Default is *not* ([y]es/n): ")
    if str.lower() == 'y' or str.lower() == 'yes':
        print('this setting will override exists file!')
        start(override=True)
    else:
        print('Do not override')
        start(override=False)
    # merge2excel(merge_result_output_filename)
