# coding: utf-8
import sys
import time

import requests
import json
import re
import random
import base64
import math
import uvicorn
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from fastapi import FastAPI
from lxml import etree

# 模拟前端CryptoJS加密
aes_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
aes_chars_len = len(aes_chars)


def randomString(len):
    retStr = ''
    i = 0
    while i < len:
        retStr += aes_chars[(math.floor(random.random() * aes_chars_len))]
        i = i + 1
    return retStr


def add_to_16(s):
    while len(s) % 16 != 0:
        s += '\0'
    return str.encode(s, 'utf-8')


def getAesString(data, key, iv):  # AES-128-CBC加密模式，key需要为16位，key和iv可以一样
    key = re.sub('/(^\s+)|(\s+$)/g', '', key)
    aes = AES.new(str.encode(key), AES.MODE_CBC, str.encode(iv))
    pad_pkcs7 = pad(data.encode('utf-8'), AES.block_size, style='pkcs7')  # 选择pkcs7补全
    encrypted = aes.encrypt(pad_pkcs7)
    # print(encrypted)
    return str(base64.b64encode(encrypted), 'utf-8')


def encryptAES(data, aesKey):
    encrypted = getAesString(randomString(64) + data, aesKey, randomString(16))
    return encrypted


# 登陆并获取cookies
def getCookies(config):
    server = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.16 Safari/537.36 Edg/79.0.309.12'
    }
    login_html = server.get(
        'http://authserver.scitc.com.cn/authserver/login?service=https%3A%2F%2Fscitc.cpdaily.com%2Fportal%2Flogin',
        headers=headers).text
    html = etree.HTML(login_html)
    element = html.xpath('/html/script')[1].text  # 获取加密密钥

    # 获取表单项
    pwdDefaultEncryptSalt = element.split('\"')[3].strip()
    lt = html.xpath("//input[@type='hidden' and @name='lt']")[0].attrib['value']
    dllt = html.xpath("//input[@type='hidden' and @name='dllt']")[0].attrib['value']
    execution = html.xpath("//input[@type='hidden' and @name='execution']")[0].attrib['value']
    rmShown = html.xpath("//input[@type='hidden' and @name='rmShown']")[0].attrib['value']

    password = encryptAES(config['pwd'], pwdDefaultEncryptSalt)  # 加密密码
    params = {
        "username": config['xh'],
        "password": password,
        "lt": lt,
        "dllt": dllt,
        "execution": execution,
        "_eventId": "submit",
        "rmShown": rmShown
    }
    while True:
        res = server.post(
            'http://authserver.scitc.com.cn/authserver/login?service=https%3A%2F%2Fscitc.cpdaily.com%2Fportal%2Flogin',
            data=params, headers=headers)
        # 登陆成功后获取cookie (MOD_AUTH_CAS项)
        if server.cookies.get('MOD_AUTH_CAS') is not None:
            break
    cookies = server.cookies
    return cookies


# 表单填写检测
def agin(cookies):
    queryCollectWidUrl = 'https://scitc.cpdaily.com/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 yiban/8.1.11 cpdaily/8.1.11 wisedu/8.1.11',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Content-Type': 'application/json;charset=UTF-8'
    }

    params = {
        'pageSize': 6,
        'pageNumber': 1
    }

    res = requests.post(queryCollectWidUrl, headers=headers, cookies=cookies, data=json.dumps(params))
    print(res.json()['datas']['rows'])


# 查询表单
def queryForm(cookies):
    queryCollectWidUrl = 'https://scitc.cpdaily.com/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 yiban/8.1.11 cpdaily/8.1.11 wisedu/8.1.11',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Content-Type': 'application/json;charset=UTF-8'
    }

    params = {
        'pageSize': 6,
        'pageNumber': 1
    }
    while True:
        res = requests.post(queryCollectWidUrl, headers=headers, cookies=cookies, data=json.dumps(params))
        if len(res.json()['datas']['rows']) >= 1:
            break

    collectWid = res.json()['datas']['rows'][0]['wid']
    formWid = res.json()['datas']['rows'][0]['formWid']

    res = requests.post(url='https://scitc.cpdaily.com/wec-counselor-collector-apps/stu/collector/detailCollector',
                        headers=headers, cookies=cookies, data=json.dumps({"collectorWid": collectWid}))
    schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']

    res = requests.post(url='https://scitc.cpdaily.com/wec-counselor-collector-apps/stu/collector/getFormFields',
                        headers=headers, cookies=cookies, data=json.dumps(
            {"pageSize": 10, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}))

    form_1 = res.json()['datas']['rows']

    res = requests.post(url='https://scitc.cpdaily.com/wec-counselor-collector-apps/stu/collector/getFormFields',
                        headers=headers, cookies=cookies, data=json.dumps(
            {"pageSize": 10, "pageNumber": 2, "formWid": formWid, "collectorWid": collectWid}))
    form_2 = res.json()['datas']['rows']

    res = requests.post(url='https://scitc.cpdaily.com/wec-counselor-collector-apps/stu/collector/getFormFields',
                        headers=headers, cookies=cookies, data=json.dumps(
            {"pageSize": 10, "pageNumber": 3, "formWid": formWid, "collectorWid": collectWid}))
    form_3 = res.json()['datas']['rows']

    form = form_1 + form_2 + form_3

    return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}


# 填写form
def fillForm(form, Sheng, Shi, Qu):
    # form[0]['value'] = "专科生"
    # del form[0]['fieldItems'][1]
    # del form[0]['fieldItems'][1]
    # del form[0]['fieldItems'][1]
    #
    # form[1]['value'] = '内地'
    # del form[1]['fieldItems'][1]
    # del form[1]['fieldItems'][1]
    #
    # form[2]['value'] = '否'
    # del form[2]['fieldItems'][1]
    # del form[2]['fieldItems'][1]
    #
    # form[3]['value'] = '否'
    # del form[3]['fieldItems'][0]
    # form[4]['value'] = '否'
    # del form[4]['fieldItems'][1]
    # del form[4]['fieldItems'][1]
    #
    # # del form[4]['fieldItems'][1]
    #
    # form[6]['value'] = '否'
    # del form[6]['fieldItems'][0]
    #
    # form[7]['fieldItems'] = [None]
    #
    # form[9]['value'] = '否'
    # del form[9]['fieldItems'][0]
    #
    # form[10]['value'] = '否'
    # del form[10]['fieldItems'][0]
    # form[11]['area1'] = Sheng
    # form[11]['area2'] = Shi
    # form[11]['area3'] = Qu
    #
    # form[12]['value'] = '否'
    # del form[12]['fieldItems'][0]
    #
    # form[13]['value'] = '否'
    # del form[13]['fieldItems'][0]
    #
    # form[14]['date'] = ""
    # form[14]['time'] = ""
    #
    # form[15]['value'] = '否'
    # del form[15]['fieldItems'][0]
    #
    # form[16]['value'] = '否'
    # del form[16]['fieldItems'][0]
    #
    # form[17]['value'] = '否'
    # del form[17]['fieldItems'][0]
    #
    # form[18]['fieldItems'] = [None]
    #
    # form[19]['value'] = '否'
    # del form[19]['fieldItems'][0]
    #
    # form[20]["area1"] = ""
    # form[20]["area2"] = ""
    # form[20]["area3"] = ""
    #
    # form[21]['value'] = '36~37.2℃'
    # del form[21]['fieldItems'][1]
    # del form[21]['fieldItems'][1]
    #
    # form[22]['value'] = '是'
    # del form[22]['fieldItems'][1]
    form[0]['value'] = "<37.3℃"
    del form[0]['fieldItems'][1]
    form[1]['value'] = '36.3'
    form[2]['value'] = '正常'

    form[3]['value'] = '否'
    del form[3]['fieldItems'][0]

    form[4]['value'] = '否'
    del form[4]['fieldItems'][0]

    form[5]['value'] = '是'
    del form[5]['fieldItems'][1]

    return form


# 提交表单
def submitForm(formWid, address, collectWid, schoolTaskWid, form, cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
        'CpdailyStandAlone': '0',
        'extension': '1',
        'Cpdaily-Extension': '1wAXD2TvR72sQ8u+0Dw8Dr1Qo1jhbem8Nr+LOE6xdiqxKKuj5sXbDTrOWcaf v1X35UtZdUfxokyuIKD4mPPw5LwwsQXbVZ0Q+sXnuKEpPOtk2KDzQoQ89KVs gslxPICKmyfvEpl58eloAZSZpaLc3ifgciGw+PIdB6vOsm2H6KSbwD8FpjY3 3Tprn2s5jeHOp/3GcSdmiFLYwYXjBt7pwgd/ERR3HiBfCgGGTclquQz+tgjJ PdnDjA==',
        'Content-Type': 'application/json; charset=utf-8',
        'Host': 'scitc.cpdaily.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    # 默认正常的提交参数json
    params = {"formWid": formWid, "address": address, "collectWid": collectWid, "schoolTaskWid": schoolTaskWid,
              "form": form}

    r = requests.post("http://scitc.cpdaily.com/wec-counselor-collector-apps/stu/collector/submitForm",
                      headers=headers, cookies=cookies, data=json.dumps(params))
    msg = r.json()['message']
    return msg


# '四川省广元市利州区滨河北路二段'
def main(username, password, gpsaddress, Sheng, Shi, Qu):
    config = {"xh": username, "pwd": password, "address": gpsaddress}
    cookies = getCookies(config)
    print(cookies.get('MOD_AUTH_CAS'))
    if str(cookies) != 'None':
        try:
            params = queryForm(cookies)
            # print(params)
            if params != None:
                form = fillForm(params['form'], Sheng, Shi, Qu)
                msg = submitForm(params['formWid'], config['address'], params['collectWid'], params['schoolTaskWid'],
                                 form, cookies)
                if msg == 'SUCCESS':
                    return '自动提交完成'  # 自动提交完成
                elif msg == '该收集已填写无需再次填写':
                    return '已完成无需重复提交'  # 已完成无需重复提交
                else:
                    return '提交错误'  # 提交错误
            # 如果没有获取到数据
            else:
                return "获取问卷数据失败"  # 获取问卷数据失败
        except Exception as e:
            return "未知错误" + str(e)  # 未知错误


app = FastAPI()


@app.post("/run/")
def sign(username: str, password: str, gpsaddress: str, Sheng: str, Shi: str, Qu: str):
    return [main(username, password, gpsaddress, Sheng, Shi, Qu)]


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001)
