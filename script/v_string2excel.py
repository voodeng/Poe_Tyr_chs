# -*- coding: utf-8 -*-
import os
import sys
import xml.etree.ElementTree as ET

import pandas as pd

from config import *


def parse_file(filename, type):
    if filename.startswith(("~", ".")):
        return

    entry_list = []
    tree = ET.parse(filename)
    root = tree.getroot()
    name = root.find(STR_NAME).text

    for entry in root.iter(STR_ENTRY):
        id = entry.find(STR_ID).text
        default_text = entry.find(STR_DEFAULT_TEXT).text
        female_text = entry.find(STR_FEMALE_TEXT).text

        item = {}
        if type == 1:
            item["Name"] = name
            item["ID"] = id
            item["DefaultText"] = default_text
            item["FemaleText"] = female_text
            item['Custom'] = ''
            item['Custom_female'] = ''
        else:
            item["index"] = "{name}_{id}".format(name=name, id=id)
            item["DefaultText"] = default_text
            item["FemaleText"] = female_text

        entry_list.append(item)

    return entry_list


def parse_dir(path, **args):

    type = args['type']

    if 'd_key' in args:
        d_key = args['d_key']
    else:
        d_key = 'DefaultText'

    if 'f_key' in args:
        f_key = args['f_key']
    else:
        f_key = 'FemaleText'

    string_query_list = []

    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.startswith(("~", ".")):
                continue

            full_filename = os.path.join(dirpath, filename)

            entry_list = []
            tree = ET.parse(full_filename)
            root = tree.getroot()
            name = root.find(STR_NAME).text

            for entry in root.iter(STR_ENTRY):
                id = entry.find(STR_ID).text
                default_text = entry.find(STR_DEFAULT_TEXT).text
                female_text = entry.find(STR_FEMALE_TEXT).text

                item = {}
                if not type or type == 0:
                    item["Name"] = name
                    item["ID"] = id
                    item["DefaultText"] = default_text
                    item["FemaleText"] = female_text
                    item['Custom'] = ''
                    item['Custom_female'] = ''
                else:
                    item["index"] = "{name}_{id}".format(name=name, id=id)
                    item[d_key] = default_text
                    item[f_key] = female_text

                entry_list.append(item)

            string_query_list.extend(entry_list)

    # string_df = pd.DataFrame(string_query_list,index=None)
    string_df = string_query_list

    return string_df


def string2excel(path, output, type):

    # type 1: like trans, index = Name_ID
    # type 0: no index no custom table

    string_df = parse_dir(path, type=0)
    string_df = pd.DataFrame(string_df)
    if not type or type == 0:
        string_df.to_excel(output, columns=[
                        'Name', 'ID', 'DefaultText', 'FemaleText', 'Custom', 'Custom_female'], index=False)
    else:
        string_df.to_excel(output, columns=[
                        'index', 'DefaultText', 'FemaleText'], index=False)


if __name__ == '__main__':
    string2excel(STRING_DIR, string_result_output_filename, 0)
