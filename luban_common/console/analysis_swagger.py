#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/2/15 20:00
# @Author  : hubiao
# @File    : analysis_swagger.py
import os

import chevron
import requests
import copy
from datetime import datetime
from pathlib2 import Path

from luban_common import base_utils
from luban_common.operation import yaml_file


class AnalysisSwaggerJson():
    """
    swagger自动生成接口测试用例的工具类,此类以生成json格式的测试用例
    """

    def __init__(self, url):
        """
        初始化类,指定请求的swagger接口地址
        如："http://192.168.13.197:8989/builder/v2/api-docs"
        如："http://192.168.13.202:8081/Plan/rs/swagger/swagger.json"
        """
        self.url = url
        yamlDate = yaml_file.get_yaml_data(f"{os.path.dirname(os.path.realpath(__file__))}/../config/parameConfig.yaml")
        self.default_parame = yamlDate.get("defaultParame")
        self.blacklist = yamlDate.get("blacklist")


    def analysis_json_data(self, isDuplicated=False):
        """
        解析json格式数据的主函数
        :return:
        """
        # swagger接口文档地址
        try:
            http_interface_groups =[]
            response = requests.get(self.url)
            assert response.status_code == 200,f"地址无法访问，响应状态码为{response.status_code}"
            res = response.json()
            if isinstance(res,dict):
                http_interface_groups.append(self.analysis(res))
            else:
                if isinstance(res,list) and "swagger-resources" in self.url:
                    print(f"这是一个 swagger-resources, 共有 {len(res)} 个group")
                    for i in res:
                        print(f"开始处理 {i.get('name')}")
                        if isinstance(i,dict) and i.get("url"):
                            response = requests.get(self.url.split("/swagger-resources",1)[0]+i.get("url"))
                            assert response.status_code == 200, f"地址无法访问，响应状态码为{response.status_code}"
                            res = response.json()
                            http_interface_groups.append(self.analysis(res))
                        else:
                            raise ValueError(u"不是一个有效的swagger地址")
                else:
                    raise ValueError(u"不是一个有效的swagger地址")
            return http_interface_groups
        except Exception as e:
            raise e

    def analysis(self,res):
        # 定义接口分组格式
        http_interface_group = {"config": {"name": "","name_en": "","host": "", "base_url": ""},"groups": []}
        pathsData = res.get("paths")  # 取接口地址返回的path数据,包括了请求的路径
        self.basePath = res.get("basePath") if res.get("basePath") else ""  # 获取接口的根路径
        # 第一错，swagger文档是ip地址，使用https协议会错误,注意接口地址的请求协议
        host = "http://" + res.get("host") if res.get("host") else ""
        title = res.get("info").get("title")  # 获取接口的标题
        http_interface_group["config"]["name"] = title  # 在初始化用例集字典更新值
        http_interface_group["config"]["name_en"] = self.url.split("/")[3].lower().replace("-", "_") if self.url.startswith("http") else self.url.split("/")[1].lower().replace("-", "_")
        http_interface_group["config"]["host"] = host
        http_interface_group["config"]["base_url"] = self.basePath
        self.definitions = res.get("definitions")  # body参数
        tags_list = []  # 接口分组标签
        for tag_dict in res.get("tags"):
            tags_list.append(tag_dict)
        if isinstance(pathsData, dict):  # 判断接口返回的paths数据类型是否dict类型
            # 前面已经把接口返回的结果tags分别写入了tags_list空列表,再从json对应的tag往里面插入数据
            for tag in tags_list:
                group = {"name": "", "file_name": "", "class_name": "", "interfaces": []}
                self.repetition_operationId = []
                for uri, value in list(pathsData.items()):
                    for method in list(value.keys()):
                        params = value[method]
                        # deprecated字段标识：接口是否被弃用，暂时无法判断
                        if not "deprecated" in value.keys():
                            if params.get("tags")[0] == tag.get("name"):
                                group["name"] = tag.get("name")
                                interface = self.wash_params(params, uri, method, group)
                                group["interfaces"].append(interface)
                        else:
                            print(f'interface path: {uri}, if name: {params["operationId"]}, is deprecated.')
                            break
                    # 优化循环性能，已经处理过的数据删除掉，避免重复循环
                    # del pathsData[f"{uri}"]
                # 生成 class_name 和 file_name
                uri_list = base_utils.jpath(group, check_key="uri", sub_key="uri")
                if isinstance(uri_list,list):
                    file_name = ""
                    for uri in uri_list:
                        k1 = uri.split("?")[0].split("/{", 1)[0].split("/")[1:]
                        for i in uri_list:
                            k2 = i.split("?")[0].split("/{", 1)[0].split("/")[1:]
                            k1 = k1 if not list(sorted(set(k1).intersection(set(k2)), key=k1.index)) else list(sorted(set(k1).intersection(set(k2)), key=k1.index))
                        file_name = "_".join(k1).replace("-", "_").title().replace("_", "")
                        break
                    group["class_name"] = file_name
                    group["file_name"] = file_name[0].lower()+file_name[1:]
                # 合并相同file_name
                groups = base_utils.jpath(http_interface_group.get("groups"), check_key="file_name", sub_key="file_name")
                if groups:
                    if group.get("file_name") in groups:
                        interface_group = http_interface_group.get("groups")[groups.index(group.get("file_name"))]
                        interface_group["name"] = "_".join([interface_group.get("name"),group.get("name")])
                        interface_group["interfaces"].extend(group.get("interfaces"))
                        continue
                http_interface_group["groups"].append(group)
        else:
            return "error"
        return http_interface_group

    def wash_params(self, params, api, method, group):
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
            "produces": "",
            "headers": {},
            "body":{},
            "body_field_type":{},
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
        name = params.get("summary").replace("/", "_") if params.get("summary") else params.get("operationId")
        http_interface["name_cn"] = name
        # 处理 operationId 会相同的问题
        name_en_list = base_utils.jpath(group["interfaces"], check_key="name_en", sub_key="name_en")
        if name_en_list and params.get("operationId") in name_en_list:
            self.repetition_operationId.append(params.get("operationId"))
            name_en = params.get("operationId") + "_" + str(self.repetition_operationId.count(params.get("operationId")))
        else:
            name_en = params.get("operationId")
        http_interface["name_en"] = name_en
        http_interface["method"] = method.upper()
        http_interface["uri"] = api
        http_interface["basePath"] = self.basePath
        parameters = params.get("parameters")  # 未解析的参数字典
        responses = params.get("responses")
        produces = params.get("produces")

        if not parameters:  # 确保参数字典存在
            parameters = {}
        # 调试用
        # if name != "获取某企业下的所有专业类型列表":
        #     return
        # if name != "批量删除有效数据":
        #     return
        for each in parameters:
            if each.get("in") == "body":
                # if method.upper() == "GET":
                #     raise SyntaxError("语法错误: GET方法不应该有请求体,接口名为："+api)
                schema = each.get("schema")
                if schema:
                    self.jiexi(schema, http_interface, each=each)
                    # schema type为array时，已把变量命名成 array_string，后续直接传数组即可
                    if schema.get("type") == "array":
                        if isinstance(http_interface["body"],str) and http_interface["body"].startswith("$array_"):
                            pass
                        else:
                            bady = http_interface["body"]
                            del http_interface["body"]
                            http_interface.update({"body": [bady]})

            if each.get("in") == "query":
                name = each.get("name")
                http_interface["query_params"].update({name: each.get("type")})
                if "description" in each.keys():
                    http_interface["params_description"].update({name: each.get("description") + (",必填" if each.get("required") else ",非必填")})

            if each.get("in") == "path":
                name = each.get("name")
                http_interface["path_params"].update({name: each.get("type")})
                if "description" in each.keys():
                    http_interface["params_description"].update({name: each.get("description") + (",必填" if each.get("required") else ",非必填")})

            if each.get("in") == "cookie":
                name = each.get("name")
                http_interface["cookie_params"].update({name: each.get("type")})
                if "description" in each.keys():
                    http_interface["params_description"].update({name: each.get("description") + (",必填" if each.get("required") else ",非必填")})

        # 把 query_params 的 key 组装成新的 query_params_url ,生成用例时添加成测试方法的参数
        if "query_params" in http_interface.keys() and http_interface["query_params"]:
            args = []
            kwargs = []
            for key, value in http_interface["query_params"].items():
                self.wash_body(key, http_interface["query_params"], args, kwargs, parameters_form="query")
            http_interface["query_params_args"] = list(set(args))
            http_interface["query_params_kwargs"] = list(set(kwargs))
        # 把 path_params 的 key 组装成新的 path_params_url ,生成用例时添加成测试方法的参数
        if "path_params" in http_interface.keys() and http_interface["path_params"]:
            args = []
            kwargs = []
            for key, value in http_interface["path_params"].items():
                self.wash_body(key, http_interface["path_params"], args, kwargs, parameters_form="path")
            http_interface["path_params_args"] = list(set(args))
            http_interface["path_params_kwargs"] = list(set(kwargs))
        # 把 cookie_params 的 key 组装成新的 cookie_params_url ,生成用例时添加成测试方法的参数
        if "cookie_params" in http_interface.keys() and http_interface["cookie_params"]:
            args = []
            kwargs = []
            for key, value in http_interface["cookie_params"].items():
                self.wash_body(key, http_interface["cookie_params"], args, kwargs, parameters_form="cookie")
            http_interface["cookie_params_args"] = list(set(args))
            http_interface["cookie_params_kwargs"] = list(set(kwargs))
        # 把 body 的 key 组装成新的 body_param ,生成用例时添加成测试方法的参数
        if "body" in http_interface.keys() and http_interface["body"]:
            self.args = []
            self.kwargs = []
            http_interface["body_field_type"] = copy.deepcopy(http_interface["body"])
            self.recursion(http_interface["body"])
            http_interface["body_params_args"] = (list(set(self.args)) if http_interface["body_params_args"]==[] else http_interface["body_params_args"])
            http_interface["body_params_kwargs"] = (list(set(self.kwargs)) if http_interface["body_params_kwargs"]==[] else http_interface["body_params_kwargs"])
        # 把 args、kwargs 组装在一起，方便后续调用
        http_interface["params_args"] = list(set(http_interface["path_params_args"] + http_interface["cookie_params_args"] + http_interface["query_params_args"] + http_interface["body_params_args"]))
        http_interface["params_kwargs"] = list(set(http_interface["path_params_kwargs"]+http_interface["cookie_params_kwargs"] + http_interface["query_params_kwargs"] + http_interface["body_params_kwargs"]))
        http_interface["params_args_nobody"] = list(set(http_interface["path_params_args"] + http_interface["cookie_params_args"] + http_interface["query_params_args"]))
        http_interface["params_kwargs_nobody"] = list(set(http_interface["path_params_kwargs"]+http_interface["cookie_params_kwargs"] + http_interface["query_params_kwargs"]))
        # 把 params_description 组装成 params_description_list 生成用例时,生成字段备注使用
        if "params_description" in http_interface.keys():
            params_description = []
            for k, v in http_interface["params_description"].items():
                params_description.append(k + ": " + v.replace("\n", "").replace("\r", "").replace("\t", ""))
            http_interface["params_description_list"] = params_description

        for each in parameters:
            if each.get("in") == "header":
                name = each.get("name")
                for key in each.keys():
                    if "example" in key:
                        http_interface["headers"].update({name: each[key]})
                    else:
                        if name == "token":
                            http_interface["headers"].update({name: "$token"})
                        else:
                            http_interface["headers"].update({name: ""})

        for key, value in responses.items():
            schema = value.get("schema")
            if schema:
                ref = schema.get("$ref")
                if ref:
                    param_key = ref.split("/")[-1]
                    res = self.definitions.get(param_key).get("properties")
                    i = 0
                    for k, v in res.items():
                        if "example" in v.keys():
                            http_interface["validate"].append({"eq": []})
                            http_interface["validate"][i]["eq"].append({k:v.get("example")})
                            http_interface["validate"][i]["eq"].append({"description":v.get("description")})
                            # http_interface["validate"][i]["eq"].append("content." + k)
                            # http_interface["validate"][i]["eq"].append(v.get("example"))
                            # http_interface["validate"][i]["eq"].append(v.get("description"))
                            i += 1
            #     else:
            #         if len(http_interface["validate"]) != 1:
            #             http_interface["validate"].append({"eq": []})
            # else:
            #     if len(http_interface["validate"]) != 1:
            #         http_interface["validate"].append({"eq": []})

        # 接口请求参数为空字典，则删除这些key
        for k in list(http_interface.keys()):
            if not http_interface[k]:
                del http_interface[k]

        # 定义接口测试用例
        return http_interface

    def jiexi(self,schema,http_interface,ephemeral_key=None,key_type=None,body=None,each=None):
        if "$ref" in schema.keys():
            ref = schema.get("$ref")
            if ref:
                # 拆分这个ref，根据实际情况来取第几个/反斜杠
                param_key = ref.split("/", 2)[-1]
                try:
                    param = self.definitions.get(param_key).get("properties")
                    requireds = self.definitions.get(param_key).get("required")
                except:
                    if len(http_interface["body"]) == 0:
                        del http_interface["body"]
                        body = each.get("name")
                        body_description = each.get("description") if each.get("description") else body
                        http_interface.update({"body": f"${body}$"})
                        http_interface["body_params_kwargs"].append(f"${body}=None$")
                        http_interface["params_description"].update({f"${body}$": f"{body_description}"})
                    print(f"警告: {http_interface.get('name_cn')} 接口的 {ref} 定义，没有properties节点信息，请确认程序生成的swagger信息是否正确")
                    return
                ephemeral_data = {}
                for key, value in param.items():
                    required = True if isinstance(requireds,list) and key in requireds else False
                    if "type" in value.keys():
                        if ephemeral_key:
                            ephemeral_data.update({key: value["type"]})
                            if "description" in value.keys():
                                http_interface["params_description"].update({key: value.get("description") + ",可用值:" + (",".join(value.get("enum")) if "enum" in value.keys() else value.get("description")) + (",必填" if required else ",非必填")})
                            if "items" in value.keys() and "$ref" in value.get("items"):
                                pass
                        else:
                            if "description" in value.keys():
                                http_interface["params_description"].update({key: value.get("description") + ",可用值:" + (",".join(value.get("enum")) if "enum" in value.keys() else value.get("description")) + (",必填" if required else ",非必填")})
                            else:
                                http_interface["params_description"].update({key: value.get("type") + (",必填" if value.get("required") else ",非必填")})
                            http_interface["body"].update({key: value.get("type")})
                        if "items" in value.keys() and "$ref" in value.get("items"):
                            if value.get("items").get("$ref") == ref:
                                # 跳出递归死循环
                                pass
                            else:
                                if ephemeral_key is None:
                                    http_interface["body"].update({key: []})
                                    self.jiexi(value.get("items"), http_interface, key, value["type"],body=http_interface["body"][key])
                                else:
                                    if body is not None:
                                        if key_type == "array":
                                            if key in ephemeral_data:
                                                ephemeral_data.update({key: []})
                                            else:
                                                body.append({key: []})
                                    self.jiexi(value.get("items"), http_interface, key, value["type"],body=ephemeral_data)
                    elif "$ref" in value.keys():
                        if value.get("$ref") == ref:
                            # 跳出递归死循环
                            pass
                        else:
                            self.jiexi(value, http_interface, key)
                if ephemeral_key:
                    if body:
                        if body[ephemeral_key] == "array":
                            body[ephemeral_key] = [ephemeral_data]
                        else:
                            body[ephemeral_key].append(ephemeral_data)
                    else:
                        if isinstance(body,list):
                            http_interface["body"].update({ephemeral_key.split("_")[-1]: [ephemeral_data]})
                        else:
                            http_interface["body"].update({ephemeral_key.split("_")[-1]: ephemeral_data})
        else:
            for key, value in schema.items():
                if isinstance(value, dict) and "$ref" in value.keys():
                    self.jiexi(value, http_interface,ephemeral_key)
                    return
            # 处理body为列表时的情况
            if schema.get("type") == "array" and ephemeral_key is None:
                del http_interface["body"]
                body = "_".join(base_utils.get_all_value(schema))
                http_interface.update({"body": f"${body}$"})
                http_interface["body_params_kwargs"].append(f"${body}=None$")
                http_interface["params_description"].update({f"${body}$": f"${body}$"})
            # 处理body为字符串时的情况
            elif schema.get("type") == "string" and ephemeral_key is None:
                body = "_".join(base_utils.get_all_value(schema))
                if "binary" in base_utils.get_all_value(schema):
                    http_interface.update({"body_binary": f"${body}$"})
                else:
                    http_interface.update({"body": f"${body}$"})
                http_interface["body_params_kwargs"].append(f"${body}=None$")
                http_interface["params_description"].update({f"${body}$": f"${body}$"})

    def recursion(self, data):
        """
        递归解析数据f
        :param data:
        :return:
        """
        if isinstance(data, list):
            for itme in data:
                self.recursion(itme)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    self.recursion(value)
                    continue
                if isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, list):
                            self.recursion(v)
                            continue
                        self.wash_body(k, value, self.args, self.kwargs)
                    continue
                self.wash_body(key, data, self.args, self.kwargs)

    def wash_body(self,arg, body, list_args, list_kwargs, parameters_form=None):
        """
        清洗body 数据
        :param arg: 指定key
        :param body: 需要清洗的 body 数据
        :param list_args: 无默认值的参数列表
        :param list_kwargs: 有默认值的参数列表
        :param parameters_form: 传参方式
        :return:
        """
        # 无默认值或在黑名单中的参数无需处理
        if arg in list_args or arg in self.blacklist:
            return
        if arg in self.default_parame.keys():
            # 接口传参默认值处理
            kwarg = ""
            if isinstance(self.default_parame[arg], int):
                kwarg = str(self.default_parame[arg])
            elif isinstance(self.default_parame[arg], str):
                # 前后加$表示变量
                if self.default_parame[arg].startswith("$") and self.default_parame[arg].endswith("$"):
                    kwarg = self.default_parame[arg]
                else:
                    # 如果是字符串常量必须要加引号
                    kwarg = f'"{self.default_parame[arg]}"'
            list_kwargs.append(arg + "=" + kwarg)
        # 当类型为boolean时，默认设置为False
        elif body[arg] == "boolean":
            list_kwargs.append(arg + "=$False$")
        # 当parameters_form不是None或不是path参数时，参数默认值设置为None
        elif parameters_form is not None or parameters_form != "path":
            list_kwargs.append(arg + "=$None$")
        # body 请求体参数化处理
        body[arg] = "$" + arg + "$"


if __name__ == "__main__":
    url = "http://192.168.13.242:8864/sphere/swagger-resources"
    url0 = "http://192.168.13.246:8182/Plan/rs/swagger/swagger.json"
    url1 = "http://192.168.13.246:8182/gateway/builder/v2/api-docs"
    url2 = "http://192.168.3.195:8989/LBprocess/v2/api-docs"
    url3 = "http://192.168.3.195/pdscommon/rs/swagger/swagger.json"
    url4 = "http://192.168.3.195/pdsdoc/rs/swagger/swagger.json"
    url5 = "http://192.168.3.195/BuilderCommonBusinessdata/rs/swagger/swagger.json"
    url6 = "http://192.168.13.233:8080/auth-server/v2/api-docs"
    url7 = "http://192.168.3.195/openapi/rs/swagger/swagger.json"
    # url9 = "http://192.168.3.236:8083/monitor/v2/api-docs?group=center"
    url10 = "http://192.168.13.246:8182/misc/v2/api-docs?group=信息深度(center端)"
    url11 = "http://192.168.13.246:8182/misc/v2/api-docs?group=信息深度(客户端)"
    url12 = "http://192.168.3.195/BuilderCommonBusinessdata/rs/swagger/swagger.json"
    url13 = "http://192.168.3.195/gateway/process/v2/api-docs"
    url14 = "http://192.168.13.246:8182/gateway/luban-meter/v2/api-docs?group=V1.0.0"
    url15 = "http://192.168.13.246:8182/gateway/luban-infrastructure-center/v2/api-docs?group=V1.0.0"
    url16 = "http://192.168.13.246:8182/gateway/luban-misc/v2/api-docs?group=V1.0.0"
    url17 = "http://192.168.13.242:8864/sphere/v2/api-docs?group=安全模块-检查"
    url18 = "http://192.168.13.246:8502/luban-archives/v2/api-docs?group=V1.0.0"
    url19 = "http://192.168.13.242:8864/sphere/v2/api-docs?group=%E7%94%9F%E4%BA%A7%E6%A8%A1%E5%9D%97"
    url30 = "http://192.168.13.242:8864/sphere/swagger-resources"


    # print(AnalysisSwaggerJson(url).analysis_json_data())
    # print(AnalysisSwaggerJson(url0).analysis_json_data())
    # print(AnalysisSwaggerJson(url1).analysis_json_data())
    # print(AnalysisSwaggerJson(url2).analysis_json_data())
    # print(AnalysisSwaggerJson(url3).analysis_json_data())
    # print(AnalysisSwaggerJson(url4).analysis_json_data())
    # print(AnalysisSwaggerJson(url5).analysis_json_data())
    # print(AnalysisSwaggerJson(url7).analysis_json_data())
    # print(AnalysisSwaggerJson(url6).analysis_json_data())
    # print(AnalysisSwaggerJson(url9).analysis_json_data())
    # print(AnalysisSwaggerJson(url10).analysis_json_data())
    # print(AnalysisSwaggerJson(url11).analysis_json_data())
    # print(AnalysisSwaggerJson(url12).analysis_json_data())
    # print(AnalysisSwaggerJson(url13).analysis_json_data())
    # print(AnalysisSwaggerJson(url14).analysis_json_data())
    # print(AnalysisSwaggerJson(url15).analysis_json_data())
    # print(AnalysisSwaggerJson(url16).analysis_json_data())
    # print(AnalysisSwaggerJson(url17).analysis_json_data())
    # print(AnalysisSwaggerJson(url18).analysis_json_data())
    # print(AnalysisSwaggerJson(url19).analysis_json_data())
    print(AnalysisSwaggerJson(url30).analysis_json_data())

