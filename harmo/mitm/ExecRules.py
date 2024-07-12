#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/4/3 15:00
# @Author  : hubiao
# @Email   : 250021520@qq.com

from NoiseReduction import *

class ExecRules:
    def __init__(self,scriptPath,diff=None):
        self.diff = diff
        data = NoiseReduction().getRules(scriptPath)
        self.rulesDoc = data['rulesDoc']
        self.rulesIgnoreExect = data['rulesIgnoreExect']
        self.rulesIgnoreContain = data['rulesIgnoreContain']
        self.rulesGet = data['rulesGet']
        self.errorDict ={}

    def execRulesIgnoreExect(self,data,flowData):
        for each in self.rulesIgnoreExect:
            if data['key'] == each['Location'] and (flowData["path"] == each['Path'] or each['Path'] == 'ALL'):
                self.diff.remove(data)

    def execRulesIgnoreContain(self,data,flowData):
        for each in self.rulesIgnoreContain:
            if str(each['Location']).upper() in str(data['key']).upper() and (flowData["path"] == each['Path'] or each['Path'] == 'ALL'):
                tempkey = [v['key']  for v in self.diff if self.diff != [] ]
                if data['key'] in tempkey : self.diff.remove(data)

    def execRulesGet(self,data,flowData):
        for each in self.rulesGet:
            if ('_').join(str(each['Location']).split('.')[1:]).upper() in str(data['key']).upper() and (
                    flowData["path"] == each['Path'] or each['Path'] == 'ALL'):
                self.diff.remove(data)

    def main(self,flowData):
        if self.diff!=[]:
            for diffeach in self.diff[:]:
                self.execRulesIgnoreExect(diffeach,flowData)
                self.execRulesIgnoreContain(diffeach,flowData)
                self.execRulesGet(diffeach,flowData)
        return self.diff


