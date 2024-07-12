#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/4/3 15:00
# @Author  : hubiao
# @Email   : 250021520@qq.com

import copy

from harmo import base_utils
from harmo.operation import json_file
from utils import Utils
import time
from ThirdServer.advanceForm.main import *

class NoiseReduction:
    def __init__(self):
        self.config = Utils().getConfig()
        self.rules_IGNORE_CONTAIN,self.rules_IGNORE_EXECT,self.rules_GET,self.rules_DOC = [],[],[],[]
        self.ts =str(int(time.time()))
        with open('conifg/rules.yaml', 'r', encoding='utf-8') as r:
            self.rules = yaml.load(r,Loader=yaml.FullLoader)
        with open('conifg/filter.yaml', 'r', encoding='utf-8') as f:
            filter = yaml.load(f,Loader=yaml.FullLoader)
        self.filter = [ each for each in filter['FilterConfig'] if each['Status'] ]

    def createTestCase(self,modelName,testDocName=None):
        scriptPathlist,modelName =[],modelName+"_测试脚本集"
        try:
            os.mkdir(modelName)
        except:
            pass
        if self.config['whetherRecord']:
            name = 'NoName_测试脚本文件夹_'.replace('NoName',testDocName)+self.ts if testDocName != None else 'NoName_测试脚本文件夹_'+self.ts
            path =  os.getcwd() + os.sep+modelName+os.sep+name
            os.mkdir(path)
            #path = path + os.sep
            scriptPathlist.append(path)
        else:
            scriptPathlist = self.config['path']
        return scriptPathlist

    def createScript(self,scriptPath):
        execPath = str(scriptPath) + os.sep + 'script.json'
        if self.config['whetherRecord']:
            flowData = json_file.get_json_data(base_utils.file_absolute_path('script.json'))
            with open(execPath, 'w') as ff:
                ff.write(json.dumps(flowData))
        else:
            with open(execPath, 'r') as f1:
                flowData = json.loads(f1.read())
        flowDataDeepCopy = [each for each in flowData if each != {} and self.__specialFlowStatus(each)]
        flowData_urlList = [each['url'] for each in flowDataDeepCopy]
        if self.filter:
            for each in self.filter:
                filterStatus = False
                for i in range(len(flowData_urlList)):
                    if each['StepList'][0] in flowData_urlList[i] and filterStatus==False:
                        num =-1
                        for g in range(len(each['StepList'])):
                            k = i+g
                            if each['StepList'][g] in flowData_urlList[k]:
                                num = num+1
                            if num ==g and num==len(each['StepList'])-1:
                                filterStatus = True
                                end = i + len(each['StepList'])
                                headers = {
                                    'access-token' : 'MockAccessToken',
                                    'Content-Type' : 'application/json'
                                }
                                Mock = {'location': each['Mock'], 'method': "MOCK",
                                        'flow': flowDataDeepCopy[i],'id':"MockId",
                                        'url':'MockUrl','headers':headers,'body':'MockData',
                                        'MockName':each['Name'],'path':'MockPath'}
                                flowDataDeepCopy =flowDataDeepCopy[:i]+[Mock]+flowDataDeepCopy[end:]
                                break
        return flowDataDeepCopy

    def getValue(self,data,rules):
        location_list = str(dict(rules)['Location']).split('.')
        value = copy.deepcopy(data)
        for path in location_list:
            try:
                path = int(path)
            except:
                pass
            finally:
                try:
                    value = value[path]
                except:
                    pass
        return value

    def getRules(self,scriptPath):
        flowData,recond =self.createScript(scriptPath),[]
        if self.rules:
            for eachRule in self.rules['Rules']:
                if str(eachRule['Type']).upper() == 'GETVALUE':
                    eachRule['value'],id =[],self.getValueId(flowData,eachRule)
                    for data in flowData:
                        if id == data['id'] and id!=None:
                            eachRule['value'].append(self.getValue(data,eachRule))
                        recond.append({'id':data['id'],'url':data['url'],'method':data['method']})
                    self.rules_GET.append(eachRule)
                if str(eachRule['Type']).upper() == 'IGNORE':
                    if eachRule['Contain']:
                        self.rules_IGNORE_CONTAIN.append(eachRule)
                    else:
                        self.rules_IGNORE_EXECT.append(eachRule)
                if str(eachRule['Type']).upper() == 'DOC':
                    self.rules_DOC.append(eachRule)
            return {'rules': self.rules['Rules'],'status':self.config['whetherRecord'],
                    'model': self.config['Model'], 'NotifyUser': self.config['NotifyUser'],
                    'ts':self.ts,'flowData':flowData,'rulesIgnoreContain':self.rules_IGNORE_CONTAIN,
                    'rulesIgnoreExect':self.rules_IGNORE_EXECT,'rulesGet':self.rules_GET,
                    'rulesDoc':self.rules_DOC}

    def getValueId(self,flowdata,rule):
        id =None
        if 'AfterAPI' in rule.keys() :
            for i in range(len(flowdata)):
                if str(rule['AfterAPI']['Method']).upper()!='MOCK':
                    if str(rule['AfterAPI']['Method']).upper()==str(flowdata[i]['method']).upper() and rule['AfterAPI']['Path'] in flowdata[i]['path']:
                        id=flowdata[i+1]['id']
                else:
                    if 'MockName' in flowdata[i].keys():
                        if rule['AfterAPI']['Path'] == flowdata[i]['MockName']:
                            id = flowdata[i+1]['id']
        else:
            for data in flowdata:
                if rule['Path'] in data['path']:
                    id = data['id']
        return id

    def __specialFlowStatus(self,flowdata):
        status = True
        if 'resp' in flowdata.keys():
            if flowdata['resp'] ==None:
                status=False
        return status




