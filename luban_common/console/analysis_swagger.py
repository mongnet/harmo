#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/2/15 20:00
# @Author  : hubiao
# @File    : analysis_swagger.py
import os

import chevron
import requests
from pathlib2 import Path

from luban_common import base_utils
from luban_common.operation import yaml_file


class AnalysisSwaggerJson():
    """
    swagger自动生成接口测试用例的工具类,此类以生成json格式的测试用例
    """

    def __init__(self, url):
        '''
        初始化类,指定请求的swagger接口地址
        如："http://192.168.13.197:8989/builder/v2/api-docs"
        如："http://192.168.13.202:8081/Plan/rs/swagger/swagger.json"
        '''
        self.url = url
        self.tags_list = []  # 接口分组标签
        # 定义接口分组格式
        self.http_interface_group = {"config": {"name": "","name_en": "","host": "", "base_url": ""},"groups": []}


    def analysis_json_data(self, isDuplicated=False):
        """
        解析json格式数据的主函数
        :return:
        """
        # swagger接口文档地址
        try:
            res = requests.get(self.url).json()
        except Exception as e:
            raise e

        self.data = res['paths']  # 取接口地址返回的path数据,包括了请求的路径
        self.basePath = res['basePath']  # 获取接口的根路径
        # 第一错，swagger文档是ip地址，使用https协议会错误,注意接口地址的请求协议
        self.host = 'http://' + res.get('host') if res.get('host') else ''
        self.title = res['info']['title']  # 获取接口的标题
        self.http_interface_group['config']['name'] = self.title  # 在初始化用例集字典更新值
        self.http_interface_group['config']['name_en'] = self.url.split('/')[3].lower() if self.url.startswith("http") else self.url.split('/')[1].lower()
        self.http_interface_group['config']['host'] = self.host
        self.http_interface_group['config']['base_url'] = self.basePath
        self.definitions = res['definitions']  # body参数


        for tag_dict in res['tags']:
            self.tags_list.append(tag_dict)

        if isinstance(self.data, dict):  # 判断接口返回的paths数据类型是否dict类型
            # 前面已经把接口返回的结果tags分别写入了tags_list空列表,再从json对应的tag往里面插入数据
            for tag in self.tags_list:
                self.group = {"name": "", "file_name": "", "class_name": "", "interfaces": []}
                self.repetition_operationId = []
                for uri, value in self.data.items():
                    for method in list(value.keys()):
                        params = value[method]
                        # deprecated字段标识：接口是否被弃用，暂时无法判断
                        if not 'deprecated' in value.keys():
                            if params['tags'][0] == tag.get('name'):
                                self.group['name'] = tag.get('name')
                                interface = self.wash_params(params, uri, method)
                                self.group['interfaces'].append(interface)
                        else:
                            print('interface path: {}, if name: {}, is deprecated.'.format(uri, params['operationId']))
                            break
                # 生成 class_name 和 file_name
                uri_list = base_utils.jpath(self.group, check_key='uri', sub_key='uri')
                if isinstance(uri_list,list):
                    file_name = ''
                    for uri in uri_list:
                        k1 = uri.split('/{', 1)[0].split('/')[1:]
                        for i in uri_list:
                            k2 = i.split('/{', 1)[0].split('/')[1:]
                            file_name = list(sorted(set(k1).intersection(set(k2)), key=k1.index))
                        break
                    self.group['class_name'] = "_".join(file_name).capitalize()
                    self.group['file_name'] = "_".join(file_name)
                self.http_interface_group['groups'].append(self.group)
        else:
            return 'error'
        return  self.http_interface_group

    def wash_params(self, params, api, method):
        """
        清洗数据json，把每个接口数据都加入到一个字典中
        :param params: swagger中的接口参数信息
        :param uri: 接口URI地址
        :param method: 接口请求方法
        :return:
        """
        # 定义具体接口数据格式
        http_interface = {
            "name_cn": "",
            "name_en": "",
            "uri": "",
            "basePath": "",
            "method": "",
            "headers": {},
            'body':{},
            "body_params_args": [],
            "body_params_kwargs": [],
            "params_description":{},
            "params_description_list":{},
            "query_params": {},
            "query_params_args": [],
            "query_params_kwargs": [],
            "path_params": {},
            "path_params_args": [],
            "path_params_kwargs": [],
            "cookie_params": {},
            "cookie_params_args": [],
            "cookie_params_kwargs": [],
            "validate": [],
            "output": []
        }
        # 这里程序可能没有写summary，只能用operationId来替代了
        name = params.get('summary').replace('/', '_') if params.get('summary') else params.get('operationId')
        http_interface['name_cn'] = name
        # 处理 operationId 会相同的问题
        name_en_list = base_utils.jpath(self.group['interfaces'], check_key='name_en', sub_key='name_en')
        if name_en_list and params.get('operationId') in name_en_list:
            self.repetition_operationId.append(params.get('operationId'))
            name_en = params.get('operationId') + '_' + str(self.repetition_operationId.count(params.get('operationId')))
        else:
            name_en = params.get('operationId')
        http_interface['name_en'] = name_en
        http_interface['method'] = method.upper()
        http_interface['uri'] = api
        http_interface['basePath'] = self.basePath
        parameters = params.get('parameters')  # 未解析的参数字典
        responses = params.get('responses')

        if not parameters:  # 确保参数字典存在
            parameters = {}
        # 调试用
        # if name != "检查库工程类别自定义列表接口,排序字段sort_num":
        #     return
        for each in parameters:
            if each.get('in') == 'body':
                # if method.upper() == 'GET':
                #     raise SyntaxError("语法错误: GET方法不应该有请求体,接口名为："+api)
                schema = each.get('schema')
                if schema and '$ref' in schema.keys() or ('items' in schema.keys() and '$ref' in schema.get('items').keys()):
                    ref = schema.get('items').get('$ref') if schema.get('$ref') is None else schema.get('$ref')
                    if ref:
                        # 拆分这个uri，根据实际情况来取第几个/反斜杠
                        param_key = ref.split('/', 2)[-1]
                        param = self.definitions[param_key]['properties']
                        for key, value in param.items():
                            if 'type' in value.keys():
                                if 'description' in value.keys():
                                    http_interface['params_description'].update({key: value['description']})
                                else:
                                    http_interface['params_description'].update({key: value['type']})
                                if 'items' in value.keys():
                                    if '$ref' in value.get('items'):
                                        items_ref = self.definitions[value.get('items').get('$ref').split('/', 2)[-1]]['properties']
                                        data = {}
                                        for k, v in items_ref.items():
                                            if 'type' in v.keys():
                                                data.update({k: v['type']})
                                                if 'description' in v.keys():
                                                    http_interface['params_description'].update({k: v['description']})
                                        http_interface['body'].update({key: [data]})
                                    elif 'type' in value.get('items'):
                                        for k,v in value.get('items').items():
                                            http_interface['body'].update({key: [v]})
                                            if 'description' in value.keys():
                                                http_interface['params_description'].update({key: value['description']})
                                            else:
                                                http_interface['params_description'].update({key: value['type']})
                                else:
                                    http_interface['body'].update({key: value['type']})
                            elif '$ref' in value.keys():  # 解决 BasicPage 问题
                                data = {}
                                # 有多个schema时，这里会报错
                                if self.definitions.get(value.get('$ref').split('/', 2)[-1]).get('properties'):
                                    for k,v in self.definitions.get(value.get('$ref').split('/', 2)[-1]).get('properties').items():
                                        if 'type' in v.keys():
                                            data.update({k: v['type']})
                                            if 'description' in v.keys():
                                                http_interface['params_description'].update({k: v['description']})
                                            else:
                                                http_interface['params_description'].update({k: v['type']})
                                http_interface['body'].update({key: data})
                                # print(key)
                    # 处理body为列表时的情况
                    if schema.get('type') == 'array':
                        bady = http_interface['body']
                        del http_interface['body']
                        http_interface.update({'body':[bady]})
                # 结果为None时，传参分列表和字符串
                elif schema.get('$ref') is None and schema.get('type')=='array':
                    http_interface['body'] = 'body_list'
                    http_interface['params_description'].update({"body_list": schema.get('items').get('type')})
                elif schema.get('$ref') is None and schema.get('type')=='string':
                    http_interface['body'] = 'body_str'
                    http_interface['params_description'].update({"body_str": schema.get('type')})

            # 看能否把下面的合并成一个，且把必填字段写出
            # else:
            #     name = each.get('name')
            #     for key in each.keys():
            #         http_interface['query_params'].update({name: each[key]})
            #         if 'description' in each.keys():
            #             http_interface['params_description'].update({name: each['description']})

            if each.get('in') == 'query':
                name = each.get('name')
                http_interface['query_params'].update({name: each.get('type')})
                if 'description' in each.keys():
                    http_interface['params_description'].update({name: each['description']})

            if each.get('in') == 'path':
                name = each.get('name')
                http_interface['path_params'].update({name: each.get('type')})
                if 'description' in each.keys():
                    http_interface['params_description'].update({name: each['description']})

            if each.get('in') == 'cookie':
                name = each.get('name')
                http_interface['cookie_params'].update({name: each.get('type')})
                if 'description' in each.keys():
                    http_interface['params_description'].update({name: each['description']})
            # 会出现有多个schema的情况，发现后面的schema都是有问题的，所以直接跳出循环
            # break

        # 把 query_params 的 key 组装成新的 query_params_url ,生成用例时添加成测试方法的参数
        if 'query_params' in http_interface.keys() and http_interface['query_params']:
            args = []
            kwargs = []
            for key, value in http_interface['query_params'].items():
                self.wash_body(key, http_interface['query_params'], args, kwargs, parameters_form='query')
            http_interface['query_params_args'] = list(set(args))
            http_interface['query_params_kwargs'] = list(set(kwargs))
        # 把 path_params 的 key 组装成新的 path_params_url ,生成用例时添加成测试方法的参数
        if 'path_params' in http_interface.keys() and http_interface['path_params']:
            args = []
            kwargs = []
            for key, value in http_interface['path_params'].items():
                self.wash_body(key, http_interface['path_params'], args, kwargs, parameters_form='path')
            http_interface['path_params_args'] = list(set(args))
            http_interface['path_params_kwargs'] = list(set(kwargs))
        # 把 cookie_params 的 key 组装成新的 cookie_params_url ,生成用例时添加成测试方法的参数
        if 'cookie_params' in http_interface.keys() and http_interface['cookie_params']:
            args = []
            kwargs = []
            for key, value in http_interface['cookie_params'].items():
                self.wash_body(key, http_interface['cookie_params'], args, kwargs, parameters_form='cookie')
            http_interface['cookie_params_args'] = list(set(args))
            http_interface['cookie_params_kwargs'] = list(set(kwargs))
        # 把 body 的 key 组装成新的 body_param ,生成用例时添加成测试方法的参数
        if 'body' in http_interface.keys() and http_interface['body']:
            if http_interface['body'] != 'body_list' and http_interface['body'] != 'body_str':
                self.args = []
                self.kwargs = []
                self.recursion(http_interface['body'])
                http_interface['body_params_args'] = list(set(self.args))
                http_interface['body_params_kwargs'] = list(set(self.kwargs))
            elif http_interface['body'] == 'body_list':
                http_interface['body'] = "'$body_list$'"
                http_interface['body_params_kwargs'] = ["body_list=[]"]
            elif  http_interface['body'] == 'body_str':
                http_interface['body'] = "'$body_str$'"
                http_interface['body_params_kwargs'] = ["body_str='body_str'"]
        # 把 args、kwargs 组装在一起，方便后续调用
        http_interface['params_args'] = http_interface['path_params_args'] + http_interface['cookie_params_args'] + http_interface['query_params_args'] + http_interface['body_params_args']
        http_interface['params_kwargs'] = http_interface['path_params_kwargs'] + http_interface['cookie_params_kwargs'] + http_interface['query_params_kwargs'] + http_interface['body_params_kwargs']
        # 把 params_description 组装成 params_description_list 生成用例时,生成字段备注使用
        if 'params_description' in http_interface.keys():
            params_description = []
            for k, v in http_interface['params_description'].items():
                params_description.append(k + ': ' + v.replace('\n', '').replace('\r', '').replace('\t', ''))
            http_interface['params_description_list'] = params_description

        for each in parameters:
            if each.get('in') == 'header':
                name = each.get('name')
                for key in each.keys():
                    if 'example' in key:
                        http_interface['headers'].update({name: each[key]})
                    else:
                        if name == 'token':
                            http_interface['headers'].update({name: '$token'})
                        else:
                            http_interface['headers'].update({name: ''})

        for key, value in responses.items():
            schema = value.get('schema')
            if schema:
                ref = schema.get('$ref')
                if ref:
                    param_key = ref.split('/')[-1]
                    res = self.definitions[param_key]['properties']
                    i = 0
                    for k, v in res.items():
                        if 'example' in v.keys():
                            http_interface['validate'].append({"eq": []})
                            http_interface['validate'][i]['eq'].append('content.' + k)
                            http_interface['validate'][i]['eq'].append(v['example'])
                            i += 1
                else:
                    if len(http_interface['validate']) != 1:
                        http_interface['validate'].append({"eq": []})
            else:
                if len(http_interface['validate']) != 1:
                    http_interface['validate'].append({"eq": []})

        # 接口请求参数为空字典，则删除这些key
        for k in list(http_interface.keys()):
            if not http_interface[k]:
                del http_interface[k]

        # 定义接口测试用例
        return http_interface

    def recursion(self,data):
        if isinstance(data, list):
            for itme in data:
                self.recursion(itme)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    self.recursion(value)
            for key, value in data.items():
                if isinstance(value, list):
                    if isinstance(value[0], dict):
                        for k, v in value[0].items():
                            self.wash_body(k, value[0], self.args, self.kwargs)
                        continue
                elif isinstance(value, dict):
                    for k, v in value.items():
                        self.wash_body(k, value, self.args, self.kwargs)
                    continue
                self.wash_body(key, data, self.args, self.kwargs)

    def wash_body(self,arg, body, list_args, list_kwargs, parameters_form=None):
        '''
        清洗body 数据
        :param arg: 指定key
        :param body: 需要清洗的 body 数据
        :param list_args: 无默认值的参数列表
        :param list_kwargs: 有默认值的参数列表
        :param parameters_form: 传参方式
        :return:
        '''
        current_path = os.path.dirname(os.path.realpath(__file__))
        default_parame = yaml_file.get_yaml_data(f'{current_path}/../config/default_parame.yaml')
        blacklist = yaml_file.get_yaml_data(f'{current_path}/../config/blacklist.yaml')
        if arg in list_args or arg in [kwarg.split('=')[0] for kwarg in list_kwargs if kwarg.startswith(arg)]:
            return
        if arg in default_parame.keys():
            # 接口传参默认值处理
            kwarg = ""
            if isinstance(default_parame[arg], int):
                kwarg = str(default_parame[arg])
            elif isinstance(default_parame[arg], str):
                # 前后加$表示变量
                if default_parame[arg].startswith('$') and default_parame[arg].endswith('$'):
                    kwarg = default_parame[arg]
                else:
                    # 如果是字符串常量必须要加引号
                    kwarg = '"' + default_parame[arg] + '"'
            list_kwargs.append(arg + '=' + kwarg)
        # 当parameters_form不是None或不是path参数时，参数默认值设置为None
        elif parameters_form is not None and parameters_form != 'path':
            list_kwargs.append(arg + '=$None$')
        elif body[arg] == 'boolean':
            list_kwargs.append(arg + '=$False$')
        elif arg not in blacklist:
            list_args.append(arg)
        # body 请求体参数化处理
        body[arg] = '$' + arg + '$'

    def generator_interface_file(self,data):
        '''
        生成接口文件
        :param data:
        :return:
        '''
        if not isinstance(data,dict):
            raise FileExistsError("数据类型错误，传入的数据必须为dict")
        for key, values in data.items():
            if "groups" in key:
                path = Path.cwd() / data["config"]["name"]
                path.mkdir(mode=0o777, parents=True, exist_ok=True)
                package_init = path / "__init__.py"
                package_init.touch(exist_ok=False)
                for group in values:
                    # with open('../config/interface.config', 'r') as config:
                    interfaces = chevron.render(group, group)
                    interface_file = path/f"test_{group['file_name']}.py"
                    with interface_file.open("w", encoding="utf-8") as f:
                        f.write(interfaces)


if __name__ == '__main__':
    url = "http://192.168.13.202:8081/Plan/rs/swagger/swagger.json"
    url1 = "http://192.168.3.195/LBbuilder/v2/api-docs"
    url2 = "http://192.168.3.195:8989/LBprocess/v2/api-docs"
    url3 = "http://192.168.13.20/pdscommon/rs/swagger/swagger.json"
    url4 = 'http://192.168.13.202:8082/pdsdoc/rs/swagger/swagger.json'
    url5 = 'http://192.168.3.195/BuilderCommonBusinessdata/rs/swagger/swagger.json'
    url6 = 'http://192.168.3.195/BuilderCommonBusinessdata/rs/swagger/swagger.json'
    print(AnalysisSwaggerJson(url).analysis_json_data())
    print(AnalysisSwaggerJson(url1).analysis_json_data())
    print(AnalysisSwaggerJson(url2).analysis_json_data())
    print(AnalysisSwaggerJson(url3).analysis_json_data())
    print(AnalysisSwaggerJson(url4).analysis_json_data())
    print(AnalysisSwaggerJson(url5).analysis_json_data())
    print(AnalysisSwaggerJson(url6).analysis_json_data())

    # js.generator_interface_file(result)
    # http://192.168.3.195:8989/BuilderCommonBusinessdata/swagger/index.html
    # http://192.168.3.195:8989/LBprocess/swagger-ui.html
    # http://192.168.13.233:8080/dev-api/doc.html

