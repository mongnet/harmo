# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json,requests,os,yaml


class AdvanceForm:
    def __init__(self,url,headers,host):
        self.formUrl = requests.get(url,params=None,headers=headers).json()['data']['url']
        self.AccessToken = str(str(self.formUrl).split('&token=')[1]).split('&refreshToken=')[0]
        self.bid =  str(str(self.formUrl).split('bid=')[1]).split('&')[0]
        self.tid = str(str(self.formUrl).split('tid=')[1]).split('&')[0]
        self.id = str(str(self.formUrl).split('&id=')[1]).split('&')[0]
        self.uploadPDF = str(str(self.formUrl).split('uploadPDF=')[1]).split('&')[0]
        self.uploadMeta = str(str(self.formUrl).split('uploadMeta=')[1]).split('&')[0]
        self.host = host
        self.headers = {
            'Content-Type': 'application/json',
            'Access-Token': self.AccessToken
        }
        self.loc = os.path.abspath(os.path.dirname(__file__))
        loc = self.loc+os.sep+'dataTemplateForm.yaml'
        with open(loc,'r',encoding='utf-8') as file:
            self.dataTemplate = yaml.load(file,Loader=yaml.FullLoader)

    def createInstance(self):
        url = self.host +os.sep+'report-backend-meter/v2.0/service/rb/template/'+self.tid
        requests.get(url,headers=self.headers).json()
        url_isntance = self.host +'/report-backend-meter/v2.0/service/rb/instance/'+self.id
        res = requests.get(url_isntance,headers=self.headers).json()['data']
        time,name = res['createTime'],res['name']
        self.dataTemplate['createTime'],self.dataTemplate['templateId'],self.dataTemplate['id'] = time,time,self.id
        requests.put(url_isntance,json=self.dataTemplate,headers=self.headers)
        path = self.loc+os.sep+name+'.pdf'
        fileinfo = {"file": (name, open(path, "rb"), "pdf")}
        requests.post(self.uploadPDF,files=fileinfo)
        body =[{"page":1,"staticText":[],"num":[],"text":[]}]
        res = requests.post(self.uploadMeta,json=body,headers={'Content-Type':'application/json'})
        print('Mock 表单结束')
        return res








# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    url = r'http://service.lbuilder.cn/luban-data-manage/common/report/DATA_FORM/v1/page_url?bid=7633497dced94157919d9490caba2ce2&id=64d1b821e7ea5d325f43e56a&tid=1002220987246182400&type=1'
    headers = {
        "Access-Token": "eyJhbGciOiJIUzUxMiJ9.eyJsb2dpblR5cGUiOiIxOTIiLCJleHAiOjE2OTE4OTc3ODMsImlhdCI6MTY5MTQ2NTc4MywidXNlcm5hbWUiOiJsYjg4MTdpIn0.uEv4rPbBG-CUAxJZ9OF3IM_F6Eh9R11YSzQvzi-BrNTtH7hdKnNX1mh2na41l55eB6X171hxW9jyG25mxWiZNg",
        "Content-type": "application/json"
    }
    host ='http://service.lbuilder.cn'
    AdvanceForm(url,headers,host).createInstance()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
