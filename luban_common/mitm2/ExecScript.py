import importlib

from NoiseReduction import *
import copy,requests
from utils import Utils
import time,os,json,yaml


class ExecScript:
    def __init__(self,scriptPath):
        #self.scriptPathlist = NoiseReduction().scriptPathlist
        data = NoiseReduction().getRules(scriptPath)
        self.rulesDoc = data['rulesDoc']
        self.rulesIgnoreExect = data['rulesIgnoreExect']
        self.rulesIgnoreContain = data['rulesIgnoreContain']
        self.rulesGet = data['rulesGet']
        with open('config.yaml', 'r', encoding='utf-8') as file:
            configInfo = yaml.load(file, Loader=yaml.FullLoader)
        self.host = configInfo['Setting']['Host']

    def updateToken(self,data):
        checkToken = False
        access_token = Utils().setToken()
        for each in data:
            if 'access-token' in each['headers'].keys() and checkToken ==False:
                data = eval(str(data).replace(str(each['headers']['access-token']),access_token))
                checkToken = True
        return data

    def callAPI(self,flowData):
        if 'MOCK' in str(flowData['method']).upper():
            mock_list = str(flowData['location']).split('.')
            module = importlib.import_module('.'.join(mock_list[:3]))
            module_class = getattr(module,mock_list[-2])
            obj = module_class(flowData['flow']['url'],flowData['flow']['headers'],self.host)
            Mock_fun = getattr(obj,mock_list[-1])
            Mock_fun()
            result = None
        if 'GET' == str(flowData['method']).upper():
            result = requests.get(flowData['url'], headers=flowData['headers'])
        if 'POST' == str(flowData['method']).upper():
            if 'Content-Type' in dict(flowData['headers']).keys():
                if 'multipart/form-data' not in dict(flowData['headers'])['Content-Type']:
                    result = requests.post(flowData['url'], json=flowData['body'],headers=flowData['headers'])
                else:
                    rulesDocPaths = [eachPath['Path'] for eachPath in self.rulesDoc]
                    if flowData['path'] in rulesDocPaths:
                        path = os.path.dirname(os.path.abspath(__file__)) + os.sep + self.rulesDoc[int(rulesDocPaths.index(flowData['path']))]['DOC']
                        docName = self.rulesDoc[int(rulesDocPaths.index(flowData['path']))]['DOC']
                        fileinfo = {"file": (docName, open(path, "rb"), "image/png")}
                        result = requests.post(flowData['url'], files=fileinfo)
                    else:
                        print("脚本错误:上传附件接口报错！")

            else:
                result = requests.post(flowData['url'], json=flowData['body'], headers=flowData['headers'])
        if 'DELETE' == str(flowData['method']).upper():
            result = requests.delete(flowData['url'], headers=flowData['headers'])
        if 'PUT' == str(flowData['method']).upper():
            result = requests.put(flowData['url'], json=flowData['body'], headers=flowData['headers'])
        try:
            print(flowData['url'])
            print(flowData['body'])
            print(flowData['id'])
        except:
            pass
        return result

