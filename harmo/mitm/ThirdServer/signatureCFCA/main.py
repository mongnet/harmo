# This is a sample Python script.
import ast
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json,requests,os,yaml
from _global import *

class SignatureCFCA:
    def __init__(self,url,headers,host):
        self.loc = os.path.abspath(os.path.dirname(__file__))
        loc = self.loc+os.sep+'signCFCA.yaml'
        with open(loc,'r',encoding='utf-8') as file:
            self.sign = yaml.load(file,Loader=yaml.FullLoader)
        self.sign['businessId'] = [GLOBAL[key] for key in GLOBAL.keys() if '.id' in key][0]
        self.sign['pdfFileId'] = [GLOBAL[key] for key in GLOBAL.keys() if 'fileId' in key][0]
        self.sign['pdfName'] = "资料测试用.pdf"
        self.sign['processInstanceId'] = [GLOBAL[key] for key in GLOBAL.keys() if 'processInstanceId' in key][0]
        self.sign['processNodeId'] = [GLOBAL[key] for key in GLOBAL.keys() if 'processNodeId' in key][0]
        self.headers = headers
        self.host = host

    def updateSignCFCA(self):
        url = self.host + '/luban-misc/sign/cfca/union/sign'
        res = requests.post(url,json=self.sign,headers=self.headers).json()
        fileId = res['data']['fileId']
        md5 = res['data']['md5']
        size = int(res['data']['size'])
        name = self.sign['pdfName']
        body = {"id":self.sign['businessId'],"fileId":fileId,"md5":md5,"name":name,"size":size}
        url_updateSign = self.host +'/luban-data-manage/common/sign/DATA_FORM/v1/update_sign_file'
        res = requests.post(url_updateSign,json=body,headers=self.headers)
        print('Mock 签名签章结束')
        return res

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    GLOBAL = {
                'resp.data.result.-1.id': 'a45b7718b8044b838dd7353250d91c90',
                'resp.data.result.-1.formInstanceId': '64db2c9ae7ea5d325f43e795',
                'resp.data.result.-1.fileId': 'e7e1e62d8bf74113a7164ffeaf80e8b1',
                'resp.data.result.-1.processInstanceId': '5586107',
                'resp.data.result.-1.fileName': '14a2656d58e84debb9d0139db35491ca.pdf',
                'resp.data.result.-1.md5': '43512070cf9f39a66bc983944dafb508',
                'resp.data.result.-1.processNodeId': 'X84ebefb579b640f690d7d43eaa1d99e8'
            }
    url = r''
    headers = {
        "Access-Token": "eyJhbGciOiJIUzUxMiJ9.eyJsb2dpblR5cGUiOiIxOTIiLCJleHAiOjE2OTI1MjgwNzIsImlhdCI6MTY5MjA5NjA3MiwidXNlcm5hbWUiOiJsYjg4MTdpIn0.1Y4wNr_bKADeIdYBt65GAoUXpm3V0T3J8vEuaXVj4S9wUKhdaGhsQECGXt5LShLWVEyNJJmnWvL2j_yv7sSvOQ",
        "Content-type": "application/json"
    }
    host ='http://service.lbuilder.cn'
    SignatureCFCA(url,headers,host).updateSignCFCA()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
