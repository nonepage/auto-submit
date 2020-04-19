# coding: utf-8
import configparser
import sys
import requests
import json
import time
import os
from selenium import webdriver

# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ' + str(content))
    sys.stdout.flush()


# 读取配置
def getConfig(file='config.ini'):
    config = configparser.ConfigParser()
    config.read(file, encoding='utf-8')


    xh = config['user']['xh']
    pwd = config['user']['pwd']
    address = config['user']['address']
    return {"xh": xh, "pwd": pwd, "address": address}


# 登陆并获取cookies
def getCookies(config):
    from selenium import webdriver

    hear = os.getcwd() + '\\chromedriver.exe'
    wd = webdriver.Chrome(hear)
    wd.get('http://authserver.scitc.com.cn/authserver/login?service=https%3A%2F%2Fscitc.cpdaily.com%2Fportal%2Flogin')
    username = wd.find_element_by_id("username")
    username.send_keys(config['xh'])
    password = wd.find_element_by_id('password')
    password.send_keys(config['pwd'])
    password.submit()
    time.sleep(2)
    cookie = wd.get_cookies()
    cookies = {cookie[0]['name']: cookie[0]['value'], cookie[1]['name']: cookie[1]['value']}
    wd.quit()
    return cookies


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
def fillForm(form):
    form[0]['value'] = "专科生"
    del form[0]['fieldItems'][1]
    del form[0]['fieldItems'][1]
    del form[0]['fieldItems'][1]
    form[1]['value']='内地'
    del form[1]['fieldItems'][1]
    del form[1]['fieldItems'][1]
    form[2]['value'] = '否'
    del form[2]['fieldItems'][1]
    del form[2]['fieldItems'][1]
    form[3]['value']='否'
    del form[3]['fieldItems'][0]
    form[4]['value']='否'
    del form[4]['fieldItems'][1]
    del form[4]['fieldItems'][1]
    form[6]['value'] = '否'
    del form[6]['fieldItems'][0]
    form[7]['fieldItems']=[None]
    form[9]['value']='否'
    del form[9]['fieldItems'][0]
    form[10]['value']='否'
    del form[10]['fieldItems'][0]
    form[11]['area1']='四川省'
    form[11]['area2'] = '成都市'
    form[11]['area3'] = '新都区'
    form[12]['value']='否'
    del form[12]['fieldItems'][0]
    form[13]['value']='否'
    del form[13]['fieldItems'][0]
    form[14]['date'] = ""
    form[14]['time'] = ""
    form[15]['value']='否'
    del form[15]['fieldItems'][0]
    form[16]['value'] = '否'
    del form [16]['fieldItems'][0]
    form[17]['value'] = '否'
    del form[17]['fieldItems'][0]
    form[18]['fieldItems']=[None]
    form[19]['value'] = '否'
    del form[19]['fieldItems'][0]
    form[20]["area1"] = ""
    form[20]["area2"] = ""
    form[20]["area3"] = ""
    form[21]['value'] = '36~37.2℃'
    del form[21]['fieldItems'][1]
    del form[21]['fieldItems'][1]
    form[22]['value'] = '是'
    del form[22]['fieldItems'][1]
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
                exit(-1)
            elif msg == '该收集已填写无需再次填写':
                log('今日已提交！')
                exit(-1)
            else:
                log('自动提交失败。。。')
                log('错误是' + msg)
                exit(-1)
        else:
            log('模拟登陆失败。。。')
            log('原因可能是学号或密码错误，请检查配置后，重启脚本。。。')
            exit(-1)


if __name__ == '__main__':
    main()
