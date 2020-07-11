# coding: utf-8
import configparser
import sys
import requests
import json
import time
import os
import re
import random
import base64
import math
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from lxml import etree



# 模拟前端CryptoJS加密
aes_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
aes_chars_len = len(aes_chars)
def randomString(len):
  retStr = ''
  i=0
  while i < len:
    retStr += aes_chars[(math.floor(random.random() * aes_chars_len))]
    i=i+1
  return retStr

def add_to_16(s):
    while len(s) % 16 != 0:
        s += '\0'
    return str.encode(s,'utf-8')

def getAesString(data,key,iv):  # AES-128-CBC加密模式，key需要为16位，key和iv可以一样
    key = re.sub('/(^\s+)|(\s+$)/g', '', key)
    aes = AES.new(str.encode(key),AES.MODE_CBC,str.encode(iv))
    pad_pkcs7 = pad(data.encode('utf-8'), AES.block_size, style='pkcs7')  # 选择pkcs7补全
    encrypted =aes.encrypt(pad_pkcs7)
    # print(encrypted)
    return str(base64.b64encode(encrypted),'utf-8')

def encryptAES(data,aesKey):
    encrypted =getAesString(randomString(64)+data,aesKey,randomString(16))
    return encrypted
# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ' + str(content))
    sys.stdout.flush()


# 读取配置
def getConfig():
    fo = open("init.txt", "a+")
    fo.seek(0)
    xh = fo.readline().strip('\n')
    pwd = fo.readline().strip('\n')
    address = fo.readline()
    if xh == '':
        print("第一次初始化")
        xh = input("账号：")
        pwd = input("密码：")
        address = input("地址（例如：中国xx省xx市xx区）:")
        write_f = [xh, "\n", pwd, '\n', address]
        fo.writelines(write_f)
        fo.close()

    return {"xh": xh, "pwd": pwd, "address": address}


# 登陆并获取cookies
def getCookies(config):
    server = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.16 Safari/537.36 Edg/79.0.309.12'
    }
    login_html = server.get('http://authserver.scitc.com.cn/authserver/login?service=https%3A%2F%2Fscitc.cpdaily.com%2Fportal%2Flogin', headers=headers).text
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

    res = server.post('http://authserver.scitc.com.cn/authserver/login?service=https%3A%2F%2Fscitc.cpdaily.com%2Fportal%2Flogin', data=params, headers=headers)
    # 登陆成功后获取cookie (MOD_AUTH_CAS项)
    cookies = server.cookies
    return cookies

#表单填写检测
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

    res = requests.post(queryCollectWidUrl, headers=headers, cookies=cookies, data=json.dumps(params))

    if len(res.json()['datas']['rows']) < 1:
        return None

    collectWid = res.json()['datas']['rows'][0]['wid']
    formWid = res.json()['datas']['rows'][0]['formWid']

    res = requests.post(url='https://scitc.cpdaily.com/wec-counselor-collector-apps/stu/collector/detailCollector',
                        headers=headers, cookies=cookies, data=json.dumps({"collectorWid": collectWid}));
    schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']

    res = requests.post(url='https://scitc.cpdaily.com/wec-counselor-collector-apps/stu/collector/getFormFields',
                        headers=headers, cookies=cookies, data=json.dumps(
            {"pageSize": 10, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}))

    form = res.json()['datas']['rows']

    return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}


# 填写form
def fillForm(form):
    form[0]['value'] = "<37.3℃"
    del form[0]['fieldItems'][1]
    form[1]['value']='36.5'
    form[2]['value'] = '正常'
    del form[2]['fieldItems'][1]
    del form[2]['fieldItems'][1]
    del form[2]['fieldItems'][1]
    del form[2]['fieldItems'][1]
    del form[2]['fieldItems'][1]
    del form[2]['fieldItems'][1]
    form[3]['value']='雪峰校区5#公寓'
    del form[3]['fieldItems'][0]
    del form[3]['fieldItems'][0]
    del form[3]['fieldItems'][0]
    del form[3]['fieldItems'][0]
    del form[3]['fieldItems'][1]
    del form[3]['fieldItems'][1]
    del form[3]['fieldItems'][1]
    form[4]['value']='5412'
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


def main():
    config = getConfig()
    while True:
        log('脚本开始执行。。。')
        cookies = getCookies(config)
        if str(cookies) != 'None':
            log('模拟登陆成功。。。')
            log('正在查询最新待填写问卷。。。')
            params = queryForm(cookies)
            if str(params) == 'None':
                log('获取最新待填写问卷失败，可能是辅导员还没有发布。。。')
                time.sleep(5)
                exit(-1)
            log('查询最新待填写问卷成功。。。')
            log('正在自动填写问卷。。。')
            form = fillForm(params['form'])
            log('填写问卷成功。。。')
            log('正在自动提交。。。')
            msg = submitForm(params['formWid'], config['address'], params['collectWid'], params['schoolTaskWid'], form,
                             cookies)
            if msg == 'SUCCESS':
                log('自动提交成功！')
                agin(cookies)
                time.sleep(5)
                exit(-1)
            elif msg == '该收集已填写无需再次填写':
                log('今日已提交！')
                agin(cookies)
                time.sleep(5)
                exit(-1)
            else:
                log('自动提交失败。。。')
                log('错误是' + msg)
                time.sleep(5)
                exit(-1)
        else:
            log('模拟登陆失败。。。')
            log('原因可能是学号或密码错误，请检查配置后，重启脚本。。。')
            time.sleep(5)
            exit(-1)


if __name__ == '__main__':
    main()
