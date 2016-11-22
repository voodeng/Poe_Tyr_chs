# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET

import pandas as pd

TAG_STRING_TABLE_ENTRY = "Entry"
TAG_STRING_TABLE_NAME = 'Name'
TAG_STRING_TABLE_ID = 'ID'
TAG_STRING_TABLE_DEFAULT_TEXT = "DefaultText"
TAG_STRING_TABLE_FEMALE_TEXT = "FemaleText"


class StringTable:
    def __init__(self):
        self.df = pd.DataFrame()

    def parse_file(self, filename):
        '''
        Return:
            items: {list} [{tuple} (name, id, default_text, female_text)]
        '''
        tree = ET.parse(filename)
        root = tree.getroot()

        # print(filename)
        name = root.find(TAG_STRING_TABLE_NAME).text
        items = []
        for entry in root.iter(TAG_STRING_TABLE_ENTRY):
            id = entry.find(TAG_STRING_TABLE_ID).text
            default_text = entry.find(TAG_STRING_TABLE_DEFAULT_TEXT).text
            female_text = entry.find(TAG_STRING_TABLE_FEMALE_TEXT).text

            item = (name, id, default_text, female_text)
            items.append(item)
        return items


    def parse_dir(self, strtbl_dir):
        result = []
        for dirpath, dirnames, filenames in os.walk(strtbl_dir):
            for filename in filenames:
                if filename.startswith(("~", ".")):
                    continue
                if not filename.endswith(("stringtable")):
                    continue
                full_filename = os.path.join(dirpath, filename)
                items = self.parse_file(full_filename)
                result.extend(items)
        return result


    def create_df(self, **args):
        '''
        Args:
            index {boolean}
            data {list}
            d_key {str}
            f_key {str}
        '''
        index = False if 'index' not in args else args['index']
        d_key = 'DefaultText' if 'd_key' not in args else args['d_key']
        f_key = 'FemaleText' if 'f_key' not in args else args['f_key']

        if 'data' not in args:
            print('err: need arg (data=?)')
            return

        df = pd.DataFrame.from_records(
            args['data'], columns=['Name', 'ID', d_key, f_key])

        if index:
            df.index = [df['Name'] + '_' + df['ID']]
            df.index.name = 'index'
            df = df[[d_key, f_key]]

        return df
