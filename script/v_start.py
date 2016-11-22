# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET

import pandas as pd

from config import *
from lib import *


def out2excel(df, outFile):
    return


def trans2excel(path, outFile):
    return


def trans_merge(leftFile, rightFile):
    return


def patch_file(patchList, targetFile):
    return


def updata_string(filename, outPath):
    return


from v_string2excel import *


def original_table_2excel():
    string2excel(STRING_DIR, string_result_output_filename, 0)


def trans_group_2excel(type):

    # translated_result_list = translated_result_list[type]
    translated_df_list = []

    for result in translated_result_list[type]:

        group_name = result[u"group_name"]
        path = os.path.join(HOME_DIR, TRANDS_GROUP_DIR, result[u"path"])
        print(group_name, path)

        default_text_key = u"[{group_name}]{col_tilte}".format(
            group_name=group_name, col_tilte=STR_DEFAULT_TEXT)

        female_text_key = u"[{group_name}]{col_tilte}".format(
            group_name=group_name, col_tilte=STR_FEMALE_TEXT)

        res = parse_dir(path, type=1, d_key= default_text_key, f_key = female_text_key)
        translated_df = pd.DataFrame(res).set_index('index')
        translated_df_list.append(translated_df)

    translated_df_merge_result = translated_df_list[0]

    for df in translated_df_list[1:]:
        translated_df_merge_result = translated_df_merge_result.join(
            df, how='outer')

    translated_df_merge_result.fillna(value="")

    translated_df_merge_result.to_excel(trans_result_output_filename)


def trans_merge_one():
    many = pd.read_excel(trans_result_output_filename, index_col='index')

    for result in translated_result_list[type]:
        group_name = result["group_name"]


if __name__ == '__main__':
    game_name = TYPE_NAME
    # original_table_2excel()
    trans_group_2excel(game_name)