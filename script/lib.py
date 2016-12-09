# -*- coding:utf-8 -*-
import operator
import itertools
import re
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
    '''
    先删除所有空格，再按照需要保留空格
    需要干掉的空格:
        所有非ascii间的空格
        [ li ] 左右及贴边的空格
        ( li ) 左右及贴边的空格
        - 左右的空格
    要保留的空格:
        {0}
        英文间的空格
    '''
    result = []

    def en(s):
        return is_ascii(s) and s != ' '

    def ch(s):
        return not is_ascii(s) and s != ' '

    for index in range(len(text) - 1):
        first = text[index]
        second = text[index + 1]

        if ch(first) and second == " ":
            result.append(first)
        elif first == " " and ch(second):
            continue
        elif first == " " and second == "[" or first == " " and second == "]":
            continue
        elif first == " " and second == "(" or first == " " and second == ")":
            continue
        elif first == " " and second == "-":
            continue
        elif first == " " and second == " ":
            continue
        else:
            result.append(first)

    result.append(text[-1])

    new_result = ''.join(result)
    new_result = new_result.replace('[ ', '[').replace('] ', ']').replace(
        '( ', '(').replace(') ', ')').replace('- ', '-')
    new_result = new_result.strip()

    return new_result


# tee = u'[ 怕，  派   遣 [Sl ot 0] 。  ] sma {1}  (gloss - aire) {0} x{2} {3} ashgo 草... vs。'
# 理想值 [怕，派遣[Sl ot 0]。]草
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


def ch_quote(text):
    dquotes = itertools.cycle(u'“”' if text.count('"') & 1 == 0 else u'＂')
    squotes = itertools.cycle(u'‘’' if text.count("'") & 1 == 0 else u'＇')
    _obj = lambda x: next(dquotes) if '"' == x.group() else next(squotes)
    pattern = re.compile('[\'\"]', re.U)

    text = pattern.sub(_obj, text)
    return text


def conver(text, ty):
    '''
    参照字典，对照转换
    按需求添加转换
    '''
    table = {
        ord(f): ord(t)
        # for f, t in zip('，。\“\”\‘\’＇＂！？【】（）％＃＠＆１２３４５６７８９０•',
        # ',.\"\"\'\'\'\"!?[]()%#@&1234567890·')
        for f, t in zip('，。“”‘’＇＂！？【】；（）％＃＠＆１２３４５６７８９０•',
                        ',.""\'\'\'"!?[];()%#@&1234567890·')
    }

    table2 = {ord(f): ord(t) for f, t in zip(',.!?;', '，。！？；')}

    # 两个不一样的间隔符
    # • # ·

    if ty == 0:
        # 中转英
        return text.translate(table)
    else:
        # 英转中
        text = text.translate(table).translate(table2)
        text = ch_quote(text)
        return text


# 标点转换
# tee = ' "英文引号" 和 “中文引号” 和 "千中后” “后英" ”后中” “前中“ “前中‘单影’ 中国，中文，标点符号！你好？１２３４５＠＃【】+=-（） '
# print(conver(tee, 0))
# print(conver(tee, 1))


def oth_handle(text):
    # table = [
    #     '。。。':'……',
    #     '[ ':'[',
    #     '] ':']',
    #     '- ':'-',
    #     ' -':'-',
    #     '--':'-',
    #     '-':'—',
    #     '( ':'(',
    #     ') ':')',
    #     'vs。':'vs.',
    #     ']vs.', '] vs.'
    #  ]

    text = text.replace('。。。', '……').replace('--', '-').replace(
        '-', '—').replace('vs。', 'vs. ').replace(
            ')vs.', ') vs.').replace(']vs.', '] vs.').replace(
                'vs.  {', 'vs. {').replace(']＇', ']')

    text = nfix(leftQuote(text))
    return text


def fix_text(str):
    if str is None or str == '':
        return ''
    else:
        str = conver(str, 1)
        str = rm_space(str)
        str = oth_handle(str)
        return str


if __name__ == '__main__':
    print('Some Char Tools')
