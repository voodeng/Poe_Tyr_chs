# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET

import pandas as pd

from config import *
from lib import *

# return DataFrame and use fix str lib
def string2excel2(path, default_text_key, female_text_key):
    translated_query_list = []
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.startswith(("~", ".")):
                continue
            full_filename = os.path.join(dirpath, filename)

            tree = ET.parse(full_filename)
            root = tree.getroot()
            name = root.find(STR_NAME).text

            for entry in root.iter(STR_ENTRY):
                id = entry.find(STR_ID).text
                default_text = entry.find(STR_DEFAULT_TEXT).text
                female_text = entry.find(STR_FEMALE_TEXT).text

                dft = default_text
                # if dft is not None:
                #     if has_ch(dft) is False:
                #         dft = ''

                fmt = female_text
                # dft = fix_text(default_text)
                # fmt = fix_text(female_text)

                item = {}
                item[u"index"] = u"{name}_{id}".format(name=name, id=id)
                item[default_text_key] = dft
                item[female_text_key] = fmt

                translated_query_list.append(item)

    translated_df = pd.DataFrame(translated_query_list)
    translated_df = translated_df.set_index('index')
    print(translated_df.describe())
    return translated_df

# output translate file
# index format "Name_ID", global_var TYPE_NAME
def translate_out():

    translated_df_list = []

    for result in translated_result_list[TYPE_NAME]:

        group_name = result[u"group_name"]
        path = os.path.join(HOME_DIR, TRANDS_GROUP_DIR, result[u"path"])
        print(group_name, path)

        default_text_key = u"[{group_name}]{col_tilte}".format(
            group_name=group_name, col_tilte=STR_DEFAULT_TEXT)

        female_text_key = u"[{group_name}]{col_tilte}".format(
            group_name=group_name, col_tilte=STR_FEMALE_TEXT)

        translated_df = string2excel2(path, default_text_key, female_text_key)
        translated_df_list.append(translated_df)

    translated_df_merge_result = translated_df_list[0]

    # df merge
    for df in translated_df_list[1:]:
        translated_df_merge_result = translated_df_merge_result.join(
            df, how='outer')

    translated_df_merge_result.fillna(value="")

    translated_df_merge_result.to_excel(trans_result_output_filename)

translate_out()
