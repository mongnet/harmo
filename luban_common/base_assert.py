#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2019/4/3 15:12
# @Author  : hubiao
# @File    : base_assert.py
import operator
from collections import Counter
import allure
from luban_common import base_utils, extract

class Assertions:
    """
    公共断言方法
    """
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
    def assert_assign_attribute_value(self, data,key,expect_value):
        """
        校验数据集中指定key的值是否等于预期值
        :param data:校验的data
        :param key:预期key
        :param expect_value:预期值
        :return:
        """
        if isinstance(data[key], list) and isinstance(expect_value,list):
            if data[key] != expect_value:
                assert False, f"预期值不等于实际值,实际值为:{data[key]}, 预期值为:{expected_value}"
        elif isinstance(data[key], (str,int,float)):
            assert data[key] == expect_value, f"预期值不等于实际值,实际值为:{data[key]}, 预期值为:{expect_value}"
        else:
            assert False, f"当前传入的实际值类型为{type(data[key])},预期值类型为{type(expect_value)}, 现只支持list,str,int,float的校验, 其余暂不支持"

    @classmethod
    @allure.step("校验数据集中存在预期值,预期值为:{2}")
    def assert_in_value(self, actual_value,expect_value):
        """
        校验数据集中存在预期值
        :param actual_value: 校验的actual_value
        :param expect_value:预期值
        :return:
        """
        if isinstance(actual_value,(list,dict)):
            if isinstance(expect_value, dict):
                for value in base_utils.get_all_value(expect_value):
                    assert value in base_utils.get_all_value(actual_value), f"实际数据中不存在预期值为：{value} 的数据,实际数据为：{actual_value}"
            elif isinstance(expect_value, list):
                for value in expect_value:
                    assert value in base_utils.get_all_value(actual_value), f"实际数据中不存在预期值为：{value} 的数据,实际数据为：{actual_value}"
            else:
                assert expect_value in base_utils.get_all_value(actual_value), f"实际数据中不存在预期值为：{expect_value} 的数据,实际数据为：{actual_value}"
        else:
            assert False, f"{type(actual_value)}数据类型不支持,现只支持list,dict"

    @classmethod
    @allure.step("校验数据集中不存在预期值,预期值为:{2}")
    def assert_not_in_value(self, actual_value,expect_value):
        """
        校验数据集中不存在预期值
        :param actual_value: 响应数据
        :param expect_value: 预期值
        :return:
        """
        if isinstance(actual_value,(list,dict)):
            if isinstance(expect_value, dict):
                for value in base_utils.get_all_value(expect_value):
                    assert value not in base_utils.get_all_value(actual_value), f"实际数据中存在预期值为：{value} 的数据,实际数据为：{actual_value}"
            elif isinstance(expect_value, list):
                for value in expect_value:
                    assert value not in base_utils.get_all_value(actual_value), f"实际数据中存在预期值为：{value} 的数据,实际数据为：{actual_value}"
            else:
                assert expect_value not in base_utils.get_all_value(actual_value), f"实际数据中存在预期值为：{expect_value} 的数据,实际数据为：{actual_value}"
        else:
            assert False,f"{type(actual_value)}数据类型不支持,现只支持list,dict"

    @classmethod
    @allure.step("校验以预期值开头,预期值为:{2}")
    def assert_startswith(self, actual_value,expect_value, msg=None):
        """
        校验以预期值开头
        :param actual_value: 校验的actual_value
        :param expect_value: 预期值
        :param msg: 预制消息
        :return:
        """
        if isinstance(actual_value,str):
            assert actual_value.startswith(expect_value),f"实际数据没有以：{expect_value} 开头, 实际数据为：{actual_value}" if not msg else f"{msg},实际数据没有以：{expect_value} 开头, 实际数据为：{actual_value}"
        else:
            assert False, "只支持 str 的校验,其余暂不支持"

    @classmethod
    @allure.step("校验以预期值结尾,预期值为:{2}")
    def assert_endswith(self, actual_value,expect_value, msg=None):
        """
        校验以预期值结尾
        :param actual_value: 校验的actual_value
        :param expect_value: 预期值
        :param msg: 预制消息
        :return:
        """
        if isinstance(actual_value,str):
            assert actual_value.endswith(expect_value),f"实际数据没有以：{expect_value} 结尾, 实际数据为：{actual_value}" if not msg else f"{msg},实际数据没有以：{expect_value} 结尾, 实际数据为：{actual_value}"
        else:
            assert False, "只支持 str 的校验,其余暂不支持"

    @classmethod
    @allure.step("校验字典中存在预期key,预期值为:{2}")
    def assert_in_key(self, actual_value,key, msg=None):
        """
        校验字典中存在预期key
        :param actual_value: 响应数据
        :param key: 预期key值
        :param msg: 预制消息
        :return:
        """
        if isinstance(actual_value,(list,dict)):
            assert key in base_utils.get_all_key(actual_value), f"实际数据中未包含:{key}, 实际数据为：{actual_value}" if not msg else f"{msg},实际数据中未包含:{key}, 实际数据为：{actual_value}"
        else:
            assert False,f"{type(actual_value)}数据类型不支持,现只支持list,dict"

    @classmethod
    @allure.step("校验字典中不存在预期key,预期值为:{2}")
    def assert_not_in_key(self, actual_value,expected_key, msg=None):
        """
        验证check_value中不存在预期key
        :param actual_value: 响应数据
        :param expected_key: 预期key
        :param msg: 预制消息
        :return:
        """
        if isinstance(actual_value,(list,dict)):
            assert expected_key not in base_utils.get_all_key(actual_value), f"实际数据中存在预期key为：{expected_key} 的数据, 实际数据为：{actual_value}" if not msg else f"{msg}, 实际数据中存在预期key为：{expected_key} 的数据, 实际数据为：{actual_value}"
        else:
            assert False,f"{type(actual_value)}数据类型不支持,现只支持list,dict"

    @classmethod
    @allure.step("校验实际值:{1} 等于预期值:{2}")
    def assert_equal_value(self, actual_value, expect_value, msg=None):
        """
        校验等于预期值
        :param actual_value: 实际值
        :param expect_value: 预期值
        :param msg: 预制消息
        :return:
        """
        if isinstance(actual_value,type(expect_value)):
            assert actual_value == expect_value, f"断言失败, 实际值为:{actual_value}, 预期值为:{expect_value}" if not msg else f"{msg}, 实际值为:{actual_value}, 预期值为：{expect_value}"
        else:
            assert False, f"数据类型不匹配,实际值:{actual_value} 类型为:{type(actual_value)},预期值:{expect_value} 类型为:{type(expect_value)}"

    @classmethod
    @allure.step("校验字符串中包含指定字符串,预期值为:{2}")
    def assert_contains(self, actual_value:str, contains_value:str, msg=None):
        """
        断言字符串中包含指定字符串
        :param actual_value: 实际字符串
        :param contains_value: 预期字符串
        :param msg: 预制消息
        :return:
        """
        if isinstance(actual_value, str) and isinstance(contains_value, str):
            assert contains_value in actual_value, f"断言失败,实际数据中未包含 {contains_value} ,实际值为:{actual_value}" if not msg else f"{msg},实际数据中未包含 {contains_value} ,实际值为:{actual_value}"
        else:
            assert False, "只支持str类型"

    @classmethod
    @allure.step("断言字符串中不包含指定字符串,预期值为:{2}")
    def assert_not_contains(self, actual_value, contains_value, msg=None):
        """
        断言字符串中不包含指定字符串
        :param actual_value: 实际字符串
        :param contains_value: 预期字符串
        :param msg: 预制消息
        :return:
        """
        if isinstance(actual_value, str) and isinstance(contains_value, str):
            assert contains_value not in actual_value, f"断言失败,实际数据包含了 {contains_value}, 实际值为:{actual_value}" if not msg else f"{msg},实际数据中未包含 {contains_value} ,实际值为:{actual_value}"
        else:
            assert False, "只支持str类型"

    @classmethod
    @allure.step("校验等于预期值,预期值为:{2}")
    def assert_not_equal_value(self, actual_value, expect_value, msg=None):
        """
        校验不等于预期值
        :param actual_value: 实际值
        :param expect_value: 预期值
        :param msg: 预制消息
        :return:
        """
        assert actual_value != expect_value, f"断言失败,实际值等于预期值,实际值为:{actual_value}, 预期值为:{expect_value}" if not msg else f"{msg},实际值等于预期值,实际值为:{actual_value}, 预期值为:{expect_value}"

    @classmethod
    @allure.step("校验是否等于None")
    def assert_isNone(self, actual_value, msg=None):
        """
        校验是否等于None
        :param actual_value: 实际值
        :param msg: 预制消息
        :return:
        """
        if actual_value is None:
            assert True
        else:
            assert False, f"断言失败,{actual_value} 不等于None" if not msg else f"{msg},校验值:{actual_value} 不等于None"

    @classmethod
    @allure.step("校验为空")
    def assert_isEmpty(self, actual_value, msg=None):
        """
        校验值为空,当传入值为None、False、空字符串""、0、空列表[]、空字典{}、空元组()都会判定为空
        :param actual_value: 实际值
        :param msg: 预制消息
        :return:
        """
        if not actual_value:
            assert True
        else:
            assert False, f"校验值不为空,值为:{actual_value}" if not msg else f"{msg},校验值为:{actual_value}"

    @classmethod
    @allure.step("校验不为空")
    def assert_isNotEmpty(self, actual_value, msg=None):
        """
        校验值不为空,当传入值为None、False、空字符串""、0、空列表[]、空字典{}、空元组()都会判定为空
        :param actual_value: 实际值
        :param msg: 预制消息
        :return:
        """
        if actual_value:
            assert True
        else:
            assert False, f"校验值为空,值为:{actual_value}" if not msg else f"{msg},校验值为:{actual_value}"

    @classmethod
    @allure.step("校验时间小于预期,实际值为:{2},预期值为:{3}")
    def assert_time(self, actual_value, expect_value):
        """
        校验时间小于预期
        :param actual_value: 实际时间
        :param expect_value: 预期时间
        :return:
        """
        if actual_value <= expect_value:
            assert True
        else:
            assert False, f"实际时间大于预期时间,实际值为:{actual_value}, 预期值为:{expect_value}"

    @classmethod
    @allure.step("校验字典或列表是否相等,实际值为:{1},预期值为:{2}")
    def assert_dictOrList_eq(self,actual_value, expect_value):
        """
        校验字典或列表是否相等
        :param actual_value: 实际字典或列表
        :param expect_value: 预期字典或列表
        :return:
        """
        if isinstance(actual_value, dict) and isinstance(expect_value, dict):
            if operator.eq(actual_value,expect_value):
                assert True
            else:
                assert False,"二个字典不相等"
        elif isinstance(actual_value, list) and isinstance(expect_value, list):
            ls1 = list(set(actual_value).difference(set(expect_value)))
            ls2 = list(set(expect_value).difference(set(actual_value)))
            if not ls1 and not ls2:
                assert True
            else:
                if ls1 and ls2:
                    assert False, f"二个列表不相等,第一个列表比第二个列表多了：{ls1},第二个列表比第一个列表多了：{ls2}"
                elif ls1:
                    assert False, f"二个列表不相等,第一个列表比第二个列表多了：{ls1}"
                elif ls2:
                    assert False, f"二个列表不相等,第二个列表比第一个列表多了：{ls2}"
                else:
                    assert False, "列表对比失败，出现未预期的异常"
        else:
            assert False, "传入的数据不是字典或列表"

    @classmethod
    @allure.step("校验列表中是否有重复项")
    def assert_list_repetition(self, actual_value: list):
        """
        校验列表中是否有重复项
        :param actual_value: 列表
        :return:
        """
        if isinstance(actual_value,list):
            repetition = {key: value for key, value in dict(Counter(actual_value)).items() if value > 1}
            if repetition:
                assert False, f"列表中有重复项,重复项为：{repetition}"
        else:
            assert False, "传入的数据不是一个list"

    @classmethod
    @allure.step("集合校验")
    def validate_response(self, response, validate_list: list) -> None:
        """
        校验结果
        :param response:
        :param validate_list:
        :return:
        """
        if not response.get("response_obj") and not hasattr(response.get("response_obj"),"headers"):
            raise ValueError("response 中未包含 response 对象")
        for check in validate_list:
            for check_type, check_value in check.items():
                if len(check_value) > 1:
                    actual_value = extract.extract_by_object(response.get("response_obj"), check_value[0])  # 实际结果
                    expect_value = check_value[1]  # 期望结果
                    if check_type in ["assert_code", "code"]:
                        Assertions.assert_code(response,actual_value, expect_value)
                    elif check_type in ["assert_equal_value", "equal", "equals"]:
                        Assertions.assert_equal_value(actual_value, expect_value)
                    elif check_type in ["assert_not_equal_value"]:
                        Assertions.assert_not_equal_value(actual_value, expect_value)
                    elif check_type in ["assert_assign_attribute_value"]:
                        Assertions.assert_assign_attribute_value(response, actual_value, expect_value)
                    elif check_type in ["assert_in_value", "in"]:
                        Assertions.assert_in_value(actual_value, expect_value)
                    elif check_type in ["assert_not_in_value", "in"]:
                        Assertions.assert_not_in_value(actual_value, expect_value)
                    elif check_type in ["assert_startswith"]:
                        Assertions.assert_startswith(actual_value, expect_value)
                    elif check_type in ["assert_endswith"]:
                        Assertions.assert_endswith(actual_value, expect_value)
                    elif check_type in ["assert_in_key"]:
                        Assertions.assert_in_key(actual_value, expect_value)
                    elif check_type in ["assert_not_in_key"]:
                        Assertions.assert_not_in_key(actual_value, expect_value)
                    elif check_type in ["assert_contains"]:
                        Assertions.assert_contains(actual_value, expect_value)
                    elif check_type in ["assert_not_contains"]:
                        Assertions.assert_not_contains(actual_value, expect_value)
                    elif check_type in ["assert_time"]:
                        Assertions.assert_time(actual_value, expect_value)
                    elif check_type in ["assert_dictOrList_eq"]:
                        Assertions.assert_dictOrList_eq(actual_value, expect_value)
                    else:
                        if hasattr(Assertions, check_type):
                            getattr(Assertions, check_type)(actual_value, expect_value)
                        else:
                            print(f'{check_type} not valid check type')
                else:
                    actual_value = extract.extract_by_object(response.get("response_obj"), check_value[0])  # 实际结果
                    if check_type in ["assert_isEmpty"]:
                        Assertions.assert_isEmpty(actual_value)
                    elif check_type in ["assert_isNotEmpty"]:
                        Assertions.assert_isNotEmpty(actual_value)
                    elif check_type in ["assert_isNone"]:
                        Assertions.assert_isNone(actual_value)
                    elif check_type in ["assert_list_repetition"]:
                        Assertions.assert_list_repetition(actual_value)
                    else:
                        if hasattr(Assertions, check_type):
                            getattr(Assertions, check_type)(actual_value)
                        else:
                            print(f'{check_type} not valid check type')

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
    list1 = [1111,"adfaf","公众号：彪哥的测试之路",False,None]
    list2 = [1111,"公众号：彪哥的测试之路","adfaf"]
    list3 = ["89010001#89","89010001#89","89010001#89", "96003010#96"]
    list4 = [{"name":"hubiao"},{"name":"mongnet"},{"chengji":[10,20,30]},{"proj":[{"projname":"项目部工程"},{"projsize":1024},{"poe":[{"hu":"adf"}]}]}]
    list5 = [["89010001#89","89010001#89","89010001#89", "96003010#96"],{"name":"mongnet"},{"chengji":[10,20,30]},{"proj":[{"projname":"项目部工程"},{"projsize":1024},{"poe":[{"hu":"adf"}]}]}]
    str0 = "http://lkjt.lubansoft.net:8086/main/schedule/list"
    str1 = "http://lkjt.lubansoft.net:8086"
    str2 = "大佬"
    data = ['WBS数据-质检','WEB质检-标段基本信息', 'w' ]
    expected_value = ['WEB质检-标段基本信息', 'WBS数据-质检']
    Assertions.assert_equal_value('自动化测试企业','初始化分公司')
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
    # Assertions.assert_contains("http://lkjt.lubansoft.net:8086/main/schedule/list","http://lkjt.lubansoft.net:8086")
    # Assertions.assert_not_contains(str0,str2)
    # Assertions.assert_list_repetition(list3)
    # Assertions.assert_in_value(data,expected_value)
    # in_value 和 in_key 等要支持list和dict,现在只部分支持
    # Assertions.assert_in_key(list4, "hu")
    # Assertions.assert_not_in_key(list4, "hdu")
    # Assertions.assert_not_in_value(list1, "null")
    Assertions.assert_time("1494325882000", "1662432740000")
    # None、False、空字符串""、0、空列表[]、空字典{}、空元组()


