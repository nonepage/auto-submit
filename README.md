## 功能描述
全自动提交今日校园防疫表单。

### 开发环境
- Pycharm x64
- Python 3.8.5

### 依赖安装
`pip install -i https://pypi.doubanio.com/simple/ -r requirements.txt`
### 接口使用
请求代码示例

```python
import requests

# POST
    data = {
        'username': 'xxxx',  # 填写你的用户名
        'password': 'xxxx',  # 填写你的密码
        'gpsaddress': '四川省成都市金牛区XXX', #GPS定位地址
        'Sheng': '四川省',
        'Shi': '成都市',
        'Qu': '金牛区'
    }
requests.post('http://xxxx:8001/run/', params=data)

```
| 请求方式  | 参数 | 说明 | 是否必须 |
| ------------ | ------------ | ------------ | ------------ |
| username | 学号 |   | 是 |
| password | 密码 |   | 是 |
| gpsaddress | GPS定位地址 |   | 是 |
| Sheng | 省份  |   | 是 |
| Shi | 市 |   | 是 |
| Qu | 区 |   | 是 |
