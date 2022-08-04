#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2019/4/3 15:12
# @Author  : hubiao
# @File    : base_assert.py
import operator
from collections import Counter

import allure

from luban_common import base_utils


class Assertions:
    """
    公共断言方法
    """

    @classmethod
    @allure.step("校验status_code和code")
    def assert_all_code(self, response, expected_http_code, expected_code):
        """
        即将废弃
        校验status_code和code状态码
        :param response: 响应数据
        :param expected_http_code: 预期的http状态码
        :param expected_code: 预期code状态码
        :return:
        """
        assert response.get("status_code") == expected_http_code,f'''校验失败,实际http_code为:{response.get("status_code")},预期http_code为:{expected_http_code}
               
        请求URL:{response.get("request_url")}
        请求Method:{response.get("request_method")}
        请求Headers:{response.get("request_header")}
        请求Params:{response.get("request_params")}
        请求Payload:{response.get("request_payload")}
        响应status_code:{response.get("status_code")}
        响应信息:{response.get("Response_text") if response.get("source_response") is None else response.get("source_response")}'''

        assert response.get("code")[0] == expected_code,f'''校验失败,实际code为:{response.get("code")[0]},预期code为:{expected_code}
               
        请求URL:{response.get("request_url")}
        请求Method:{response.get("request_method")}
        请求Headers:{response.get("request_header")}
        请求Params:{response.get("request_params")}
        请求Payload:{response.get("request_payload")}
        响应status_code:{response.get("status_code")}
        响应信息:{response.get("Response_text") if response.get("source_response") is None else response.get("source_response")}'''

    @classmethod
    @allure.step("校验状态码,实际值为:{2},预期值为:{3}")
    def assert_code(self, response, reality_code, expected_code):
        """
        验证response响应体中的code或status_code状态码
        assert_code 相对于 assert_equal_value 断言 assert_code 可返回全部响应信息,方便code错误时查看响应信息
        :param response: 响应体
        :param reality_code: 响应体中的code或status_code状态码
        :param expected_code: 预期code或status_code状态码
        :return:
        """
        assert reality_code == expected_code, f'''校验失败,实际值为:{reality_code},预期值为:{expected_code}
        
        请求URL:{response.get("request_url")}
        请求Method:{response.get("request_method")}
        请求Headers:{response.get("request_header")}
        请求Params:{response.get("request_params")}
        请求Payload:{response.get("request_payload")}
        响应status_code:{response.get("status_code")}
        响应信息:{response.get("Response_text") if response.get("source_response") is None else response.get("source_response")}'''

    @classmethod
    @allure.step("校验数据集中指定key的值,预期key为:{2},预期值为:{3}")
    def assert_assign_attribute_value(self, data,key,expected_value):
        """
        校验数据集中指定key的值是否等于预期值
        :param data:校验的data
        :param key:预期key
        :param expected_value:预期值
        :return:
        """
        if isinstance(data[key], list) and isinstance(expected_value,list):
            if data[key] != expected_value:
                assert False, f"预期值不等于实际值,实际值为:{data[key]}, 预期值为:{expected_value}"
        elif isinstance(data[key], (str,int,float)):
            assert data[key] == expected_value, f"预期值不等于实际值,实际值为:{data[key]}, 预期值为:{expected_value}"
        else:
            assert False, f"当前传入的实际值类型为{type(data[key])},预期值类型为{type(expected_value)}, 现只支持list,str,int,float的校验, 其余暂不支持"

    @classmethod
    @allure.step("校验数据集中存在预期值,预期值为:{2}")
    def assert_in_value(self, data,expected_value):
        """
        校验数据集中存在预期值
        :param data: 校验的data
        :param expected_value:预期值
        :return:
        """
        if isinstance(data,(list,dict)):
            if isinstance(expected_value, dict):
                for value in base_utils.get_all_value(expected_value):
                    assert value in base_utils.get_all_value(data), f"实际数据中不存在预期值为：{value} 的数据,实际数据为：{data}"
            elif isinstance(expected_value, list):
                for value in expected_value:
                    assert value in base_utils.get_all_value(data), f"实际数据中不存在预期值为：{value} 的数据,实际数据为：{data}"
            else:
                assert expected_value in base_utils.get_all_value(data), f"实际数据中不存在预期值为：{expected_value} 的数据,实际数据为：{data}"
        else:
            assert False, f"{type(data)}数据类型不支持,现只支持list,dict"

    @classmethod
    @allure.step("校验数据集中不存在预期值,预期值为:{2}")
    def assert_not_in_value(self, data,expected_value):
        """
        校验数据集中不存在预期值
        :param data: 响应数据
        :param expected_value: 预期值
        :return:
        """
        if isinstance(data,(list,dict)):
            if isinstance(expected_value, dict):
                for value in base_utils.get_all_value(expected_value):
                    assert value not in base_utils.get_all_value(data), f"实际数据中存在预期值为：{value} 的数据,实际数据为：{data}"
            elif isinstance(expected_value, list):
                for value in expected_value:
                    assert value not in base_utils.get_all_value(data), f"实际数据中存在预期值为：{value} 的数据,实际数据为：{data}"
            else:
                assert expected_value not in base_utils.get_all_value(data), f"实际数据中存在预期值为：{expected_value} 的数据,实际数据为：{data}"
        else:
            assert False,f"{type(data)}数据类型不支持,现只支持list,dict"

    @classmethod
    @allure.step("校验以预期值开头,预期值为:{2}")
    def assert_startswith(self, data,expected_value, msg=None):
        """
        校验以预期值开头
        :param data: 校验的data
        :param expected_value: 预期值
        :param msg: 预制消息
        :return:
        """
        if isinstance(data,str):
            assert data.startswith(expected_value),f"实际数据没有以：{expected_value} 开头, 实际数据为：{data}" if not msg else f"{msg},实际数据没有以：{expected_value} 开头, 实际数据为：{data}"
        else:
            assert False, "只支持 str 的校验,其余暂不支持"

    @classmethod
    @allure.step("校验以预期值结尾,预期值为:{2}")
    def assert_endswith(self, data,expected_value, msg=None):
        """
        校验以预期值结尾
        :param data: 校验的data
        :param expected_value: 预期值
        :param msg: 预制消息
        :return:
        """
        if isinstance(data,str):
            assert data.endswith(expected_value),f"实际数据没有以：{expected_value} 结尾, 实际数据为：{data}" if not msg else f"{msg},实际数据没有以：{expected_value} 结尾, 实际数据为：{data}"
        else:
            assert False, "只支持 str 的校验,其余暂不支持"

    @classmethod
    @allure.step("校验字典中存在预期key,预期值为:{2}")
    def assert_in_key(self, data,key, msg=None):
        """
        校验字典中存在预期key
        :param data: 响应数据
        :param key: 预期key值
        :param msg: 预制消息
        :return:
        """
        if isinstance(data,(list,dict)):
            assert key in base_utils.get_all_key(data), f"实际数据中未包含:{key}, 实际数据为：{data}" if not msg else f"{msg},实际数据中未包含:{key}, 实际数据为：{data}"
        else:
            assert False,f"{type(data)}数据类型不支持,现只支持list,dict"

    @classmethod
    @allure.step("校验字典中不存在预期key,预期值为:{2}")
    def assert_not_in_key(self, data,expected_key, msg=None):
        """
        验证check_value中不存在预期key
        :param data: 响应数据
        :param expected_key: 预期key
        :param msg: 预制消息
        :return:
        """
        if isinstance(data,(list,dict)):
            assert expected_key not in base_utils.get_all_key(data), f"实际数据中存在预期key为：{expected_key} 的数据, 实际数据为：{data}" if not msg else f"{msg}, 实际数据中存在预期key为：{expected_key} 的数据, 实际数据为：{data}"
        else:
            assert False,f"{type(data)}数据类型不支持,现只支持list,dict"

    @classmethod
    @allure.step("校验实际值:{1} 等于预期值:{2}")
    def assert_equal_value(self, reality_value, expected_value, msg=None):
        """
        校验等于预期值
        :param reality_value: 实际值
        :param expected_value: 预期值
        :param msg: 预制消息
        :return:
        """
        if isinstance(reality_value,type(expected_value)):
            assert expected_value == reality_value, f"断言失败, 实际值为:{reality_value}, 预期值为:{expected_value}" if not msg else f"{msg}, 实际值为:{reality_value}, 预期值为：{expected_value}"
        else:
            assert False, f"数据类型不匹配,实际值:{reality_value} 类型为:{type(reality_value)},预期值:{expected_value} 类型为:{type(expected_value)}"

    @classmethod
    @allure.step("校验字符串中包含指定字符串,预期值为:{2}")
    def assert_contains(self, original_value:str, contains_value:str, msg=None):
        """
        断言字符串中包含指定字符串
        :param original_value: 实际字符串
        :param contains_value: 预期字符串
        :param msg: 预制消息
        :return:
        """
        if isinstance(original_value, str) and isinstance(contains_value, str):
            assert contains_value in original_value, f"断言失败,实际数据中未包含 {contains_value} ,实际值为:{original_value}" if not msg else f"{msg},实际数据中未包含 {contains_value} ,实际值为:{original_value}"
        else:
            assert False, "只支持str类型"

    @classmethod
    @allure.step("断言字符串中不包含指定字符串,预期值为:{2}")
    def assert_not_contains(self, original_value, contains_value, msg=None):
        """
        断言字符串中不包含指定字符串
        :param original_value: 实际字符串
        :param contains_value: 预期字符串
        :param msg: 预制消息
        :return:
        """
        if isinstance(original_value, str) and isinstance(contains_value, str):
            assert contains_value not in original_value, f"断言失败,实际数据包含了 {contains_value}, 实际值为:{original_value}" if not msg else f"{msg},实际数据中未包含 {contains_value} ,实际值为:{original_value}"
        else:
            assert False, "只支持str类型"

    @classmethod
    @allure.step("校验等于预期值,预期值为:{2}")
    def assert_not_equal_value(self, reality_value, expected_value, msg=None):
        """
        校验不等于预期值
        :param reality_value: 实际值
        :param expected_value: 预期值
        :param msg: 预制消息
        :return:
        """
        assert expected_value != reality_value, f"断言失败,实际值等于预期值,实际值为:{reality_value}, 预期值为:{expected_value}" if not msg else f"{msg},实际值等于预期值,实际值为:{reality_value}, 预期值为:{expected_value}"

    @classmethod
    @allure.step("校验是否等于None")
    def assert_isNone(self, reality_value, msg=None):
        """
        校验是否等于None
        :param reality_value: 实际值
        :param msg: 预制消息
        :return:
        """
        if reality_value is None:
            assert True
        else:
            assert False, f"断言失败,{reality_value} 不等于None" if not msg else f"{msg},校验值:{reality_value} 不等于None"

    @classmethod
    @allure.step("校验为空")
    def assert_isEmpty(self, reality_value, msg=None):
        """
        校验值为空,当传入值为None、False、空字符串""、0、空列表[]、空字典{}、空元组()都会判定为空
        :param reality_value: 实际值
        :param msg: 预制消息
        :return:
        """
        if not reality_value:
            assert True
        else:
            assert False, f"校验值不为空,值为:{reality_value}" if not msg else f"{msg},校验值为:{reality_value}"

    @classmethod
    @allure.step("校验不为空")
    def assert_isNotEmpty(self, reality_value, msg=None):
        """
        校验值不为空,当传入值为None、False、空字符串""、0、空列表[]、空字典{}、空元组()都会判定为空
        :param reality_value: 实际值
        :param msg: 预制消息
        :return:
        """
        if reality_value:
            assert True
        else:
            assert False, f"校验值为空,值为:{reality_value}" if not msg else f"{msg},校验值为:{reality_value}"

    @classmethod
    @allure.step("校验时间小于预期,实际值为:{2},预期值为:{3}")
    def assert_time(self, reality_time, expected_time):
        """
        校验时间小于预期
        :param reality_time: 响应的data
        :param expected_time: 预期值为
        :return:
        """
        if reality_time <= expected_time:
            assert True
        else:
            assert False, f"实际时间大于预期时间,实际值为:{reality_time}, 预期值为:{expected_time}"

    @classmethod
    @allure.step("校验字典或列表是否相等,实际值为:{1},预期值为:{2}")
    def assert_dictOrList_eq(self,reality, expected):
        """
        校验字典或列表是否相等
        :param reality: 实际字典或列表
        :param expected: 预期字典或列表
        :return:
        """
        if isinstance(reality, dict) and isinstance(expected, dict):
            if operator.eq(reality,expected):
                assert True
            else:
                assert False,"二个字典不相等"
        elif isinstance(reality, list) and isinstance(expected, list):
            if list(set(reality).difference(set(expected))) == [] and list(set(expected).difference(set(reality))) == []:
                assert True
            else:
                assert False, "二个列表不相等"
        else:
            assert False, "传入的数据不是字典或列表"

    @classmethod
    @allure.step("校验列表中是否有重复项")
    def assert_list_repetition(self, lists):
        """
        校验列表中是否有重复项
        :param lists: 列表
        :return:
        """
        if isinstance(lists,list):
            repetition = {key: value for key, value in dict(Counter(lists)).items() if value > 1}
            if repetition:
                assert False, f"列表中有重复项,重复项为：{repetition}"
        else:
            assert False, "传入的数据不是一个list"

if __name__ == "__main__":
    dict1 = {"projId":113692,"ppid":130817,"projName":"BW接口用工程-勿删160711"}
    dict2 = {"projId":113692,"projName":"BW接口用工程-勿删160711","ppid":130817}
    dict3 = {"hu":[1111,"adf","胡彪"]}
    dict4 = {"name":"hubiao","chengji":[10,20,30],"proj":[{"projname":"项目部工程"},{"projsize":1024},{"poe":[{"hu":"adf"}]}]}
    dict5 = {"hu":"adf"}
    dict6 = {"hu":[]}
    dict7 = {"hu":""}
    dict8 = {"hu":["胡彪"]}
    dict9 = {"hu":50}
    dict10 = {"hu":1.32}
    list1 = [1111,"adfaf","胡彪",False,None]
    list2 = [1111,"胡彪","adfaf"]
    list3 = ["89010001#89","89010001#89","89010001#89", "96003010#96"]
    list4 = [{"name":"hubiao"},{"name":"mongnet"},{"chengji":[10,20,30]},{"proj":[{"projname":"项目部工程"},{"projsize":1024},{"poe":[{"hu":"adf"}]}]}]
    list5 = [["89010001#89","89010001#89","89010001#89", "96003010#96"],{"name":"mongnet"},{"chengji":[10,20,30]},{"proj":[{"projname":"项目部工程"},{"projsize":1024},{"poe":[{"hu":"adf"}]}]}]
    str0 = "http://lkjt.lubansoft.net:8086/main/schedule/list"
    str1 = "http://lkjt.lubansoft.net:8086"
    str2 = "大佬"
    data = ['WBS数据-质检','WEB质检-标段基本信息', 'w' ]
    expected_value = ['WEB质检-标段基本信息', 'WBS数据-质检']
    # Assertions.assert_dictOrList_eq(dict1,dict2)
    # Assertions.assert_dictOrList_eq(list1,list2)
    # Assertions.assert_assign_attribute_value(dict3, "hu", ["adf",1111, "胡彪"])
    # Assertions.assert_assign_attribute_value(dict5, "hu", ["adf",1111, "胡彪"])
    # Assertions.assert_assign_attribute_value(dict3, "hu", "adf")
    # Assertions.assert_assign_attribute_value(dict6, "hu", [])
    # Assertions.assert_assign_attribute_value(dict7, "hu", "")
    # Assertions.assert_assign_attribute_value(dict8, "hu", "胡彪")
    # Assertions.assert_assign_attribute_value(dict9, "hu", 50)
    # Assertions.assert_assign_attribute_value(dict10, "hu", 1.32)
    # Assertions.assert_assign_attribute_value(dict10, "hu", 1.32)
    Assertions.assert_contains("http://lkjt.lubansoft.net:8086/main/schedule/list","http://lkjt.lubansoft.net:8086")
    # Assertions.assert_not_contains(str0,str2)
    # Assertions.assert_list_repetition(list3)
    # Assertions.assert_in_value(data,expected_value)
    # in_value 和 in_key 等要支持list和dict,现在只部分支持
    # Assertions.assert_in_key(list4, "hu")
    # Assertions.assert_not_in_key(list4, "hdu")
    # Assertions.assert_not_in_value(list1, "null")
    # None、False、空字符串""、0、空列表[]、空字典{}、空元组()


