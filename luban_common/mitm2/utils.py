import requests,yaml,os,pathlib


class Utils:
    def __init__(self):
        pass

    # def setToken(self):
    #     data = self.getConfig()
    #     body = {"password": data['PSW'], "username": data['User'], "loginType": "-1"}
    #     headers = {"Content-Type": "application/json"}
    #     headers['Access-Token'] = requests.post(data['Url'][0], json=body, headers=headers).json()['data']
    #     body = {"epid": 1}
    #     requests.put(data['Url'][1], json=body, headers=headers)
    #     data = requests.get(data['Url'][2], params=None, headers=headers).json()['data']
    #     return data

    def setToken(self):
        data = self.getConfig()
        body = {"password": data['PSW'], "username": data['User'], "loginType": "-1"}
        headers = {"Content-Type": "application/json"}
        headers['Access-Token'] = requests.post(data['Url'][0], json=body, headers=headers).json()['data']
        body = {"epid": 992}
        requests.put(data['Url'][1], json=body, headers=headers)
        return headers['Access-Token']



    def getConfig(self):
        result = {}
        with open('config.yaml', 'r', encoding='utf-8') as file:
            # configInfo = yaml.load(file.read())
            configInfo = yaml.load(file, Loader=yaml.FullLoader)
            file.close()
        result['whetherRecord'], result['path'] = False, []
        if str(configInfo['Setting']['Status']).upper() == 'NOW':
            result['path'], result['whetherRecord'] = ['script.json'], True
        elif str(configInfo['Setting']['Status']).upper() == 'DEBUG':
            for value in configInfo['Setting']['Scope']:
                path = os.getcwd() + os.sep + value
                if not os.path.exists(path):
                    print("测试脚本文件夹没找到，请检查后在执行！")
                else:
                    pathAbs = path + os.sep
                    path_list = pathlib.Path(pathAbs)
                    result['path'] = result['path'] + list(path_list.iterdir())
        else:
            for eachPath in os.listdir():
                if "_测试脚本集" in eachPath:
                    path = os.getcwd() + os.sep + eachPath
                    pathAbs = path + os.sep
                    path_list = pathlib.Path(pathAbs)
                    result['path'] = result['path']+list(path_list.iterdir())
        if result['path'] == []: print("测试脚本文件夹没找到，请检查后在执行！")
        result['Model'] = configInfo['Setting']['Model']
        result['Url'], result['User'], result['PSW'], result['NotifyUser'] = configInfo['Setting']['Url'], \
            configInfo['Setting']['User'], \
            configInfo['Setting']['PSW'], \
            configInfo['Setting']['NotifyUser']
        return result