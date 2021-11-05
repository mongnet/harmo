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
        self.tags_list = []  # 接口分组标签
        # 定义接口分组格式
        self.http_interface_group = {"config": {"name": "","name_en": "","host": "", "base_url": ""},"groups": []}
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
            response = requests.get(self.url)
            assert response.status_code == 200,f"swagger地址无法访问，响应状态码为{response.status_code}"
            res = response.json()
        except Exception as e:
            raise e

        self.data = res.get("paths")  # 取接口地址返回的path数据,包括了请求的路径
        self.basePath = res.get("basePath") if res.get("basePath") else ""  # 获取接口的根路径
        # 第一错，swagger文档是ip地址，使用https协议会错误,注意接口地址的请求协议
        self.host = "http://" + res.get("host") if res.get("host") else ""
        self.title = res["info"]["title"]  # 获取接口的标题
        self.http_interface_group["config"]["name"] = self.title  # 在初始化用例集字典更新值
        self.http_interface_group["config"]["name_en"] = self.url.split("/")[3].lower().replace("-", "_") if self.url.startswith("http") else self.url.split("/")[1].lower().replace("-", "_")
        self.http_interface_group["config"]["host"] = self.host
        self.http_interface_group["config"]["base_url"] = self.basePath
        self.definitions = res.get("definitions")  # body参数

        for tag_dict in res.get("tags"):
            self.tags_list.append(tag_dict)
        if isinstance(self.data, dict):  # 判断接口返回的paths数据类型是否dict类型
            # 前面已经把接口返回的结果tags分别写入了tags_list空列表,再从json对应的tag往里面插入数据
            for tag in self.tags_list:
                self.group = {"name": "", "file_name": "", "class_name": "", "interfaces": []}
                self.repetition_operationId = []
                for uri, value in list(self.data.items()):
                    for method in list(value.keys()):
                        params = value[method]
                        # deprecated字段标识：接口是否被弃用，暂时无法判断
                        if not "deprecated" in value.keys():
                            if params.get("tags")[0] == tag.get("name"):
                                self.group["name"] = tag.get("name")
                                interface = self.wash_params(params, uri, method)
                                self.group["interfaces"].append(interface)
                        else:
                            print(f'interface path: {uri}, if name: {params["operationId"]}, is deprecated.')
                            break
                    # 优化循环性能，已经处理过的数据删除掉，避免重复循环
                    # del self.data[f"{uri}"]
                # 生成 class_name 和 file_name
                uri_list = base_utils.jpath(self.group, check_key="uri", sub_key="uri")
                if isinstance(uri_list,list):
                    file_name = ""
                    for uri in uri_list:
                        k1 = uri.split("?")[0].split("/{", 1)[0].split("/")[1:]
                        for i in uri_list:
                            k2 = i.split("?")[0].split("/{", 1)[0].split("/")[1:]
                            k1 = k1 if not list(sorted(set(k1).intersection(set(k2)), key=k1.index)) else list(sorted(set(k1).intersection(set(k2)), key=k1.index))
                        file_name = "_".join(k1).replace("-", "_").title().replace("_", "")
                        break
                    self.group["class_name"] = file_name
                    self.group["file_name"] = file_name[0].lower()+file_name[1:]
                # 合并相同file_name
                groups = base_utils.jpath(self.http_interface_group.get("groups"), check_key="file_name", sub_key="file_name")
                if groups:
                    if self.group.get("file_name") in groups:
                        interface_group = self.http_interface_group.get("groups")[groups.index(self.group.get("file_name"))]
                        interface_group["name"] = "_".join([interface_group.get("name"),self.group.get("name")])
                        interface_group["interfaces"].extend(self.group.get("interfaces"))
                        continue
                self.http_interface_group["groups"].append(self.group)
        else:
            return "error"
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
        name_en_list = base_utils.jpath(self.group["interfaces"], check_key="name_en", sub_key="name_en")
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
        # if name != "新增标段、单项、单位工程":
        #     return
        # if name != "创建任务中检查信息 （iworksweb）":
        #     return
        for each in parameters:
            if each.get("in") == "body":
                # if method.upper() == "GET":
                #     raise SyntaxError("语法错误: GET方法不应该有请求体,接口名为："+api)
                schema = each.get("schema")
                if schema:
                    self.jiexi(schema, http_interface)
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
                    http_interface["params_description"].update({name: each["description"]})

            if each.get("in") == "path":
                name = each.get("name")
                http_interface["path_params"].update({name: each.get("type")})
                if "description" in each.keys():
                    http_interface["params_description"].update({name: each["description"]})

            if each.get("in") == "cookie":
                name = each.get("name")
                http_interface["cookie_params"].update({name: each.get("type")})
                if "description" in each.keys():
                    http_interface["params_description"].update({name: each["description"]})

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
                    res = self.definitions[param_key]["properties"]
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

    def jiexi(self,schema,http_interface,ephemeral_key=None,key_type=None,body=None):
        if "$ref" in schema.keys():
            ref = schema.get("$ref")
            if ref:
                # 拆分这个uri，根据实际情况来取第几个/反斜杠
                param_key = ref.split("/", 2)[-1]
                try:
                    param = self.definitions[param_key]["properties"]
                except KeyError:
                    print(f"警告: {schema}没有properties节点信息，请确认程序生成的swagger信息是否正确")
                    return
                ephemeral_data = {}
                for key, value in param.items():
                    if "type" in value.keys():
                        if ephemeral_key:
                            ephemeral_data.update({key: value["type"]})
                            if "description" in value.keys():
                                http_interface["params_description"].update({key: value["description"] + ",可用值:" + ",".join(value["enum"]) if "enum" in value.keys() else value["description"]})
                            if "items" in value.keys() and "$ref" in value.get("items"):
                                pass
                        else:
                            if "description" in value.keys():
                                http_interface["params_description"].update({key: value["description"] + ",可用值:" + ",".join(value["enum"]) if "enum" in value.keys() else value["description"]})
                            else:
                                http_interface["params_description"].update({key: value["type"]})
                            http_interface["body"].update({key: value["type"]})
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
                http_interface["params_description"].update({f"${body}$": f"${body}$"})
                http_interface["body_params_args"].append(f"${body}$=$None$")
            elif schema.get("type") == "string" and ephemeral_key is None:
                body = "_".join(base_utils.get_all_value(schema))
                http_interface.update({"body": f"${body}$"})
                http_interface["params_description"].update({f"${body}$": f"${body}$"})
                http_interface["body_params_args"].append(f"${body}$=$None$")

    def recursion(self,data):
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
        # 无默认值的参数无需处理
        if arg in list_args and arg in self.blacklist:
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
        # 当parameters_form不是None或不是path参数时，参数默认值设置为None
        elif parameters_form is not None or parameters_form != "path":
            list_kwargs.append(arg + "=$None$")
        elif body[arg] == "boolean":
            list_kwargs.append(arg + "=$False$")
        elif arg not in self.blacklist:
            list_args.append(arg)
        # body 请求体参数化处理
        body[arg] = "$" + arg + "$"


if __name__ == "__main__":
    url = "http://192.168.13.246:8182/Plan/rs/swagger/swagger.json"
    url1 = "http://192.168.13.246:8182/gateway/builder/v2/api-docs"
    url2 = "http://192.168.3.195:8989/LBprocess/v2/api-docs"
    url3 = "http://192.168.3.195/pdscommon/rs/swagger/swagger.json"
    url4 = "http://192.168.3.195/pdsdoc/rs/swagger/swagger.json"
    url5 = "http://192.168.3.195/BuilderCommonBusinessdata/rs/swagger/swagger.json"
    url6 = "http://192.168.13.233:8080/auth-server/v2/api-docs"
    url7 = "http://192.168.3.195/openapi/rs/swagger/swagger.json"
    # url9 = "http://192.168.3.236:8083/monitor/v2/api-docs?group=center"
    # url10 = "http://192.168.3.199:9083/misc/v2/api-docs?group=信息深度(center端)"
    # url11 = "http://192.168.3.199:9083/misc/v2/api-docs?group=信息深度(客户端)"
    url12 = "http://192.168.3.195/BuilderCommonBusinessdata/rs/swagger/swagger.json"
    url13 = "http://192.168.3.195/gateway/process/v2/api-docs"
    url14 = "http://192.168.13.193:8182/gateway/luban-meter/v2/api-docs?group=V1.0.0"
    url15 = "http://192.168.13.240:8182/gateway-240/luban-infrastructure-center/v2/api-docs?group=V1.0.0"
    url16 = "http://192.168.13.246:8182/gateway/luban-misc/v2/api-docs?group=V1.0.0"
    url17 = "http://192.168.13.66:7790/things/v2/api-docs?group=%E4%B8%9A%E5%8A%A1%E6%8E%A5%E5%8F%A3"


    # print(AnalysisSwaggerJson(url).analysis_json_data())
    print(AnalysisSwaggerJson(url1).analysis_json_data())
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
    # print(AnalysisSwaggerJson(url15).analysis_json_data())
    # print(AnalysisSwaggerJson(url16).analysis_json_data())

