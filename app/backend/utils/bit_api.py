import requests
import json

# 官方文档地址
# https://doc2.bitbrowser.cn/jiekou/ben-di-fu-wu-zhi-nan.html

# 此demo仅作为参考使用，以下使用的指纹参数仅是部分参数，完整参数请参考文档

url = "http://127.0.0.1:54345"
headers = {'Content-Type': 'application/json'}

def createBrowser(host='',port='',noproxy='noproxy'):  # 创建或者更新窗口，指纹参数 browserFingerPrint 如没有特定需求，只需要指定下内核即可，如果需要更详细的参数，请参考文档
    json_data = {
        'name': 'google',  # 窗口名称
        'remark': '',  # 备注
        'proxyMethod': 2,  # 代理方式 2自定义 3 提取IP
        # 代理类型  ['noproxy', 'http', 'https', 'socks5', 'ssh']
        'proxyType': 'noproxy',
        'host': '',  # 代理主机
        'port': '',  # 代理端口
        'proxyUserName': '',  # 代理账号
        'abortImage': False,
        'clearCacheFilesBeforeLaunch': True,
        'randomFingerprint': True,
        "browserFingerPrint": {  # 指纹对象
            'coreVersion': '112',  # 内核版本 112 | 104，建议使用112，注意，win7/win8/winserver 2012 已经不支持112内核了，无法打开
            'ostype': 'PC',
            'os': 'MacIntel',
            'isIpCreateLanguage': False,
            'languages': 'en-SG'
        }
    }

    res = requests.post(f"{url}/browser/update",
                        data=json.dumps(json_data), headers=headers).json()
    if res['success']:
        browserId = res['data']['id']
        print(browserId)
        return browserId
    else:
        return None

def openBrowser(browserId,config=None): # 直接指定ID打开窗口，也可以使用 createBrowser 方法返回的ID 也可传入其他参数
    # 先创建浏览器


    # 初始化json_data字典
    json_data = {"id": browserId}

    # 如果config参数不为None，且是一个字典，将其键值对添加到json_data
    if config and isinstance(config, dict):
        for key, value in config.items():
            json_data[key] = value

    res = requests.post(f"{url}/browser/open",
                        data=json.dumps(json_data), headers=headers).json()
    # print(res)
    # print(res['data']['http'])
    return res



def closeBrowser(id):  # 关闭窗口
    json_data = {'id': f'{id}'}
    requests.post(f"{url}/browser/close",
                  data=json.dumps(json_data), headers=headers).json()


def deleteBrowser(id):  # 删除窗口
    json_data = {'id': f'{id}'}
    print(requests.post(f"{url}/browser/delete",
          data=json.dumps(json_data), headers=headers).json())

def updateBrowser(id):  # 关闭窗口
    fingers = fingerprint(id)
    browserFingerPrint = {  # 指纹对象
                    'coreVersion': '112',  # 内核版本 112 | 104，建议使用112，注意，win7/win8/winserver 2012 已经不支持112内核了，无法打开
                    'ostype': 'PC',
                    'os': 'MacIntel',
                    'isIpCreateLanguage': False,
                    'languages': 'en-SG'
                    }
    if fingers.get('success') == True:
        browserFingerPrint = fingers.get('data')

    json_data = {
        'ids': f'[{id}]',
        'browserFingerPrint': browserFingerPrint
    }
    requests.post(f"{url}/browser/update/partial",
                  data=json.dumps(json_data), headers=headers).json()

def fingerprint(id):
    json_data = {'browserId': f'{id}'}
    fingerprint = requests.post(f"{url}/browser/fingerprint/random",
                  data=json.dumps(json_data), headers=headers).json()
    return fingerprint


