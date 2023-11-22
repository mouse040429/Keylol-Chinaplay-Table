#!/bin/python3
# # -*- coding: utf-8 -*-
import re
import json
import time
import datetime
import requests
from bs4 import BeautifulSoup


def checkThreadIds():
    update = json.loads(
        open('F:/keylol-chinaplay-table/update.json', 'r', encoding='utf-8').read())
    last_tids = update['tids']
    tids = []
    res = requests.get(
        'https://keylol.com/forum.php?mod=forumdisplay&fid=234&filter=author&orderby=dateline&typeid=913').text
    threads = BeautifulSoup(res, 'html.parser').select(
        '#threadlisttableid > tbody')
    for i in range(12):
        result = re.search(r'(\d+)', threads[i].attrs['id'])
        if result:
            tid = result.group(1)
            if not tid in last_tids:
                tids.append(tid)
    for tid in reversed(tids):
        items = getThreadContent(tid)
        updateData(items)
    tids.extend(last_tids)
    update = {'date': int(time.time()), 'tids': tids[:12]}
    open('F:/keylol-chinaplay-table/update.json', 'w',
         encoding='utf-8').write(json.dumps(update, ensure_ascii=False))


def getThreadContent(tid):
    global date
    items = []

    def readNode(node):
        global discount
        for _node in node.contents:
            if isinstance(_node, str):
                match = re.search(r'(\d+(\.\d+)?)元', _node)
                if match:
                    discount = float(match.group(1))
            elif _node.name == 'a':
                cp_href = re.match(
                    r'https:\/\/chinaplay\.store\/detail\/(\S+)\/', _node.attrs['href'])
                if cp_href:
                    print(cp_href.group(1))
                    items.append([cp_href.group(1), [discount, date]])
            else:
                readNode(_node)
    res = requests.get('https://keylol.com/t'+tid+'-1-1').text
    soup = BeautifulSoup(res, 'html.parser')
    if soup.select_one('.plc .authi em'):
        date = (re.search(r'\d+-\d+-\d+', soup.select_one('.plc .authi em').text) or re.search(
            r'\d+-\d+-\d+', soup.select_one('.plc .authi em span').attrs['title'])).group(0)
        floor1 = soup.select_one('.t_fsz > table .t_f')
        readNode(floor1)
    return items


def updateData(items):
    data = json.loads(
        open('F:/keylol-chinaplay-table/data.json', 'r', encoding='utf-8').read())
    for kv in items:
        if kv[0] in data:
            new_hist = kv[1]
            if new_hist[0] <= data[kv[0]]['low'][0]:
                data[kv[0]]['low'] = new_hist
            _hist = data[kv[0]]['hist']
            if (datetime.datetime.strptime(new_hist[1], '%Y-%m-%d').date() - datetime.datetime.strptime(_hist[-1][1], '%Y-%m-%d').date()).days < 16:
                if _hist[0][0] > new_hist[0]:
                    _hist[0] = new_hist
            else:
                arr = [new_hist]
                arr.extend(_hist)
                data[kv[0]]['hist'] = arr[:10]
        else:
            data[kv[0]] = {'low': kv[1], 'hist': [kv[1]]}
    open('F:/keylol-chinaplay-table/data.json', 'w',
         encoding='utf-8').write(json.dumps(data, ensure_ascii=False, separators=(',', ':')))


def main():
    checkThreadIds()


date = None
discount = 0

if __name__ == '__main__':
    main()
