import os
import sys

from config import *


'''
# 单行文字处理

is_ascii
    单字符ascii判断
has_ch
    字符串中是否包含中文
add_space, rm_space
     中文间空格处理
'''

def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def has_ch(text):
    ch_yes = False
    for uch in text:
        if uch >= '\u4e00' and uch <= '\u9fa5':
            ch_yes = True
        else:
            continue
    return ch_yes


def add_space(text):
    result = []

    for index in range(len(text) - 1):
        first = text[index]
        second = text[index + 1]

        if not is_ascii(first) and first != u" " \
                and not is_ascii(second) and second != u" ":

            # 连续两个中文字符，并且中间没有空格
            result.append(first)
            result.append(" ")
        else:
            result.append(first)

    result.append(text[-1])

    return "".join(result)


def rm_space(text):
    result = []

    for index in range(len(text) - 1):
        first = text[index]
        second = text[index + 1]

        if not is_ascii(first) and first != " " \
           and is_ascii(second) and second == " ":

            # 连续两个中文字符，中间有空格
            result.append(first)
        elif is_ascii(first) and first == " " \
                and not is_ascii(second) and second != " ":

            continue
        else:
            result.append(first)

    result.append(text[-1])
    return "".join(result)

# tee = u'[ 怕派  遣 [Slot 0]。]'
# print(re.sub('\s+', ' ', rm_space(tee)))
# ty = 0 中文符号转英文 | 1 转英文符号再转中文符号


def leftQuote(text):
    # 行首左引号

    if text[0] == '”':
        text = '“' + text[1:]
    return text


def nfix(text):
    # 多余换行清除

    nfix = '\n\n\n\n\n\n\n'
    num = len(nfix)
    while num > 1:
        newn = nfix[0:num + 1]
        text = text.replace(newn, newn[0:num])
        num -= 1
    return text


def conver(text, ty):
    '''
    参照字典，对照转换
    按需求添加转换
    '''
    table = {
        ord(f): ord(t)
        for f, t in zip('，。！？【】：（）％＃＠＆１２３４５６７８９０•', ',.!?[]:()%#@&1234567890·')
    }

    table2 = {
        ord(f): ord(t)
        for f, t in zip(',.!?:""\'\'', '，。！？：“”‘’')
    }
    # 两个不一样的间隔符
    # • # ·
    #   ',.!?""\'\'()%#@&',
    #   '，。！？“”‘’（）％＃＠＆'

    if ty == 0:
        return text.translate(table)
    else:
        return text.translate(table).translate(table2)

# 中文标点转换
# tee = ' "英文引号" 和 “中文引号” 和 "千中后” “后英" ”后中” “前中“ “前中‘单影’ 中国，中文，标点符号！你好？１２３４５＠＃【】+=-（） '
# print(conver(tee, 0))
# print(conver(tee, 1))


def oth_handle(text):
    text = text.replace('。。。', '……').replace('vs。', 'vs.').replace(
        'vs.{', 'vs. {').replace('}vs.', '} vs.')

    text = nfix(leftQuote(text))
    return text


def fix_text(str):
    # if str is not None:
    if str is None or str == '':
        return ''
    else:
        str = rm_space(str)
        str = conver(str, 1)
        str = oth_handle(str)
        return str
