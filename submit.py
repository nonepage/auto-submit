# coding: utf-8
import configparser
import sys
import requests
import json
import time
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

    wd = webdriver.Chrome(r'd:\chromedriver.exe')
    wd.get('http://authserver.scitc.com.cn/authserver/login?service=https%3A%2F%2Fscitc.cpdaily.com%2Fportal%2Flogin')
    username = wd.find_element_by_id("username")
    username.send_keys(config['xh'])
    password = wd.find_element_by_id('password')
    password.send_keys(config['pwd'])
    password.submit()
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

    form = res.json()['datas']['rows']
    return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}


# 填写form
def fillForm(form):

    form=[{"wid":"2231","formWid":"98","fieldType":2,"title":"你的学生类别","description":"","minLength":0,"sort":"1","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field001","value":"专科生","fieldItems":[{"itemWid":"8540","content":"专科生","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2232","formWid":"98","fieldType":2,"title":"你的生源地","description":"","minLength":0,"sort":"2","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field002","value":"内地","fieldItems":[{"itemWid":"8544","content":"内地","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2233","formWid":"98","fieldType":2,"title":"你是否有疑似/确诊新冠肺炎？","description":"","minLength":0,"sort":"3","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field003","value":"否","fieldItems":[{"itemWid":"8547","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2234","formWid":"98","fieldType":2,"title":"你是否有发热、咳嗽等症状","description":"","minLength":0,"sort":"4","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field004","value":"否","fieldItems":[{"itemWid":"8551","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2235","formWid":"98","fieldType":2,"title":"你是否就诊或住院","description":"","minLength":0,"sort":"5","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field005","value":"否","fieldItems":[{"itemWid":"8552","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2236","formWid":"98","fieldType":1,"title":"如果就诊或住院，请填写你去的医院名称（未就诊、住院的不填）","description":"","minLength":1,"sort":"6","maxLength":300,"isRequired":0,"imageCount":null,"hasOtherItems":0,"colName":"field006","value":"","fieldItems":[]},{"wid":"2237","formWid":"98","fieldType":2,"title":"你当前是否被隔离？","description":"","minLength":0,"sort":"7","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field007","value":"否","fieldItems":[{"itemWid":"8556","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2238","formWid":"98","fieldType":2,"title":"如果被隔离，请选择你的隔离方式（未被隔离的不填）","description":"","minLength":0,"sort":"8","maxLength":null,"isRequired":0,"imageCount":null,"hasOtherItems":0,"colName":"field008","value":"","fieldItems":[null]},{"wid":"2239","formWid":"98","fieldType":1,"title":"如果被隔离，请填写目前被隔离的详细地址（未被隔离的不填）","description":"省、市、区/县、具体地址，如江苏省南京市江宁区利源南路55号1幢1单元202室","minLength":1,"sort":"9","maxLength":300,"isRequired":0,"imageCount":null,"hasOtherItems":0,"colName":"field009","value":"","fieldItems":[]},{"wid":"2240","formWid":"98","fieldType":2,"title":"春节期间是否在校","description":"","minLength":0,"sort":"10","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field010","value":"否","fieldItems":[{"itemWid":"8560","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2241","formWid":"98","fieldType":2,"title":"目前是否在校","description":"","minLength":0,"sort":"11","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field011","value":"否","fieldItems":[{"itemWid":"8562","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2242","formWid":"98","fieldType":1,"title":"你目前所在城市","description":"","minLength":1,"sort":"12","maxLength":300,"isRequired":1,"imageCount":-2,"hasOtherItems":0,"colName":"field012","value":"四川省/成都市/新都区","fieldItems":[],"area1":"四川省","area2":"成都市","area3":"新都区"},{"wid":"2243","formWid":"98","fieldType":2,"title":"是否已返回或从未离开学校所在的城市","description":"","minLength":0,"sort":"13","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field013","value":"否","fieldItems":[{"itemWid":"8564","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2244","formWid":"98","fieldType":2,"title":"是否确定返回学校时间","description":"","minLength":0,"sort":"14","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field014","value":"否","fieldItems":[{"itemWid":"8566","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2245","formWid":"98","fieldType":1,"title":"如果已确定，请选择你的返回时间（未确定的不填）","description":"","minLength":1,"sort":"15","maxLength":300,"isRequired":0,"imageCount":-1,"hasOtherItems":0,"colName":"field015","value":"","fieldItems":[],"date":"","time":""},{"wid":"2246","formWid":"98","fieldType":2,"title":"近1个月是否去过湖北或接触过湖北地区人士","description":"","minLength":0,"sort":"16","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field016","value":"否","fieldItems":[{"itemWid":"8568","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2247","formWid":"98","fieldType":2,"title":"近1个月是否接触过确诊病例","description":"","minLength":0,"sort":"17","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field017","value":"否","fieldItems":[{"itemWid":"8570","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2248","formWid":"98","fieldType":2,"title":"近1个月是否接触过疑似病例","description":"","minLength":0,"sort":"18","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field018","value":"否","fieldItems":[{"itemWid":"8572","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2249","formWid":"98","fieldType":2,"title":"如果有密切接触，请选择你和密切接触者（疑似/确诊/湖北）的关系（没有接触的不填）","description":"","minLength":0,"sort":"19","maxLength":null,"isRequired":0,"imageCount":null,"hasOtherItems":0,"colName":"field019","value":"","fieldItems":[null]},{"wid":"2250","formWid":"98","fieldType":2,"title":"过去14天是否有共同居住者（家属或合租者）从其他城市返回的情况","description":"","minLength":0,"sort":"20","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field020","value":"否","fieldItems":[{"itemWid":"8576","content":"否","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2251","formWid":"98","fieldType":1,"title":"如果有，请选择共同居住者是从哪个城市（国家）返回的？（上一题如选\"否\"此题不填）","description":"","minLength":1,"sort":"21","maxLength":300,"isRequired":0,"imageCount":-2,"hasOtherItems":0,"colName":"field021","value":"","fieldItems":[],"area1":"","area2":"","area3":""},{"wid":"2252","formWid":"98","fieldType":2,"title":"你今天的体温是多少","description":"","minLength":0,"sort":"22","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field022","value":"36~37.2℃","fieldItems":[{"itemWid":"8577","content":"36~37.2℃","isOtherItems":0,"contendExtend":"","isSelected":1}]},{"wid":"2253","formWid":"98","fieldType":2,"title":"本人是否承诺以上所填报的全部内容均属实、准确，不存在任何隐瞒与不实的情况，更无遗漏之处","description":"","minLength":0,"sort":"23","maxLength":null,"isRequired":1,"imageCount":null,"hasOtherItems":0,"colName":"field023","value":"是","fieldItems":[{"itemWid":"8580","content":"是","isOtherItems":0,"contendExtend":"","isSelected":1}]}]

    return form


# 提交表单
def submitForm(formWid, address, collectWid, schoolTaskWid, form, cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
        'CpdailyStandAlone': '0',
        'extension': '1',
        'Cpdaily-Extension': '1wAXD2TvR72sQ8u+0Dw8Dr1Qo1jhbem8Nr+LOE6xdiqxKKuj5sXbDTrOWcaf v1X35UtZdUfxokyuIKD4mPPw5LwwsQXbVZ0Q+sXnuKEpPOtk2KDzQoQ89KVs gslxPICKmyfvEpl58eloAZSZpaLc3ifgciGw+PIdB6vOsm2H6KSbwD8FpjY3 3Tprn2s5jeHOp/3GcSdmiFLYwYXjBt7pwgd/ERR3HiBfCgGGTclquQz+tgjJ PdnDjA==',
        'Content-Type': 'application/json; charset=utf-8',
        'Host': 'yibinu.cpdaily.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    # 默认正常的提交参数json
    params = {"formWid": formWid, "address": address, "collectWid": collectWid, "schoolTaskWid": schoolTaskWid,
              "form": form}

    r = requests.post("http:/scitc.cpdaily.com/wec-counselor-collector-apps/stu/collector/submitForm",
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
                log('无需重启脚本，1小时后，脚本将自动重新尝试。。。')
                exit(-1)
            log('查询最新待填写问卷成功。。。')
            log('正在自动填写问卷。。。')
            form = fillForm(params['form'])
            log('填写问卷成功。。。')
            log('正在自动提交。。。')
            msg = submitForm(params['formWid'], config['address'], params['collectWid'], params['schoolTaskWid'], form,
                             cookies)
            if msg == 'SUCCESS':
                log('自动提交成功！24小时后，脚本将再次自动提交。。。')
                exit(-1)
            elif msg == '该收集已填写无需再次填写':
                log('今日已提交！24小时后，脚本将再次自动提交。。。')
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
