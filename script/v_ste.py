# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import xlrd
import openpyxl

from config import *

# TODO
# 追加差异： 1.读取最新的stringtable文件，缓存进去
# 2.读取xlsx文件，缓存文本
# 3. 判定差异， 在 X_NAME 含有 STR_NAME 并且 X_ID = STR_ID 等情况下，判断 X_English 是否等于 STR_DEFAULT_TEXT , 并使用最新的覆盖
# 4. 对于有修改的差异内容，在X_Revision列里，给加红

# 双向生成文档：
# 1. 读取xlsx文件结构，输出翻译过后的文件
# 2. 忽略官方table - 后缀的数字

# 合并翻译文本，输出stringtable

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def add_space(text):
    result = []

    for index in range(len(text)-1):
        first = text[index]
        second = text[index + 1]

        if not is_ascii(first) and first != u" " \
            and not is_ascii(second) and second != u" ":
            # 连续两个中文字符，并且中间没有空格
            # 如果是英文空格，应该不是 is_ascii
            result.append(first)
            result.append(u" ")
        else:
            result.append(first)

    result.append(text[-1])

    return u"".join(result)

def rm_space(text):
    result = []

    for index in range(len(text)-1):
        first = text[index]
        second = text[index + 1]

        if not is_ascii(first) and first != u" " \
            and is_ascii(second) and second == u" " :
            # 连续两个中文字符，中间有空格
            result.append(first)
            # print first

            # result.append(u" ")
        elif is_ascii(first) and first == u" " \
               and not is_ascii(second) and second != u" " :
                continue

        else:
            result.append(first)

    result.append(text[-1])

    return u"".join(result)

# tee = u'[怕派 遣 [Slot 0]。]'
# print rm_space(unicode(tee))

def string2excel():
    # path = os.path.join(HOME_DIR, ORIGIN_DIR, 'string-table/3.02')
    path = STRING_DIR

    string_query_list = []

    refid = 0

    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.startswith(("~", ".")):
                continue

            ntype = dirpath.split('\\')[6]
            full_filename = os.path.join(dirpath, filename)
            tree = ET.parse(full_filename)
            root = tree.getroot()
            name = root.find(STR_NAME).text

            for entry in root.iter(STR_ENTRY):
                id = entry.find(STR_ID).text
                default_text = entry.find(STR_DEFAULT_TEXT).text
                female_text = entry.find(STR_FEMALE_TEXT).text

                item = {}
                # item[u"index"] = u"{name}_{id}".format(name = name, id = id)
                item[u"Refer"] = refid
                item[u"Type"] = ntype
                item[u"Name"] = name
                item[u"ID"] = id
                item[u"DefaultText"] = default_text
                item[u"FemaleText"] = female_text
                item[u'Mod'] = ''
                item[u'Mod_Female'] = ''
                item[u'Custom'] = ''
                item[u'Custom_female'] = ''

                refid += 1
                string_query_list.append(item)

    string_df = pd.DataFrame(string_query_list)
    string_df = string_df.set_index('Refer')
    # print(string_df.sort_index(axis=1, ascending=False))
    print(string_df.head())
    # print string_df

    string_df.to_excel(string_result_output_filename, columns=['Type','Name','ID','DefaultText','FemaleText','Mod','Mod_Female', 'Custom', 'Custom_female'])


def merge_trans():

    translated_result_list = [
        {
            u"group_name": u"ali4.0",
            u"path": u"ali4.0",
        },
        # {
        #     u"group_name": u"3dm5.0",
        #     u"path": u"3dm_5.0",
        # }
        {
            u"group_name": u"DLC1",
            u"path": u"DLC1",
        },
        {
            u"group_name": u"DLC2",
            u"path": u"DLC2",
        }
    ]

    translated_df_list = []

    for result in translated_result_list:
        translated_query_list = []

        group_name = result[u"group_name"]
        path = os.path.join(HOME_DIR, TRANDS_GROUP_DIR, result[u"path"])
        print(group_name, path)

        default_text_key = u"[{group_name}]{col_tilte}".format(group_name = group_name,
                                                                col_tilte = STR_DEFAULT_TEXT)

        female_text_key = u"[{group_name}]{col_tilte}".format(group_name = group_name,
                                                                col_tilte = STR_FEMALE_TEXT)

        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.startswith(("~", ".")):
                    continue
                full_filename = os.path.join(dirpath, filename)
                #print full_filename.encode('utf-8')

                # parse string table xml
                tree = ET.parse(full_filename)
                root = tree.getroot()

                name = root.find(STR_NAME).text
                #print name.encode('utf-8')

                for entry in root.iter(STR_ENTRY):
                    id = entry.find(STR_ID).text
                    default_text = entry.find(STR_DEFAULT_TEXT).text
                    female_text = entry.find(STR_FEMALE_TEXT).text
                    dft = unicode(default_text)
                    dft = rm_space(dft)

                    item = {}
                    item[u"index"] = u"{name}_{id}".format(name = name, id = id)
                    item[default_text_key] = dft.strip()
                    item[female_text_key] = unicode(female_text).strip()

                    #print item
                    translated_query_list.append(item)

        translated_df = pd.DataFrame(translated_query_list)
        translated_df = translated_df.set_index('index')
        #print(translated_df.head())
        print( translated_df.describe() )
        translated_df_list.append(translated_df)

    translated_df_merge_result = translated_df_list[0]
    #print u"Left-->"
    # print translated_df_merge_result.describe()


    for df in translated_df_list[1:]:
        #print u"Right-->"
        #print df.describe()
        #translated_df_merge_result = pd.concat([result, df], axis=1)
        translated_df_merge_result = translated_df_merge_result.join(df, how='outer')

    translated_df_merge_result.fillna(value="")

    # 输出对比文件excel
    translated_df_merge_result.to_excel(merge_result_output_filename)

    string_result_output_filename = os.path.join(HOME_DIR, TEMP_DIR, u'string_result.xlsx')

    book = xlrd.open_workbook(string_result_output_filename)

    wb = openpyxl.Workbook()
    ws = wb.active

    for sheet in book.sheets():
        for rowx in range(0, sheet.nrows):
            # Table	ID	Speaker	Listener	English	English Female	Mod	Mod Female	Revision
            # table, id, speaker, listener, english, english_female, mod, mod_female, revision = sheet.row_values(rowx)

            Refer,type, table, id, english, english_female, mod, mod_female, custom, custom_female = sheet.row_values(rowx)
            # Refer	Name	ID	DefaultText FemaleText	Mod	Mod_Female

            if rowx > 0:

                key = u"{table}_{id}".format(table = table.split()[0], id = id)
                # print key
                if key not in translated_df_merge_result.index:
                    # mod = english
                    mod_female = english_female

                else:
                    translated_result = translated_df_merge_result.ix[key]

                    for result in translated_result_list:
                        group_name = result[u"group_name"]
                        default_text_key = u"[{group_name}]{col_tilte}".format(group_name = group_name,
                                                                                col_tilte = STR_DEFAULT_TEXT)

                        female_text_key = u"[{group_name}]{col_tilte}".format(group_name = group_name,
                                                                                col_tilte = STR_FEMALE_TEXT)

                        default = translated_result[default_text_key]
                        # default = unicode(default).strip()
                        # default = default.replace(' ', '')
                        try:
                            if default:
                                if u"nan" == unicode(default):
                                    continue
                                if u"None" == unicode(default):
                                    continue
                                default = unicode(default)
                                # mod = default
                                # mod_female = translated_result[female_text_key]
                                custom = default
                                custom_female = translated_result[female_text_key]

                                #print default
                                break
                        except:
                            # print u"\n======"

                            # print u"key: ", default_text_key
                            # print u"text: ", default
                            # print "Unexpected error:", sys.exc_info()[0]
                            if default[1]:
                                if u"nan" == unicode(default):
                                    continue
                                if u"None" == unicode(default):
                                    continue
                                default = unicode(default)
                                # default = default.replace(' ', '')
                                custom = default[1]
                                custom_female = translated_result[female_text_key][0]
                        else:
                            # mod = english
                            # mod_female = english_female
                            # pass
                            break

            ws.append((Refer,type, table, id, english, english_female, mod, mod_female, custom, custom_female))

    print(u"{filename} outputing").format(filename = output_full_filename)
    wb.save(output_full_filename)


def up_string():
    mytrans_excel = os.path.join(HOME_DIR,OUTPUT_DIR, u'trans_use.xlsx')
    book = xlrd.open_workbook(mytrans_excel)

    tr = pd.read_excel(mytrans_excel,header=0)

    # te = tr[( tr.ID == 2440 ) & ( tr.Name == 'game\gui' )]
    te = pd.DataFrame(tr)
    # tk = te[( te['Name']== 'game\gui' ) & ( te['ID'] == 2440 )]
    te = te.fillna(value="")

    en_strtbl_path = os.path.join(HOME_DIR, ORIGIN_DIR, 'string-table/3.02')
    output_strtbl_path = os.path.join(HOME_DIR, OUTPUT_DIR, 'sip')

    for dirpath, dirnames, filenames in os.walk(en_strtbl_path):
        for filename in filenames:
            if filename.startswith(("~", ".")):
                continue
            if not filename.endswith(("stringtable")):
                continue

            #old english string table file
            src_filename = os.path.join(dirpath, filename)
            # output to new filename
            dst_path = dirpath.replace(en_strtbl_path, output_strtbl_path)
            dst_filename = src_filename.replace(en_strtbl_path,output_strtbl_path)


            # parse string table xml
            tree = ET.parse(src_filename)

            root = tree.getroot()

            name = root.find(STR_NAME).text

            tk = te[(te['Name'] == name)]
            for entry in root.iter(STR_ENTRY):
                id = entry.find(STR_ID).text
                default_text_item = entry.find(STR_DEFAULT_TEXT)
                female_text_item = entry.find(STR_FEMALE_TEXT)

                key = u"{name}_{id}".format(name = name, id = id)
                # print key

                tp = tk.ix[tk['ID'] == int(id)]
                # mod = tp['Mod']

                # if key not in translated_df_merge_result.index:
                if tp.empty:
                    continue
                else:
                    #print key
                    # translated_result = translated_df_merge_result.ix[key]
                    translated_result = tp

                    default_text_key = u"Custom"

                    female_text_key = u"Custom_female"

                    default = translated_result[default_text_key].values
                    female = translated_result[female_text_key].values

                    default_text_item.text = unicode(default[0]).strip()
                    female_text_item.text = unicode(female[0])
            #output
            try:
                os.makedirs(dst_path)
            except:
                pass

            try:
                tree.write(dst_filename, encoding="utf-8")
            except Exception as e:
                print( src_filename )
                print( e )
                print( tree )

string2excel()
# merge_trans()
# up_string()
