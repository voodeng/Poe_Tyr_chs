# -*- coding: utf-8 -*-
import os

# string-table 结构
STR_ENTRY = 'Entry'
STR_NAME = 'Name'
STR_ID = 'ID'
STR_DEFAULT_TEXT = 'DefaultText'
STR_FEMALE_TEXT = 'FemaleText'

TAG_CUSTOM = 'Custom'
TAG_FEMALE = 'Custom_female'

# POE
POE_VER = '3.04'
POE_ORG_STRING_DIR = 'Ben'
POE_DLC1_STRING_DIR = 'DLC1'
POE_DLC2_STRING_DIR = 'DLC2'

# Tyranny
T_VER = '1.02'
T_ORG_DIR = 'en'


# Typename = Tyranny | Poe
TYPE_NAME = 'Tyranny'
VER_DIR = '1.02'
# TYPE_NAME = 'Poe'
# VER_DIR = '3.04'


# 目录
# HOME_DIR = os.path.abspath('..')
HOME_DIR = os.path.dirname(os.path.split(os.path.realpath(__file__))[0])
OUTPUT_DIR = os.path.join(HOME_DIR, 'output')
TEMP_DIR = os.path.join(HOME_DIR, 'temp_output')
ORIGIN_DIR = os.path.join(HOME_DIR, 'original')
STORAGE_DIR = os.path.join(HOME_DIR, 'storage')

STRING_DIR = os.path.join(ORIGIN_DIR, TYPE_NAME, VER_DIR)
P_STRING_DIR = os.path.join(ORIGIN_DIR, 'Poe')
T_STRING_DIR = os.path.join(ORIGIN_DIR, 'Tyranny')

# 原词表
string_result_output_filename = os.path.join(
    TEMP_DIR, TYPE_NAME + '_string_result.xlsx')

# 翻译文本表
trans_result_output_filename = os.path.join(
    TEMP_DIR, TYPE_NAME + '_trans_result.xlsx')

# 双语对比表
merge_result_output_filename = os.path.join(
    TEMP_DIR, TYPE_NAME + '_merge_result.xlsx')

# 自定义补丁表
patch_filename = os.path.join(
    STORAGE_DIR, TYPE_NAME + "_patch_table.xlsx")

# 已打补丁
merge_patched = os.path.join(
    OUTPUT_DIR, TYPE_NAME + "_merge_patched.xlsx")

# 最终输出引用表
output_full_filename = os.path.join(
    OUTPUT_DIR, TYPE_NAME + "_final.xlsx")

# 参考用合集
tempcustom_full_filename = os.path.join(
    TEMP_DIR, TYPE_NAME + "_tempCustom.xlsx")


# 已有翻译文件夹
TRANDS_GROUP_DIR = 'translate_group_result'
translated_result_list = {
    'Poe': [
        {
            "group_name": "ali4.4",
            "path": "Poe/ali4.4"
        },
        {
            "group_name": "3dm6.0",
            "path": "Poe/3dm6.0"
        }
    ],
    'Tyranny': [
        {
            "group_name": "ali",
            "path": "Tyr/ali3.6"
        },
        {
            "group_name": "3dm",
            "path": "Tyr/3dm2.0"
        }
    ]
}
