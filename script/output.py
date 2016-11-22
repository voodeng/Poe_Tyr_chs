# -*- coding: utf-8 -*-
import datetime
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
import openpyxl
import pandas as pd
import xlrd

from config import *
from lib import *


def gen_xml(xmlfilename):
    # 设置根节点
    root = ET.Element('Language')
    tree = ET.ElementTree(root)
    # 设置1级子节点
    ET.SubElement(root, 'Name').text = 'VsChs'
    ET.SubElement(root, 'GUIString').text = 'Vs{}'.format(
        datetime.datetime.now().strftime('%y%m%d'))

    if not os.path.exists(xmlfilename):
        # os.mknod(xmlfilename)
        tree.write(xmlfilename, 'utf-8')


def df_outstring(df, en_strtbl_path, output_strtbl_path, d_key, f_key):
    '''
    需要带索引 Name_ID 的 DataFrame
    '''

    default_text_key = d_key
    female_text_key = f_key

    translated_df_merge_result = df

    for dirpath, dirnames, filenames in os.walk(en_strtbl_path):

        for filename in filenames:
            if filename.startswith(("~", ".")):
                continue
            if not filename.endswith(("stringtable")):
                continue

            # old english string table file
            src_filename = os.path.join(dirpath, filename)
            # output to new filename
            dst_path = dirpath.replace(en_strtbl_path, output_strtbl_path)
            dst_filename = src_filename.replace(en_strtbl_path,
                                                output_strtbl_path)

            # parse string table xml
            tree = ET.parse(src_filename)
            root = tree.getroot()
            name = root.find(STR_NAME).text

            for entry in root.iter(STR_ENTRY):
                id = entry.find(STR_ID).text
                default_text_item = entry.find(STR_DEFAULT_TEXT)
                female_text_item = entry.find(STR_FEMALE_TEXT)

                key = u"{name}_{id}".format(name=name, id=id)

                if key not in translated_df_merge_result.index:
                    continue
                else:
                    print(key)

                    translated_result = translated_df_merge_result.ix[key]

                    default = translated_result[default_text_key]
                    female = translated_result[female_text_key]
                    try:
                        if default:
                            if u"nan" == default or default == '':
                                continue
                            default_text_item.text = default
                            if female:
                                female_text_item.text = female
                            # print default
                            # break
                            continue
                    except:
                        if default.iloc[1]:
                            if u"nan" == default.iloc[1] or default.iloc == '':
                                continue
                            default_text_item.text = default.iloc[1]
                            if female.iloc[1]:
                                female_text_item.text = female.iloc[1]
                            continue
                    else:
                        # mod = english
                        # mod_female = english_female
                        continue

            try:
                os.makedirs(dst_path)
            except:
                pass

            try:
                tree.write(dst_filename, encoding="utf-8")
            except Exception as e:
                print(src_filename)
                print(e)
                print(tree)

    print('Output to: ' + output_strtbl_path)


def excel_outstring(final_filename, en_strtbl_path, output_strtbl_path, d_key,
                    f_key):

    default_text_key = d_key
    female_text_key = f_key

    try:
        tmdf = pd.read_excel(final_filename, index_col='index').fillna('')
    except:
        tmdf = pd.read_excel(final_filename).fillna('')
        tmdf.index = [tmdf['Name'] + '_' + tmdf['ID'].astype(str)]

    print(tmdf.index)

    df_outstring(tmdf, en_strtbl_path, output_strtbl_path, default_text_key,
                 female_text_key)

    xmlfilename = os.path.join(output_strtbl_path, "language.xml")
    gen_xml(xmlfilename)


if __name__ == '__main__':
    print('Output Excel to StringTable')

    final_filename = os.path.join(TEMP_DIR, 'Tyr_final.xlsx')
    en_strtbl_path = os.path.join(ORIGIN_DIR, 'Tyranny/1.0/en')
    output_strtbl_path = os.path.join(OUTPUT_DIR, 'Tyr/outtext')

    excel_outstring(final_filename, en_strtbl_path, output_strtbl_path,
                    'merged', 'merged_female')
