#!/bin/python3
# # -*- coding: utf-8 -*-
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup




def checkThreadIds(type):
    tids = []
    hrefs = {'tcp':'https://keylol.com/forum.php?mod=forumdisplay&fid=234&filter=author&orderby=dateline&typeid=913','t2g':'https://keylol.com/forum.php?mod=forumdisplay&fid=234&filter=author&orderby=dateline&typeid=970'}
    
    update = json.loads(
        open('update.json', 'r', encoding='utf-8').read())
    last_tids = update[type]
    res = requests.get(hrefs[type]).text
    threads = BeautifulSoup(res, 'html.parser').select(
        '#threadlisttableid > tbody')
    for i in range(10):
        result = re.search(r'(\d+)', threads[i].attrs['id'])
        if result:
            tid = result.group(1)
            if not tid in last_tids:
                tids.append(tid)
    for tid in reversed(tids):
        items = getThreadContent(tid,type)
        updateData(type,items)
    if len(tids) > 0:
        tids.extend(last_tids)
        update[type] = tids[:10]
        open('update.json', 'w',
             encoding='utf-8').write(json.dumps(update, ensure_ascii=False))


def getThreadContent(tid,type):
    def readNodeCp(node):
        global discount
        for _node in node.contents:
            if isinstance(_node, str):
                match = re.search(r'(\d+(\.\d+)?)元', _node)
                if match:
                    discount = float(match.group(1))
            elif _node.name == 'a':
                cp_href = re.match(
                    r'https:\/\/chinaplay\.store\/detail\/([\w-]+)\/?', _node.attrs['href'])
                if cp_href:
                    print(cp_href.group(1))
                    items.append([cp_href.group(1), [discount, date]])
            else:
                readNodeCp(_node)
    def readNode2g(node):
        global discount
        for _node in node.contents:
            if isinstance(_node, str):
                match = re.search(r'价格：(\d+(\.\d+)?)', _node)
                if match:
                    print(match)
                    discount = float(match.group(1))
            elif _node.name == 'a':
                cp_href = re.match(
                    r'https:\/\/2game\.hk\/cn\/([\w-]+)\/?', _node.attrs['href'])
                if cp_href:
                    print(cp_href.group(1))
                    items.append([cp_href.group(1), [discount, date]])
            else:
                readNode2g(_node)

    global date
    items = []

    res = requests.get('https://keylol.com/t'+tid+'-1-1').text
    res2 = re.sub(r'</?strong[^>]*>','',re.sub(r'</?span[^>]*>','',res))
    soup = BeautifulSoup(res2, 'html.parser')
    if soup.select_one('.plc .authi em'):
        date = (re.search(r'\d+-\d+-\d+', soup.select_one('.plc .authi em').text) or re.search(
            r'\d+-\d+-\d+', soup.select_one('.plc .authi em span').attrs['title'])).group(0)
        floor1 = soup.select_one('.t_fsz > table .t_f')
        if type == 'tcp':
            readNodeCp(floor1)
        else:
            readNode2g(floor1)
    return items


def updateData(type,items):
    file_name = {'tcp':'datacp.json','t2g':'data2g.json'}
    
    data = json.loads(
        open(file_name[type], 'r', encoding='utf-8').read())
    for kv in items:
        if kv[0] in data:
            new_hist = kv[1]
            old_hist = data[kv[0]]['hist']
            if (datetime.datetime.strptime(new_hist[1], '%Y-%m-%d').date() - datetime.datetime.strptime(old_hist[0][1], '%Y-%m-%d').date()).days < 16:
                if old_hist[0][0] > new_hist[0]:
                    data[kv[0]]['low'] = new_hist
                    data[kv[0]]['hist'][0] = new_hist
            else:
                if data[kv[0]]['low'][0] >= new_hist[0]:
                    data[kv[0]]['low'] = new_hist
                arr = [new_hist]
                arr.extend(old_hist)
                data[kv[0]]['hist'] = arr[:10]
        else:
            data[kv[0]] = {'low': kv[1], 'hist': [kv[1]]}
    open(file_name[type], 'w',
         encoding='utf-8').write(json.dumps(data, ensure_ascii=False, separators=(',', ':')))


def main():
    checkThreadIds('tcp')
    checkThreadIds('t2g')


date = None
discount = 0

if __name__ == '__main__':
    main()
