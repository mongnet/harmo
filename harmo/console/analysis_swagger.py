#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2020/2/15 20:00
# @Author  : hubiao
# @File    : analysis_swagger.py
import json
import os
import re
from urllib.parse import urlparse

import jsonpath
import copy
from collections import Counter
from typing import Optional
from pathlib import Path
from harmo import base_utils, http_requests
from harmo.operation import yaml_file
from harmo.base_assert import Assertions

class AnalysisSwaggerJson():
    """
    swagger自动生成接口测试用例的工具类,此类以生成json格式的测试用例
    """

    def __init__(self):
        """
        初始化类
        """
        yamlDate = yaml_file.get_yaml_data(f"{os.path.dirname(os.path.realpath(__file__))}/../config/parameConfig.yaml")
        self.default_parame = yamlDate.get("defaultParame")
        self.blacklist = yamlDate.get("blacklist")
        self.header ={"Accept": "application/json,text/plain","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2372.400 QQBrowser/9.5.10548.400","Content-Type": "application/json;charset=utf-8","Accept-Encoding": "gzip, deflate","Accept-Language": "zh-CN,zh;q=0.8"}


    def analysis_json_data(self, swaggerUrl: str, header: Optional[dict]=None):
        """
        解析json格式数据的主函数
        :return:
        """
        # 指定请求的swagger接口地址
        # 如："http://192.168.13.197:8989/builder/v2/api-docs"
        # 如："http://192.168.13.202:8081/Plan/rs/swagger/swagger.json"
        # 如："D:/Automation/standadrd_polling/data/swagger_ent_admin.json"
        try:
            http_interface_groups =[]
            if re.compile(r"(http)(s?)(://)").match(swaggerUrl):
                req = http_requests.HttpRequests(swaggerUrl)
                response = req.send_request("GET", swaggerUrl, header=header)
                Assertions.assert_code(response, response.get("status_code"), 200)
                swagger_res = response.get("source_response")
            elif base_utils.file_is_exist(swaggerUrl) and swaggerUrl.endswith(".json"):
                swaggerfile = open(base_utils.file_absolute_path(swaggerUrl),'r',encoding='utf-8-sig')
                swagger_res = json.loads(swaggerfile.read())
            else:
                raise ValueError(f"error: {swaggerUrl} 不是一个有效的swagger地址或文件(swagger地址必须以http或http开头,文件必须以.json结尾)")
            if isinstance(swagger_res,dict):
                if swagger_res.get("urls"):
                    print(f"这是一个 swagger-groups, 共有 {len(swagger_res.get('urls'))} 个group")
                    for i in swagger_res.get("urls"):
                        print(f"正在处理第 {swagger_res.get('urls').index(i)+1} 个")
                        if isinstance(i, dict) and i.get("url"):
                            req = http_requests.HttpRequests(swaggerUrl)
                            response = req.send_request("GET", swaggerUrl.split(f"{swagger_res.get('configUrl')}",1)[0] + i.get("url"), header=header)
                            Assertions.assert_code(response, response.get("status_code"), 200)
                            res = response.get("source_response")
                            if res.get("paths"):
                                http_interface_groups.append(self.__analysis(swaggerUrl,res))
                            else:
                                print(f'warning: 注意 {i.get("url")} 中没有定义接口')
                        else:
                            raise ValueError(f"error: 不是一个有效的swagger地址或文件")
                elif swagger_res.get("paths"):
                    http_interface_groups.append(self.__analysis(swaggerUrl,swagger_res))
                else:
                    print(f'warning: 注意 {swaggerUrl} 中没有定义接口')
            elif isinstance(swagger_res,list) and "swagger-resources" in swaggerUrl:
                print(f"这是一个 swagger-groups, 共有 {len(swagger_res)} 个group")
                for i in swagger_res:
                    print(f"正在处理第 {swagger_res.index(i)+1} 个")
                    if isinstance(i,dict) and i.get("url"):
                        req = http_requests.HttpRequests(swaggerUrl)
                        response = req.send_request("GET", swaggerUrl.split("/swagger-resources",1)[0]+i.get("url"), header=header)
                        Assertions.assert_code(response, response.get("status_code"), 200)
                        res = response.get("source_response")
                        if res.get("paths"):
                            http_interface_groups.append(self.__analysis(swaggerUrl,res))
                        else:
                            print(f'warning: 注意 {i.get("url")} 中没有定义接口')
                    else:
                        raise ValueError(f"error: 不是一个有效的swagger地址")
            else:
                raise ValueError(f"error: 不是一个有效的swagger地址或文件")
            return http_interface_groups
        except Exception as e:
            raise e

    def __analysis(self, swaggerUrl: str, res: dict):
        # 定义接口分组格式
        http_interface_group = {"config": {"name": "","name_en": "", "base_url": "", "version": ""},"groups": []}
        paths = res.get("paths")  # 取接口地址返回的path数据,包括了请求的路径
        self.version = res.get("openapi") if res.get("openapi") else res.get("swagger")
        # swagger
        if self.version.startswith("3"):
            self.components = res.get("components").get("schemas")  # body参数
        else:
            self.components = res.get("definitions")  # body参数
        # 获取根路径
        __basePath = jsonpath.jsonpath(res, '$..servers[?(@.url)]..url')
        if __basePath:
            server_url = urlparse(__basePath[0])
            if len(server_url.path) == 1:
                self.basePath = ""
            else:
                self.basePath =server_url.path
            self.base_url = f"{server_url.scheme}://{server_url.netloc}"
        else:
            self.basePath = res.get("basePath") if res.get("basePath") else ""  # 获取接口的根路径
            server_url = urlparse(swaggerUrl)
            self.base_url = f"{server_url.scheme}://{server_url.netloc}"
        title = res.get("info").get("title")  # 获取接口的标题
        http_interface_group["config"]["name"] = title  # 在初始化用例集字典更新值
        http_interface_group["config"]["name_en"] = self.basePath.replace("/","")
        http_interface_group["config"]["base_url"] = self.base_url
        http_interface_group["config"]["version"] = self.version
        if isinstance(paths, dict):  # 判断接口返回的paths数据类型是否dict类型
            # 获取全部path的tag名称,按tag分组
            tags = {}
            for path_key,path_value in paths.items():
                tag_name = jsonpath.jsonpath(path_value, "$..tags[0]")[0]
                if tag_name in tags.keys():
                    tags.get(tag_name).update({path_key:path_value})
                else:
                    tags.update({tag_name:{path_key:path_value}})
            # 相同tag的接口放一起，生成在同一文件中
            for tag_name,tag_value in tags.items():
                # 调试用
                # if tag_name != "设置权重值":
                #     continue
                group = {"name": "", "file_name": "", "class_name": "", "interfaces": []}
                # 生成 class_name 和 file_name
                uri_list = list(tag_value.keys())
                startswith_equal_path_list = []
                if isinstance(uri_list,list):
                    file_name = ""
                    # 避免文件名重复
                    uri_list = [self.basePath+uri for uri in uri_list if self.basePath]
                    for uri in uri_list:
                        k1 = uri.split("?")[0].replace("{", "").replace("}", "").split("/")[1:]
                        coincide_list = []
                        for i in uri_list:
                            k2 = i.split("?")[0].replace("{", "").replace("}", "").split("/")[1:]
                            coincide_list.append(k2)
                            k1 = k1 if not list(sorted(set(k1).intersection(set(k2)), key=k1.index)) else list(sorted(set(k1).intersection(set(k2)), key=k1.index))
                        # 获取path中从头开始，匹配的path目录
                        startswith_equal_path_list = base_utils.coincide_list(coincide_list)
                        file_name = "_".join(startswith_equal_path_list).replace("-", "_")
                        break
                    group["class_name"] = file_name.title().replace("_", "")
                    group["file_name"] = file_name.lower()
                for uri, value in list(tag_value.items()):
                    for method in list(value.keys()):
                        params = value[method]
                        # deprecated字段标识：接口是否已废弃，废弃接口不会被生成
                        # if "deprecated" in value.get(method).keys() and value.get(method).get("deprecated"):
                        #     print(f'warning: {uri} 已标识为废弃，废弃接口不会被生成')
                        #     continue
                        # else:
                        group["name"] = tag_name
                        interface = self.__wash_params(params, uri, method, group, startswith_equal_path_list)
                        if interface:
                            group["interfaces"].append(interface)
                # 合并相同file_name
                groups = base_utils.jpath(http_interface_group.get("groups"), check_key="file_name", sub_key="file_name")
                if groups:
                    if group.get("file_name") in groups:
                        interface_group = http_interface_group.get("groups")[groups.index(group.get("file_name"))]
                        interface_group["name"] = "_".join([interface_group.get("name"),group.get("name")])
                        interface_group["interfaces"].extend(group.get("interfaces"))
                        continue
                # 校验同一个分组中是否有相同的name_en，如有会导致方法同名
                if group.get("interfaces"):
                    repetition = {"方法名 "+key: "重复了 "+str(value)+" 次" for key, value in dict(Counter(jsonpath.jsonpath(group.get("interfaces"),"$..name_en"))).items() if value > 1}
                    if repetition:
                        print(group.get("interfaces"))
                        assert False, f"生成的接口方法名出现重名：{repetition}"
                http_interface_group["groups"].append(group)
        else:
            return f"error: paths不是一个dict类型，现在的类型为：{type(paths)}，paths的内容为:{paths}"
        return http_interface_group

    def __wash_params(self, params, uri, method, group, startswith_equal_path_list):
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
            "interface_basePath": "",
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
            "cookie_params": {},
            "cookie_params_args": [],
            "cookie_params_kwargs": [],
            "formData_params": {},
            "formData_params_args": [],
            "formData_params_kwargs": [],
            "validate": [],
            "output": []
        }
        # 这里程序可能没有写summary，只能用operationId来替代了
        name = params.get("summary").replace("/", "_") if params.get("summary") else params.get("operationId")
        http_interface["name_cn"] = name
        # 通过url生成测试方法名，path中相同的前部分会被去掉
        repuris = [u.replace("{", "").replace("}", "").replace("_", "") for u in uri.split("/")]
        # 去除空字符串
        original_list = [repuri for repuri in repuris if repuri != '']
        # 去除相邻重复项
        from itertools import groupby
        unique_list = [key for key, group in groupby(original_list)]
        if not unique_list and params.get("operationId"):
            operationId = params.get("operationId").split("_")
            if len(operationId) >= 1:
                unique_list.append(operationId[0].lower())
        if not unique_list:
            unique_list.extend(startswith_equal_path_list)
        unique_list.append(method)
        name_en = "_".join(unique_list).replace("-", "_")
        http_interface["name_en"] = name_en
        http_interface["method"] = method.upper()
        http_interface["uri"] = uri
        http_interface["interface_basePath"] = self.basePath
        # 调试用
        # if name != "资源下的组织节点列表(指挥中心)":
        #     return
        # swagger 3.0 当请求有 body 传参时，没有 in: "body"了，现使用 requestBody 标示请求体
        if params.get("requestBody"):
            requestBody_schema = jsonpath.jsonpath(params.get("requestBody"), "$..schema")
            if requestBody_schema:
                self.__jiexi(requestBody_schema[0], http_interface)
                # schema type为array时，已把变量命名成 array_string，后续直接传数组即可
                if requestBody_schema[0].get("type") == "array":
                    if isinstance(http_interface["body"],str) and http_interface["body"].startswith("$array_"):
                        pass
                    else:
                        bady = http_interface["body"]
                        del http_interface["body"]
                        http_interface.update({"body": [bady]})
                elif not requestBody_schema[0].get("properties") and not requestBody_schema[0].get("$ref"):
                    bady = http_interface["body"]
                    del http_interface["body"]
                    http_interface.update({"body": bady})
                    print(f"warning: {uri} 为post接口,但请求体是空对象,请确认接口定义是否正确")
        #请求参数，未解析的参数字典
        parameters = params.get("parameters")
        if not parameters:  # 确保参数字典存在
            parameters = {}
        for each in parameters:
            ref = jsonpath.jsonpath(each, "$..$ref")
            if each.get("in") == "body":
                schema = each.get("schema")
                if schema:
                    self.__jiexi(schema, http_interface, each=each)
                    # schema type为array时，已把变量命名成 array_string，后续直接传数组即可
                    if schema.get("type") == "array":
                        if isinstance(http_interface["body"],str) and http_interface["body"].startswith("$array_"):
                            pass
                        else:
                            bady = http_interface["body"]
                            del http_interface["body"]
                            http_interface.update({"body": [bady]})
            elif each.get("in") == "query":
                if ref:
                    # 拆分这个ref，根据实际情况来取第几个/反斜杠
                    # schema.get("originalRef") if schema.get("originalRef") else ref.split("/")[-1]
                    param_key = ref[0].split("/")[-1]
                    properties = self.components.get(param_key).get("properties")
                    for key, value in properties.items():
                        if value.get("type") == "array":
                            if "items" in value and "$ref" in value.get("items"):
                                http_interface["query_params"].update({key: value.get("type")})
                            elif "items" in value:
                                http_interface["query_params"].update({key: value.get("type")+"_"+value.get("items").get("type")})
                            else:
                                http_interface["query_params"].update({key: value.get("type")})
                        else:
                            http_interface["query_params"].update({key: value.get("type")})
                        if "description" in value:
                            http_interface["params_description"].update({key: value.get("type")+"," if value.get("type") else "" + value.get("description") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            if value.get("schema"):
                                http_interface["params_description"].update({name: value.get("schema").get("type") + (",必填" if each.get("required") else ",非必填")})
                            else:
                                http_interface["params_description"].update({name: value.get("type") if value.get("type") else "" + (",必填" if each.get("required") else ",非必填")})
                else:
                    name = each.get("name")
                    if each.get("schema"):
                        if "items" in each.get("schema"):
                            http_interface["query_params"].update({name: each.get("schema").get("type") + "_" + each.get("schema").get("items").get("type")})
                        else:
                            http_interface["query_params"].update({name: each.get("schema").get("type")})
                    else:
                        http_interface["query_params"].update({name: each.get("type")})
                    if "description" in each:
                        if each.get("schema"):
                            http_interface["params_description"].update({name: each.get("schema").get("type") + "," + each.get("description") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            http_interface["params_description"].update({name: each.get("type")+"," if each.get("type") else "" + each.get("description") + (",必填" if each.get("required") else ",非必填")})
                    else:
                        if each.get("schema"):
                            http_interface["params_description"].update({name: each.get("schema").get("type") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            http_interface["params_description"].update({name: each.get("type") if each.get("type") else "" + (",必填" if each.get("required") else ",非必填")})
            elif each.get("in") == "path":
                if ref:
                    # 拆分这个ref，根据实际情况来取第几个/反斜杠
                    param_key = ref[0].split("/")[-1]
                    properties = self.components.get(param_key).get("properties")
                    for key, value in properties.items():
                        if value.get("type") == "array":
                            if "items" in value and "$ref" in value.get("items"):
                                http_interface["path_params"].update({key: value.get("type")})
                            elif "items" in value:
                                http_interface["path_params"].update({key: value.get("type")+"_"+value.get("items").get("type")})
                            else:
                                http_interface["path_params"].update({key: value.get("type")})
                        else:
                            http_interface["path_params"].update({key: value.get("type")})
                        if "description" in value:
                            http_interface["params_description"].update({key: value.get("type")+"," if value.get("type") else "" + value.get("description") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            if value.get("schema"):
                                http_interface["params_description"].update({name: value.get("schema").get("type") + (",必填" if each.get("required") else ",非必填")})
                            else:
                                http_interface["params_description"].update({name: value.get("type") if value.get("type") else "" + (",必填" if each.get("required") else ",非必填")})
                else:
                    name = each.get("name")
                    if each.get("schema"):
                        if "items" in each.get("schema"):
                            http_interface["path_params"].update({name: each.get("schema").get("type") + "_" + each.get("schema").get("items").get("type")})
                        else:
                            http_interface["path_params"].update({name: each.get("schema").get("type")})
                    else:
                        http_interface["path_params"].update({name: each.get("type")})
                    if "description" in each:
                        if each.get("schema"):
                            http_interface["params_description"].update({name: each.get("schema").get("type") + "," + each.get("description") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            http_interface["params_description"].update({name: each.get("type")+"," if each.get("type") else "" + each.get("description") + (",必填" if each.get("required") else ",非必填")})
                    else:
                        if each.get("schema"):
                            http_interface["params_description"].update({name: each.get("schema").get("type") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            http_interface["params_description"].update({name: each.get("type") if each.get("type") else "" + (",必填" if each.get("required") else ",非必填")})
            elif each.get("in") == "cookie":
                if ref:
                    # 拆分这个ref，根据实际情况来取第几个/反斜杠
                    param_key = ref[0].split("/")[-1]
                    properties = self.components.get(param_key).get("properties")
                    for key, value in properties.items():
                        if value.get("type") == "array":
                            if "items" in value and "$ref" in value.get("items"):
                                http_interface["cookie_params"].update({key: value.get("type")})
                            elif "items" in value:
                                http_interface["cookie_params"].update({key: value.get("type")+"_"+value.get("items").get("type")})
                            else:
                                http_interface["cookie_params"].update({key: value.get("type")})
                        else:
                            http_interface["cookie_params"].update({key: value.get("type")})
                        if "description" in value:
                            http_interface["params_description"].update({key: value.get("type")+"," if value.get("type") else "" + value.get("description") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            if value.get("schema"):
                                http_interface["params_description"].update({name: value.get("schema").get("type") + (",必填" if each.get("required") else ",非必填")})
                            else:
                                http_interface["params_description"].update({name: value.get("type") if value.get("type") else "" + (",必填" if each.get("required") else ",非必填")})
                else:
                    name = each.get("name")
                    if each.get("schema"):
                        if "items" in each.get("schema"):
                            http_interface["cookie_params"].update({name: each.get("schema").get("type") + "_" + each.get("schema").get("items").get("type")})
                        else:
                            http_interface["cookie_params"].update({name: each.get("schema").get("type")})
                    else:
                        http_interface["cookie_params"].update({name: each.get("type")})
                    if "description" in each:
                        if each.get("schema"):
                            http_interface["params_description"].update({name: each.get("schema").get("type") + "," + each.get("description") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            http_interface["params_description"].update({name: each.get("type")+"," if each.get("type") else "" + each.get("description") + (",必填" if each.get("required") else ",非必填")})
                    else:
                        if each.get("schema"):
                            http_interface["params_description"].update({name: each.get("schema").get("type") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            http_interface["params_description"].update({name: each.get("type") if each.get("type") else "" + (",必填" if each.get("required") else ",非必填")})
            elif each.get("in") == "formData":
                if ref:
                    # 拆分这个ref，根据实际情况来取第几个/反斜杠
                    param_key = ref[0].split("/")[-1]
                    properties = self.components.get(param_key).get("properties")
                    for key, value in properties.items():
                        if value.get("type") == "array":
                            if "items" in value and "$ref" in value.get("items"):
                                http_interface["formData_params"].update({key: value.get("type")})
                            elif "items" in value:
                                http_interface["formData_params"].update({key: value.get("type")+"_"+value.get("items").get("type")})
                            else:
                                http_interface["formData_params"].update({key: value.get("type")})
                        else:
                            http_interface["formData_params"].update({key: value.get("type")})
                        http_interface.update({"body_binary": f"${key}$"})
                        if "description" in value:
                            http_interface["params_description"].update({key: value.get("type") if value.get("type") else "" + value.get("description") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            if each.get("schema"):
                                http_interface["params_description"].update({name: each.get("schema").get("type") + (",必填" if each.get("required") else ",非必填")})
                            else:
                                http_interface["params_description"].update({name: each.get("type") if each.get("type") else "" + (",必填" if each.get("required") else ",非必填")})
                else:
                    name = each.get("name")
                    if each.get("schema"):
                        if "items" in each.get("schema"):
                            http_interface["formData_params"].update({name: each.get("schema").get("type") + "_" + each.get("schema").get("items").get("type")})
                        else:
                            http_interface["formData_params"].update({name: each.get("schema").get("type")})
                    else:
                        http_interface["formData_params"].update({name: each.get("type")})
                    http_interface.update({"body_binary": f"${each.get('name')}$"})
                    if "description" in each:
                        if each.get("schema"):
                            http_interface["params_description"].update({name: each.get("schema").get("type") + "," + each.get("description") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            http_interface["params_description"].update({name: each.get("type")+"," if each.get("type") else "" + each.get("description") + (",必填" if each.get("required") else ",非必填")})
                    else:
                        if each.get("schema"):
                            http_interface["params_description"].update({name: each.get("schema").get("type") + (",必填" if each.get("required") else ",非必填")})
                        else:
                            http_interface["params_description"].update({name: each.get("type") if each.get("type") else "" + (",必填" if each.get("required") else ",非必填")})
            elif each.get("in") == "header":
                name = each.get("name")
                for key in each:
                    if "example" in key:
                        http_interface["headers"].update({name: each[key]})
                    else:
                        http_interface["headers"].update({name: "$"+name.replace("-", "_")})
            else:
                print(f"warning: 出现未处理的请求类型 {each.get('in')} ，请联系作者处理")
        # 把 formData_params 的 key 组装成新的 query_params_url ,生成用例时添加成测试方法的参数
        if "formData_params" in http_interface and http_interface["formData_params"]:
            args = []
            kwargs = []
            http_interface["formData_params_field_type"] = copy.deepcopy(http_interface["formData_params"])
            for key, value in http_interface["formData_params"].items():
                self.__wash_body(key, http_interface["formData_params"], args, kwargs, parameters_form="formData")
            http_interface["formData_params_args"] = list(set(args))
            http_interface["formData_params_kwargs"] = list(set(kwargs))
        # 把 query_params 的 key 组装成新的 query_params_url ,生成用例时添加成测试方法的参数
        if "query_params" in http_interface and http_interface["query_params"]:
            args = []
            kwargs = []
            http_interface["query_params_field_type"] = copy.deepcopy(http_interface["query_params"])
            for key, value in http_interface["query_params"].items():
                self.__wash_body(key, http_interface["query_params"], args, kwargs, parameters_form="query")
            http_interface["query_params_args"] = list(set(args))
            http_interface["query_params_kwargs"] = list(set(kwargs))
        # 把 path_params 的 key 组装成新的 path_params_url ,生成用例时添加成测试方法的参数
        if "path_params" in http_interface.keys() and http_interface["path_params"]:
            args = []
            http_interface["path_params_field_type"] = copy.deepcopy(http_interface["path_params"])
            for key, value in http_interface["path_params"].items():
                args.append(key)
            http_interface["path_params_args"] = list(set(args))
        # 把 cookie_params 的 key 组装成新的 cookie_params_url ,生成用例时添加成测试方法的参数
        if "cookie_params" in http_interface.keys() and http_interface["cookie_params"]:
            args = []
            kwargs = []
            http_interface["cookie_params_field_type"] = copy.deepcopy(http_interface["cookie_params"])
            for key, value in http_interface["cookie_params"].items():
                self.__wash_body(key, http_interface["cookie_params"], args, kwargs, parameters_form="cookie")
            http_interface["cookie_params_args"] = list(set(args))
            http_interface["cookie_params_kwargs"] = list(set(kwargs))
        # 把 body 的 key 组装成新的 body_param ,生成用例时添加成测试方法的参数
        if "body" in http_interface.keys() and http_interface["body"]:
            self.args = []
            self.kwargs = []
            body_field_type = copy.deepcopy(http_interface["body"])
            http_interface["body_field_type"] = ["array_string"] if body_field_type == "$array_string$" else body_field_type
            self.__recursion(http_interface["body"])
            http_interface["body_params_args"] = (list(set(self.args)) if http_interface["body_params_args"]==[] else http_interface["body_params_args"])
            http_interface["body_params_kwargs"] = (list(set(self.kwargs)) if http_interface["body_params_kwargs"]==[] else http_interface["body_params_kwargs"])
        # 把 args、kwargs 组装在一起，方便后续调用
        http_interface["params_args"] = list(set(http_interface["path_params_args"] + http_interface["cookie_params_args"] + http_interface["query_params_args"] + http_interface["formData_params_args"] + http_interface["body_params_args"]))
        http_interface["params_kwargs"] = list(set(http_interface["cookie_params_kwargs"] + http_interface["query_params_kwargs"]+ http_interface["formData_params_kwargs"] + http_interface["body_params_kwargs"]))
        http_interface["params_args_nobody"] = list(set(http_interface["path_params_args"] + http_interface["cookie_params_args"] + http_interface["query_params_args"]  + http_interface["formData_params_args"]))
        http_interface["params_kwargs_nobody"] = list(set(http_interface["cookie_params_kwargs"] + http_interface["query_params_kwargs"] + http_interface["formData_params_kwargs"]))
        # 把 params_description 组装成 params_description_list 生成用例时,生成字段备注使用
        if "params_description" in http_interface.keys():
            params_description = []
            for k, v in http_interface["params_description"].items():
                params_description.append(k + ": " + v.replace("\n", "").replace("\r", "").replace("\t", ""))
            http_interface["params_description_list"] = params_description

        # 处理responses
        # responses = params.get("responses")
        # for key, value in responses.items():
        #     schema = value.get("schema")
        #     description = value.get("description")
        #     if description == "OK":
        #         if schema:
        #             ref = schema.get("$ref")
        #             if ref:
        #                 param_key = schema.get("originalRef") if schema.get("originalRef") else ref.split("/")[-1]
        #                 res = self.components.get(param_key).get("properties")
        #                 i = 0
        #                 for k, v in res.items():
        #                     if "example" in v.keys():
        #                         print("res",res)
        #                         http_interface["validate"].append({"eq": []})
        #                         http_interface["validate"][i]["eq"].append({k:v.get("example")})
        #                         http_interface["validate"][i]["eq"].append({"description":v.get("description")})
        #                         # http_interface["validate"][i]["eq"].append("content." + k)
        #                         # http_interface["validate"][i]["eq"].append(v.get("example"))
        #                         # http_interface["validate"][i]["eq"].append(v.get("description"))
        #                         i += 1
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

    def __jiexi(self, schema, http_interface, ephemeral_key=None, key_type=None, body=None, each=None):
        if "$ref" in schema or schema.get("type") == "object":
            if schema.get("type") == "object":
                properties = schema.get("properties")
                requireds = schema.get("required")
            else:
                ref = schema.get("$ref")
                # 拆分这个ref，根据实际情况来取第几个/反斜杠
                param_key = schema.get("originalRef") if schema.get("originalRef") else ref.split("/")[-1]
                try:
                    properties = self.components.get(param_key).get("properties")
                    requireds = self.components.get(param_key).get("required")
                except:
                    if len(http_interface["body"]) == 0:
                        del http_interface["body"]
                        body = each.get("name")
                        body_description = each.get("description") if each.get("description") else body
                        http_interface.update({"body": f"${body}$"})
                        http_interface["body_params_kwargs"].append(f"${body}=None$")
                        http_interface["params_description"].update({f"${body}$": f"{body_description}"})
                    print(f"warning: {http_interface.get('name_cn')} 接口的 {ref} 定义，没有properties节点信息，请确认程序生成的swagger信息是否正确")
                    return
            ephemeral_data = {}

            # print("schema:", schema)
            # print("param_key:", param_key)
            # print("properties:", self.definitions.get(param_key))
            # print("properties:", properties)
            # print("requireds:", requireds)
            # print("ephemeral_key:", ephemeral_key)
            # print("body:", body)
            if properties:
                for key, value in properties.items():
                    # 字段是否必填
                    required = True if isinstance(requireds,list) and key in requireds else False
                    if "type" in value:
                        if ephemeral_key:
                            ephemeral_data.update({key: value["type"]})
                            if "description" in value:
                                http_interface["params_description"].update({key: value.get("type") + "," + value.get("description") + (",可用值:" + ",".join(value.get("enum")) if "enum" in value.keys() else "") + (",必填" if required else ",非必填")})
                            if "items" in value and "$ref" in value.get("items"):
                                pass
                        else:
                            if "description" in value:
                                http_interface["params_description"].update({key: value.get("type") + "," + value.get("description") + (",可用值:" + ",".join(value.get("enum")) if "enum" in value.keys() else "") + (",必填" if required else ",非必填")})
                            else:
                                http_interface["params_description"].update({key: value.get("type") + (",必填" if value.get("required") else ",非必填")})
                            http_interface["body"].update({key: value.get("type")})
                        if "items" in value and "$ref" in value.get("items"):
                            if value.get("items").get("$ref") == ref:
                                # 跳出递归死循环
                                pass
                            else:
                                if ephemeral_key is None:
                                    http_interface["body"].update({key: []})
                                    self.__jiexi(value.get("items"), http_interface, key, value["type"], body=http_interface["body"][key])
                                else:
                                    if body is not None:
                                        if key_type == "array":
                                            if key in ephemeral_data:
                                                ephemeral_data.update({key: []})
                                            else:
                                                body.append({key: []})
                                    self.__jiexi(value.get("items"), http_interface, key, value["type"], body=ephemeral_data)
                    elif "$ref" in value:
                        if value.get("$ref") == ref:
                            # 跳出递归死循环
                            pass
                        else:
                            # print("value:",value)
                            # print("key:",key)
                            self.__jiexi(value, http_interface, key)
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
                        # print(ephemeral_key.split("_")[-1])
                        # print("ephemeral_data:",ephemeral_data)
                        http_interface["body"].update({ephemeral_key.split("_")[-1]: ephemeral_data})
        else:
            for key, value in schema.items():
                if isinstance(value, dict) and "$ref" in value:
                    self.__jiexi(value, http_interface, ephemeral_key)
                    return
            # 处理body为array时的情况
            if schema.get("type") == "array" and ephemeral_key is None:
                del http_interface["body"]
                schema_list = [str(x) for x in base_utils.get_all_value(schema, filter_key=["description"]) if isinstance(x,int)]
                body = "_".join(schema_list)
                if body:
                    http_interface["body_params_kwargs"].append(f"${body}=None$")
                    http_interface["params_description"].update({f"${body}$": f"${body}$"})
                    http_interface.update({"body": f"${body}$"})
                else:
                    http_interface["body_params_kwargs"].append(f"$body=None$")
                    http_interface["params_description"].update({f"$body$": f"$None$"})
                    http_interface.update({"body": f"$body$"})
            # 处理body为string时的情况
            elif schema.get("type") == "string" and ephemeral_key is None:
                schema_list = [str(x) for x in base_utils.get_all_value(schema, filter_key=["description"]) if isinstance(x,int)]
                body = "_".join(schema_list)
                if "binary" in schema_list:
                    http_interface.update({"body_binary": f"${body}$"})
                if body:
                    http_interface["body_params_kwargs"].append(f"${body}=None$")
                    http_interface["params_description"].update({f"${body}$": f"${body}$"})
                    http_interface.update({"body": f"${body}$"})
                else:
                    http_interface["body_params_kwargs"].append(f"$body=None$")
                    http_interface["params_description"].update({f"$body$": f"$None$"})
                    http_interface.update({"body": f"$body$"})

    def __recursion(self, data):
        """
        递归解析数据
        :param data:
        :return:
        """
        if isinstance(data, list):
            for itme in data:
                self.__recursion(itme)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    self.kwargs.append(key + "=$None$")
                    self.__recursion(value)
                    continue
                if isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, list):
                            self.kwargs.append(key + "=$None$")
                            self.__recursion(v)
                            continue
                        self.__wash_body(k, value, self.args, self.kwargs)
                    continue
                self.__wash_body(key, data, self.args, self.kwargs)

    def __wash_body(self, arg, body, list_args, list_kwargs, parameters_form=None):
        """
        清洗body 数据
        :param arg: 指定key
        :param body: 需要清洗的 body 数据
        :param list_args: 无默认值的参数列表
        :param list_kwargs: 有默认值的参数列表
        :param parameters_form: 传参方式
        :return:
        """
        if arg not in body:
            return
        # 无默认值或在黑名单中的参数无需处理
        if arg in list_args or arg in self.blacklist:
            return
        # 接口传参默认值处理
        if arg in self.default_parame:
            kwarg = ""
            if isinstance(self.default_parame[arg], int):
                kwarg = str(self.default_parame[arg])
            elif isinstance(self.default_parame[arg], str):
                # 前后加$表示变量
                if self.default_parame[arg].startswith("$") and self.default_parame[arg].endswith("$"):
                    kwarg = self.default_parame[arg]
                else:
                    # 如果是字符串常量须要加引号
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
    url = "http://192.168.13.246:8864/sphere/swagger-resources"
    url0 = "http://192.168.13.246:8182/Plan/rs/swagger/swagger.json"
    url1 = "http://192.168.13.246:8182/gateway/builder/v2/api-docs"
    url3 = "http://192.168.13.246:8182/pdscommon/rs/swagger/swagger.json"
    url4 = "http://192.168.13.246:8182/pdsdoc/rs/swagger/swagger.json"
    url5 = "http://192.168.13.246:8182/BuilderCommonBusinessdata/rs/swagger/swagger.json"
    url7 = "http://192.168.13.246:8182/openapi/rs/swagger/swagger.json"
    url12 = "http://192.168.13.246:8182/BuilderCommonBusinessdata/rs/swagger/swagger.json"
    url14 = "http://192.168.13.246:8182/gateway/luban-meter/v2/api-docs?group=V1.0.0"
    url15 = "http://192.168.13.246:8182/gateway/luban-infrastructure-center/v2/api-docs?group=V1.0.0"
    url16 = "http://192.168.13.246:8182/gateway/luban-misc/v2/api-docs?group=V1.0.0"
    url18 = "http://192.168.13.246:8502/luban-archives/v2/api-docs?group=V1.0.0"
    url31 = "http://192.168.13.157:8022/luban-bi/v2/api-docs?group=%E6%95%B0%E6%8D%AE%E6%BA%90"
    url32 = "http://192.168.13.246:8864/sphere/v2/api-docs?group=%E5%85%AC%E5%85%B1%E4%BB%BB%E5%8A%A1%E6%A8%A1%E5%9D%97"
    url33 = "http://192.168.13.157:8022/luban-bi/swagger-resources"
    url40 = "http://192.168.13.178:16636/plan/v3/api-docs"
    url41 = "D:/Automation/harmo/data/swagger_ent_admin.json"
    url43 = "https://sg.luban.fit/x-auth-server/swagger/json"
    url44 = "http://192.168.13.172:19900/auth/v3/api-docs/%E6%8E%A5%E5%8F%A3%E6%96%87%E6%A1%A3"
    url45 = "http://192.168.13.172:19902/ent-admin-user/v3/api-docs/swagger-config"
    url46 = "http://192.168.13.172:18000/process/v3/api-docs"
    url47 = "http://192.168.13.178:8864/sphere/v3/api-docs"
    url48 = "http://192.168.13.172:19901/ent-admin-org/v3/api-docs/swagger-config"
    url49 = "http://192.168.13.172:19904/acl/v3/api-docs/接口文档"



    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url0))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url1))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url3))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url4))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url5))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url7))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url12))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url14))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url15))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url16))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url18))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url31))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url32))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url33))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url40))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url41))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url43))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url44))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url45))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url46))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url47))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url48))
    # print(AnalysisSwaggerJson().analysis_json_data(swaggerUrl=url49,header={"Authorization": "Basic YWRtaW46MTExMTEx"}))
