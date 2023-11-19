#!/bin/python3
# # -*- coding: utf-8 -*-
import re
import json
import time
import requests
from bs4 import BeautifulSoup


def checkThreadIds():
    update = json.loads(open('F:/keylol-chinaplay-table/update.json', 'r', encoding='utf-8').read())
    last_tids = update['tids']
    tids = []
    res = requests.get(
        'https://keylol.com/forum.php?mod=forumdisplay&fid=234&filter=author&orderby=dateline&typeid=913').text
    threads = BeautifulSoup(res, 'html.parser').select(
        '#threadlisttableid > tbody')
    for i in range(10):
        result = re.search(r'(\d+)', threads[i].attrs['id'])
        if result:
            tid = result.group(1)
            if not tid in last_tids:
                getThreadContent(tid)
                tids.append(tid)
    tids.extend(last_tids)
    update = {'date': int(time.time()), 'tids': tids[:10]}
    open('F:/keylol-chinaplay-table/update.json', 'w',
         encoding='utf-8').write(json.dumps(update, ensure_ascii=False))


def getThreadContent(tid):
    global date
    res = requests.get('https://keylol.com/t'+tid+'-1-1').text
    soup = BeautifulSoup(res, 'html.parser')
    date = re.search(r'\d+-\d+-\d+', soup.select_one('.plc .authi em').text) or re.search(
        r'\d+-\d+-\d+', soup.select_one('.plc .authi em span').attrs['title']).group(0)
    floor1 = soup.select_one('.t_fsz > table .t_f')
    readNode(floor1)


def readNode(node):
    global discount
    global date
    global items
    if isinstance(node, str):
        match = re.search(r'(\d+(\.\d+)?)元', node)
        if match:
            discount = float(match.group(1))
    else:
        if node.name == 'a':
            cp_href = re.match(
                r'https:\/\/chinaplay\.store\/detail\/(\S+)\/', node.attrs['href'])
            if cp_href:
                items.append([cp_href.group(1), [discount, date]])
        else:
            for _node in node.contents:
                readNode(_node)


def updateData():
    global items
    history = json.loads(open('F:/keylol-chinaplay-table/data.json', 'r', encoding='utf-8').read())
    for item in items:
        if item[0] in history:
            hist = [item[1]]
            hist.extend(history[item[0]]['hist'])
            hist = hist[:10]
            if item[1][0] <= history[item[0]]['low'][0]:
                history[item[0]] = {'low': item[1], 'hist': hist}
            history[item[0]]['hist'] = hist
        else:
            history[item[0]] = {'low': [item[1], item[2]],
                                'hist': [item[1], item[2]]}
    open('F:/keylol-chinaplay-table/data.json', 'w',
         encoding='utf-8').write(json.dumps(history, ensure_ascii=False, separators=(',', ':')))


def main():
    checkThreadIds()
    updateData()


date = None
discount = 0
items = []

if __name__ == '__main__':
    main()
