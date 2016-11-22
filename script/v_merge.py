# coding=utf-8
import openpyxl
import pandas as pd
import xlrd

from config import *

string_result = string_result_output_filename
trans_result = trans_result_output_filename

font = openpyxl.styles.Font(
    name='Microsoft YaHei',
    size=10,
    bold=False,
    italic=False,
    vertAlign=None,
    underline='none',
    strike=False,
    color='FF000000')

fill = openpyxl.styles.PatternFill(
    fill_type=None,
    start_color='FFFFFFFF',
    end_color='FF000000')


def merge_trans(outfile):
    translated_df_merge_result = pd.read_excel(
        trans_result, index_col='index').fillna('')

    # translated_df_merge_result = translated_df_merge_result.set_index('index')

    book = xlrd.open_workbook(string_result)
    wb = openpyxl.Workbook()
    ws = wb.active

    for sheet in book.sheets():
        for rowx in range(0, sheet.nrows):
            table, id, english, english_female, custom, custom_female = sheet.row_values(
                rowx)

            if rowx > 0:
                key = u"{table}_{id}".format(table=table, id=id)
                print(key)

                if key not in translated_df_merge_result.index:
                    custom = english
                    custom_female = english_female

                else:
                    translated_result = translated_df_merge_result.ix[key]

                    for result in translated_result_list[TYPE_NAME]:
                        group_name = result["group_name"]
                        default_text_key = "[{group_name}]{col_tilte}".format(
                            group_name=group_name, col_tilte=STR_DEFAULT_TEXT)

                        female_text_key = "[{group_name}]{col_tilte}".format(
                            group_name=group_name, col_tilte=STR_FEMALE_TEXT)

                        default = translated_result[default_text_key]
                        famle = translated_result[female_text_key]

                        try:
                            if default.ix[0]:
                                custom = default.ix[0]
                                custom_female = famle.ix[0]
                                break
                        except:
                            custom = default
                            custom_female = famle
                            break
                        else:
                            pass
            ws.append(
                (table, id, english, english_female, custom, custom_female))

    try:
        wb.save(outfile)
        print("{filename} outputed".format(filename=outfile))
    except:
        print('Error write file!')

if __name__ = '__main__':
    merge_trans(merge_result_output_filename)
