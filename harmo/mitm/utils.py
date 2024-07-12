#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/4/3 15:00
# @Author  : hubiao
# @Email   : 250021520@qq.com

import yaml,os,pathlib


class Utils:
    def __init__(self):
        pass

    def getConfig(self):
        result = {}
        with open('conifg/config.yaml', 'r', encoding='utf-8') as file:
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
        if result['path'] == []:
            print("测试脚本文件夹没找到，请检查后在执行！")
        result['Model'] = configInfo.get('Setting').get('Model')
        result['Url'], result['User'], result['PSW'], result['NotifyUser'] = configInfo.get('Setting').get('Url'), \
            configInfo.get('Setting').get('User'), \
            configInfo.get('Setting').get('PSW'), \
            configInfo.get('Setting').get('NotifyUser')
        return result

if __name__ == '__main__':
    print(Utils().getConfig())