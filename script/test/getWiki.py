#coding: utf-8
import os
import sys
import requests
import re
import json

# 网页获取及页面分析
# v0.0.-1

def get_page(pageUrl):
    try:
        print('concet to: ' + pageUrl)
        req = requests.get(pageUrl,timeout=20)
        content = req.text
        return content
    except:
        print('concet error')
        return ''

def getSpellsDesc(pageUrl):
    content = get_page(pageUrl)
    if not content:
        print('error load page')
        return ''
    # 规则1
    pattern = re.compile('<table class="quote.*?>.*?<i>(.*?)</i>.*?</table>',re.S)
    # 规则2
    pattern2 = re.compile('<div id="mw-content-text.*?>.*?<p>(.*?)</p>.*?</div>',re.S)
    result = re.search(pattern,content)

    if result is None:
        try:
            result = re.search(pattern2,content)
            str = re.sub(r'</?\w+[^>]*>','',result.group(1))
            return str
        except:
            print('re not')
        return ''
    str = re.sub(r'</?\w+[^>]*>','',result.group(1))
    return str
