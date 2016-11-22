# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import xlrd
import openpyxl
import datetime

from config import *
from lib import *

CUS = 'vmod'

# 1 way,  使用合成带索引的文件
# final_filename = os.path.join(HOME_DIR, OUTPUT_DIR, u'final.xlsx')
# en_strtbl_path = STRING_DIR
# output_strtbl_path = os.path.join(OUTPUT_DIR, VER_DIR)
# translated_df_merge_result = pd.read_excel(final_filename).fillna('')

# 2 way 使用双语对比的无索引文件
final_filename = os.path.join(STORAGE_DIR, 'Tyr_en-chs.xlsx')
en_strtbl_path = os.path.join(ORIGIN_DIR, 'Tyranny/1.0')
output_strtbl_path = os.path.join(OUTPUT_DIR, 'Tyr')

# XML
xmlfilename = os.path.join(output_strtbl_path, "language.xml")


def gen_xml(xmlfilename):
    # 设置根节点
    root = ET.Element('Language')
    tree = ET.ElementTree(root)
    # 设置1级子节点
    ET.SubElement(root, 'Name').text = 'VsChs'
    ET.SubElement(root, 'GUIString').text = 'Vs{}'.format(
        datetime.datetime.now().strftime('%y%m%d'))

    try:
        tree.write(xmlfilename, 'utf-8')
    except:
        os.mknod(xmlfilename)
        tree.write(xmlfilename, 'utf-8')


def gen_string(final_filename, en_strbl_path, output_strtbl_path):

    tmdf = pd.read_excel(final_filename)
    tmdf.index = [tmdf['Name'] + '_' + tmdf['ID'].astype(str)]
    translated_df_merge_result = pd.DataFrame(
        tmdf, columns=['Custom', 'Custom_female']).fillna('')

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

                    default_text_key = 'Custom'
                    female_text_key = 'Custom_female'
                    default = translated_result[default_text_key]
                    female = translated_result[female_text_key]
                    try:
                        if default:
                            if u"nan" == default or default == '':
                                continue
                            default_text_item.text = default
                            if female:
                                female_text_item = female
                            # print default

                            # break
                            continue
                    except:
                        if default.iloc[1]:
                            if u"nan" == default.iloc[1] or default.iloc == '':
                                continue
                            default_text_item.text = default.iloc[1]
                            if female.iloc[1]:
                                female_text_item = female.iloc[1]
                            continue
                    else:
                        # mod = english
                        # mod_female = english_female
                        continue

            # output

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


gen_xml(xmlfilename)
