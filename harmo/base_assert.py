#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2019/4/3 15:12
# @Author  : hubiao
# @File    : base_assert.py
import operator
from collections import Counter
import allure
from harmo import base_utils, extract
from jsonschema import validate

class Assertions:
    """
    公共断言方法
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Assertions,cls).__new__(cls)
        return cls._instance

    @classmethod
    @allure.step("校验status_code和code")
    def assert_all_code(self, response, expected_http_code, expected_code):
        """
        即将废弃，建议使用 assert_code
        校验status_code和code状态码
        :param response: 响应数据
        :param expected_http_code: 预期的http状态码
        :param expected_code: 预期code状态码
        :return:
        """
        assert response.get("status_code") == expected_http_code, f'''校验失败,实际http_code为:{response.get("status_code")},预期http_code为:{response.get("status_code")}

        请求URL:{response.get("request_url")}
        请求Method:{response.get("request_method")}
        请求Headers:{response.get("request_header")}
        请求Params:{response.get("request_params")}
        请求Payload:{response.get("request_payload")}
        响应status_code:{response.get("status_code")}
        响应信息:{response.get("Response_text") if response.get("source_response") is None else response.get("source_response")}'''

        assert response.get("code")[0] == expected_code, f'''校验失败,实际code为:{response.get("code")[0]},预期code为:{response.get("code")[0]}

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
                assert False, f"预期值不等于实际值,实际值为:{data[key]}, 预期值为:{expect_value}"
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
    @allure.step("校验为空（None、False、空字符串""、0、空列表[]、空字典{}、空元组()都会判定为空）")
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
    @allure.step("校验不为空（None、False、空字符串""、0、空列表[]、空字典{}、空元组()都会判定为空）")
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
    @allure.step("schema检查")
    def assert_schema(self, schema, response):
        """
        schema检查
        :param schema: 要验证的 json schema 数据
        :param response: 要验证的 json 数据
        :return:
        """
        validate(instance=response, schema=schema)

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
    # expected_value = ['WEB质检-标段基本信息', 'WBS数据-质检']
    # Assertions.assert_equal_value('自动化测试企业','初始化分公司')
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
    # Assertions.assert_time("1494325882000", "1662432740000")
    # None、False、空字符串""、0、空列表[]、空字典{}、空元组()
    rs = {"code":200,"msg":"Success","success":True,"data":{"sysMenuTypes":[{"id":"1713851790359179268","name":"供应商管理","type":"menu","parentId":"10000000","orderNum":3,"url":"/builder/supplierManagement","component":None,"icon":"供应商管理","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179271","name":"项目管理","type":"menu","parentId":"10000000","orderNum":4,"url":"/builder/projectManagement","component":None,"icon":"项目管理","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179266","name":"职务管理","type":"menu","parentId":"10000000","orderNum":6,"url":"/builder/positionManagement","component":None,"icon":"职务管理","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179269","name":"企业人员","type":"menu","parentId":"10000000","orderNum":7,"url":"/builder/enterprise","component":None,"icon":"企业人员","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179273","name":"应用配置","type":"dir","parentId":"10000000","orderNum":21,"url":"/builder-setting-web","component":None,"icon":"应用配置","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1713851790359179276","name":"进度报警","type":"menu","parentId":"1713851790359179274","orderNum":9,"url":"/main/baseSettings/entWarnRule","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/plan/"},{"id":"1713851790359179275","name":"日历模板","type":"menu","parentId":"1713851790359179274","orderNum":8,"url":"/main/baseSettings/entCalendarTemplate","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/plan/"},{"id":"1713851790359179278","name":"安全管理","type":"dir","parentId":"1713851790359179273","orderNum":11,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1782612929997176833","name":"删除","type":"btn","parentId":"1713851790359179267","orderNum":2,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1713851790359179284","name":"数据字典","type":"menu","parentId":"10000000","orderNum":20,"url":"/builder/data-dictionary","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179282","name":"流程模板","type":"menu","parentId":"10000000","orderNum":19,"url":"/builder/flow-template","component":None,"icon":"流程模板","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179270","name":"从业人员","type":"menu","parentId":"10000000","orderNum":8,"url":"/builder/personnel","component":None,"icon":"从业人员","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179272","name":"角色管理","type":"menu","parentId":"10000000","orderNum":5,"url":"/builder/role","component":None,"icon":"角色管理","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1783326061879099392","name":"操作","type":"btn","parentId":"1713851790359179272","orderNum":5,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1783326061883293696","name":"授权","type":"btn","parentId":"1713851790359179272","orderNum":5,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1713851790359179277","name":"项目进展节点配置","type":"menu","parentId":"1713851790359179274","orderNum":10,"url":"/main/baseSettings/progressNode","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/plan/"},{"id":"1723997045709606934","name":"属性模板","type":"menu","parentId":"1713851790359179273","orderNum":18,"url":"/builder/attributeTemplate","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1714451949827661842","name":"行为积分库","type":"menu","parentId":"1713851790359179278","orderNum":15,"url":"/baseSetting/actionPointsLib/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1713851790359179280","name":"安全风险库","type":"menu","parentId":"1713851790359179278","orderNum":12,"url":"/baseSetting/safetyRisk/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1713851790359179281","name":"考试题库","type":"menu","parentId":"1713851790359179278","orderNum":13,"url":"/baseSetting/questionsBank/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1726905695791513617","name":"防护用品库","type":"menu","parentId":"1713851790359179278","orderNum":14,"url":"/baseSetting/materialWarehouse/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1722440040501309488","name":"物联配置","type":"menu","parentId":"1713851790359179273","orderNum":26,"url":"/builder/iotConfig","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1722440040501309461","name":"质量检查库","type":"menu","parentId":"1722440040501309460","orderNum":17,"url":"/baseSetting/checkLibrary/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1713851790359179267","name":"组织结构","type":"menu","parentId":"10000000","orderNum":2,"url":"/builder/companyprofile","component":None,"icon":"组织管理","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1782612929992982528","name":"修改","type":"btn","parentId":"1713851790359179267","orderNum":2,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1782612929997176832","name":"新增","type":"btn","parentId":"1713851790359179267","orderNum":2,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1782327411560415234","name":"删除","type":"btn","parentId":"1713851790359179272","orderNum":5,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1713851790359179274","name":"进度管理","type":"dir","parentId":"1713851790359179273","orderNum":8,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714451949827661843","name":"安全评分","type":"menu","parentId":"1713851790359179278","orderNum":16,"url":"/baseSetting/securityScore/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1713851790359179279","name":"安全检查库","type":"menu","parentId":"1713851790359179278","orderNum":11,"url":"/baseSetting/checkLibrary/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1722440040501309460","name":"质量管理","type":"dir","parentId":"1713851790359179273","orderNum":17,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591856","name":"安全管理","type":"dir","parentId":"10000001","orderNum":39,"url":"/sphere-safety-web","component":None,"icon":"安全管理","path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1714256290457591866","name":"整改记录","type":"menu","parentId":"1714256290457591863","orderNum":45,"url":"/inspect/rectification/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591865","name":"巡检任务","type":"menu","parentId":"1714256290457591863","orderNum":44,"url":"/inspect/patrolTask/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591869","name":"岗前教育","type":"menu","parentId":"1714256290457591868","orderNum":47,"url":"/safetyActivity/preEducation","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591844","name":"隐患排查","type":"menu","parentId":"1714256290457591843","orderNum":31,"url":"/inspect/hiddenDangerCheck/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591893","name":"防护用品","type":"menu","parentId":"1714256290457591892","orderNum":65,"url":"/occupationHealth/protectiveArticle/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591894","name":"健康检查","type":"menu","parentId":"1714256290457591892","orderNum":66,"url":"/occupationHealth/HealthCheck/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591881","name":"安全活动","type":"dir","parentId":"1714256290457591856","orderNum":57,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591884","name":"专项活动","type":"menu","parentId":"1714256290457591881","orderNum":59,"url":"/safetyActivity/specialTraining","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591883","name":"安全会议","type":"menu","parentId":"1714256290457591881","orderNum":58,"url":"/safetyActivity/safetyConference","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591882","name":"安全交底","type":"menu","parentId":"1714256290457591881","orderNum":57,"url":"/technicExplain/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591889","name":"目标管理","type":"dir","parentId":"1714256290457591856","orderNum":39,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1719605864688582738","name":"目标责任书","type":"menu","parentId":"1714256290457591889","orderNum":63,"url":"/goalManagement/dutyConclusion/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1719605864688582739","name":"目标考核","type":"menu","parentId":"1714256290457591889","orderNum":64,"url":"/goalManagement/dutyAssessment/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591895","name":"基础设置","type":"dir","parentId":"1714256290457591856","orderNum":68,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591896","name":"安全检查库","type":"menu","parentId":"1714256290457591895","orderNum":68,"url":"/baseSetting/checkLibrary/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591898","name":"考试题库","type":"menu","parentId":"1714256290457591895","orderNum":70,"url":"/baseSetting/questionsBank/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591897","name":"行为积分库","type":"menu","parentId":"1714256290457591895","orderNum":69,"url":"/baseSetting/actionPointsLib/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591902","name":"编号规则","type":"menu","parentId":"1714256290457591895","orderNum":74,"url":"/baseSetting/codeRule/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591900","name":"安全评分","type":"menu","parentId":"1714256290457591895","orderNum":72,"url":"/baseSetting/securityScore/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591899","name":"防护用品库","type":"menu","parentId":"1714256290457591895","orderNum":71,"url":"/baseSetting/materialWarehouse/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591860","name":"岗位职责","type":"menu","parentId":"1714256290457591857","orderNum":41,"url":"/system/duty/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591858","name":"管理制度","type":"menu","parentId":"1714256290457591857","orderNum":39,"url":"/system/manageRegime/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591859","name":"组织机构","type":"menu","parentId":"1714256290457591857","orderNum":40,"url":"/system/orginationStructure","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1719259302770151525","name":"安全报告","type":"menu","parentId":"1714256290457591856","orderNum":67,"url":"/report/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591892","name":"职业健康","type":"dir","parentId":"1714256290457591856","orderNum":63,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591885","name":"安全经费","type":"menu","parentId":"1714256290457591856","orderNum":64,"url":"/securityFunding","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591901","name":"安全风险库","type":"menu","parentId":"1714256290457591895","orderNum":73,"url":"/baseSetting/safetyRisk/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591857","name":"安保体系","type":"dir","parentId":"1714256290457591856","orderNum":40,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591877","name":"应急管理","type":"dir","parentId":"1714256290457591856","orderNum":65,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591879","name":"应急演练","type":"menu","parentId":"1714256290457591877","orderNum":55,"url":"/contingencyManagement/emergencyDrills","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591878","name":"应急预案","type":"menu","parentId":"1714256290457591877","orderNum":54,"url":"/emergencyManagement/emergencyPlan","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591880","name":"应急资源","type":"menu","parentId":"1714256290457591877","orderNum":56,"url":"/emergencyManagement/emergencySupplies","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591886","name":"事故管理","type":"menu","parentId":"1714256290457591856","orderNum":66,"url":"/accidentManage","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591876","name":"危大工程","type":"menu","parentId":"1714256290457591856","orderNum":53,"url":"/riskProject","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591861","name":"设备管理","type":"dir","parentId":"1714256290457591856","orderNum":42,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591862","name":"设备信息","type":"menu","parentId":"1714256290457591861","orderNum":42,"url":"/equipmentManagement/deviceInfo","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591873","name":"安全风险","type":"dir","parentId":"1714256290457591856","orderNum":51,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591874","name":"辨识评估","type":"menu","parentId":"1714256290457591873","orderNum":51,"url":"/dangerManage/dangerAssess","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591875","name":"分级管控","type":"menu","parentId":"1714256290457591873","orderNum":52,"url":"/dangerManage/dangerManage","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591887","name":"临电管理","type":"dir","parentId":"1714256290457591856","orderNum":62,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591888","name":"配电箱","type":"menu","parentId":"1714256290457591887","orderNum":62,"url":"/electricManage/electricBox","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591868","name":"安全教育","type":"dir","parentId":"1714256290457591856","orderNum":43,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591872","name":"安全考核","type":"menu","parentId":"1714256290457591868","orderNum":50,"url":"/safetyActivity/score","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591871","name":"安全培训","type":"menu","parentId":"1714256290457591868","orderNum":49,"url":"/safetyActivity/safetyTrain","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591838","name":"质保体系","type":"dir","parentId":"1714256290457591837","orderNum":27,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591870","name":"教育考试","type":"menu","parentId":"1714256290457591868","orderNum":48,"url":"/safetyActivity/exam","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786125","name":"进度管理","type":"dir","parentId":"10000001","orderNum":80,"url":"/plan-manager-web","component":None,"icon":"进度管理","path":None,"pathId":None,"isLink":None,"redirect":"/plan/"},{"id":"1714256290461786126","name":"进度计划","type":"menu","parentId":"1714256290461786125","orderNum":80,"url":"/main/schedule/list","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786127","name":"实际进度","type":"menu","parentId":"1714256290461786125","orderNum":81,"url":"/main/actual/list","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786135","name":"基础设置","type":"dir","parentId":"1714256290461786125","orderNum":87,"url":"/#","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786136","name":"日历模板","type":"menu","parentId":"1714256290461786135","orderNum":87,"url":"/main/baseSettings/calendarTemplate","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786137","name":"进度报警","type":"menu","parentId":"1714256290461786135","orderNum":88,"url":"/main/baseSettings/warnRule","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1716687262993223720","name":"BIM沙盘","type":"menu","parentId":"1714256290461786125","orderNum":84,"url":"/main/sandbox","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786132","name":"进度报告","type":"dir","parentId":"1714256290461786125","orderNum":85,"url":"/#","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786134","name":"项目进展月报","type":"menu","parentId":"1714256290461786132","orderNum":86,"url":"/main/report/monthProgress","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786133","name":"投资进度月报","type":"menu","parentId":"1714256290461786132","orderNum":85,"url":"/main/report/monthInvest","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591840","name":"组织机构","type":"menu","parentId":"1714256290457591838","orderNum":28,"url":"/system/orginationStructure","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591841","name":"岗位职责","type":"menu","parentId":"1714256290457591838","orderNum":29,"url":"/system/duty/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457690000","name":"责任书","type":"menu","parentId":"1714256290457591838","orderNum":30,"url":"/system/responsibilityLetter/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591839","name":"管理制度","type":"menu","parentId":"1714256290457591838","orderNum":27,"url":"/system/manageRegime/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780769265700306944","name":"流程表单管理","type":"menu","parentId":"1714256290457591848","orderNum":38,"url":"/configuration/formFlowConfig","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/basic-data/"},{"id":"1714256290461786117","name":"BIM管理","type":"dir","parentId":"10000001","orderNum":23,"url":"/bim-web","component":None,"icon":"BIM管理","path":None,"pathId":None,"isLink":None,"redirect":"/bim/"},{"id":"1714256290461786130","name":"整改记录","type":"menu","parentId":"1714256290461786128","orderNum":83,"url":"/main/progressTrack/rectificationRecord","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786129","name":"进度报警","type":"menu","parentId":"1714256290461786128","orderNum":82,"url":"/main/progressTrack/warnList","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591837","name":"质量管理","type":"dir","parentId":"10000001","orderNum":27,"url":"/sphere-quality-web","component":None,"icon":"质量管理","path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1720716936518553644","name":"质量报告","type":"menu","parentId":"1714256290457591837","orderNum":35,"url":"/report/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591843","name":"质量检查","type":"dir","parentId":"1714256290457591837","orderNum":31,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591845","name":"巡检任务","type":"menu","parentId":"1714256290457591843","orderNum":32,"url":"/inspect/patrolTask/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591846","name":"整改记录","type":"menu","parentId":"1714256290457591843","orderNum":33,"url":"/inspect/rectification/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591863","name":"安全检查","type":"dir","parentId":"1714256290457591856","orderNum":44,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591864","name":"隐患排查","type":"menu","parentId":"1714256290457591863","orderNum":43,"url":"/inspect/hiddenDangerCheck/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591867","name":"安全评分","type":"menu","parentId":"1714256290457591863","orderNum":46,"url":"/inspect/inspect","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780769265687724032","name":"流程表单管理","type":"menu","parentId":"1714256290457591895","orderNum":75,"url":"/configuration/formFlowConfig","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/basic-data/"},{"id":"1780769265696112640","name":"流程表单管理","type":"menu","parentId":"1714256290461786135","orderNum":89,"url":"/configuration/formFlowConfig","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/basic-data/"},{"id":"1714256290461786128","name":"进度跟踪","type":"dir","parentId":"1714256290461786125","orderNum":82,"url":"/#","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1719671740694642733","name":"质量检查库","type":"menu","parentId":"1714256290457591848","orderNum":36,"url":"/baseSetting/checkLibrary/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786118","name":"模型管理","type":"dir","parentId":"1714256290461786117","orderNum":76,"url":"/#","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786120","name":"DWG模型","type":"menu","parentId":"1714256290461786118","orderNum":77,"url":"/main/modelManager/dwg","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786119","name":"BIM模型","type":"menu","parentId":"1714256290461786118","orderNum":76,"url":"/main/modelManager/bim","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786124","name":"WBS映射","type":"menu","parentId":"1714256290461786117","orderNum":79,"url":"/main/wbsOperate","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786123","name":"场景管理","type":"menu","parentId":"1714256290461786117","orderNum":78,"url":"/main/projectManager","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591829","name":"基础数据","type":"dir","parentId":"10000001","orderNum":22,"url":"/basic-data-web","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/basic-data/"},{"id":"1723997045709606939","name":"WBS模板","type":"menu","parentId":"1714256290457591829","orderNum":22,"url":"/configuration/wbsTemplate","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591832","name":"人员信息","type":"menu","parentId":"1714256290457591829","orderNum":24,"url":"/configuration/personaInfo","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1723997045709606940","name":"WBS实例","type":"menu","parentId":"1714256290457591829","orderNum":23,"url":"/configuration/wbsInstance","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591834","name":"基础设置","type":"dir","parentId":"1714256290457591829","orderNum":25,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591836","name":"工作区域","type":"menu","parentId":"1714256290457591834","orderNum":26,"url":"/configuration/workArea","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591835","name":"作业班组","type":"menu","parentId":"1714256290457591834","orderNum":25,"url":"/configuration/operationTeams","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591847","name":"技术交底","type":"menu","parentId":"1714256290457591837","orderNum":34,"url":"/technicExplain/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591848","name":"基础设置","type":"dir","parentId":"1714256290457591837","orderNum":36,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591855","name":"编号规则","type":"menu","parentId":"1714256290457591848","orderNum":37,"url":"/baseSetting/codeRule/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1717107432192331908","name":"GIS管理","type":"menu","parentId":"1717078831549894755","orderNum":92,"url":"/main/modelManager/gis","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1717078831549894756","name":"FBX模型","type":"menu","parentId":"1717078831549894755","orderNum":91,"url":"/main/fbxManager","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1717078831549894755","name":"基础数据","type":"dir","parentId":"10000003","orderNum":91,"url":"/bim-web","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/bim/"},{"id":"1767787790370316289","name":"指挥大屏","type":"dir","parentId":"10000005","orderNum":14,"url":"/","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780830415708225538","name":"数据大屏","type":"menu","parentId":"1780830240604422144","orderNum":6,"url":"/config/screen","component":None,"icon":"leixingshujudapingzhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1767787790370316288","name":"BI配置","type":"dir","parentId":"10000006","orderNum":35,"url":"/bi/","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1767789605354708992","name":"数据集","type":"menu","parentId":"1767787790370316288","orderNum":7,"url":"/config/dataset","component":None,"icon":"leixingshujujizhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1767788068465254400","name":"数据大屏","type":"menu","parentId":"1767787790370316288","orderNum":6,"url":"/config/screen","component":None,"icon":"leixingshujudapingzhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1767790030002823168","name":"模板管理","type":"menu","parentId":"1767787790370316288","orderNum":9,"url":"/config/template","component":None,"icon":"leixingmobanguanlizhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1767789814692421632","name":"数据源","type":"menu","parentId":"1767787790370316288","orderNum":8,"url":"/config/datasource","component":None,"icon":"leixingshujuyuanzhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780830240604422144","name":"BI配置d","type":"dir","parentId":"10000006","orderNum":35,"url":"/bi/","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780830415704031232","name":"数据集","type":"menu","parentId":"1780830240604422144","orderNum":7,"url":"/config/dataset","component":None,"icon":"leixingshujujizhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780830415708225536","name":"模板管理","type":"menu","parentId":"1780830240604422144","orderNum":9,"url":"/config/template","component":None,"icon":"leixingmobanguanlizhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780830415708225537","name":"数据源","type":"menu","parentId":"1780830240604422144","orderNum":8,"url":"/config/datasource","component":None,"icon":"leixingshujuyuanzhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None}],"hasSelectedMenuIds":None,"linkageSwitch":1}}
    rs1 = {"code":200,"msg":"Success","success":True,"data":{"sysMenuTypes":[{"id":"1713851790359179268","name":"供应商管理","type":"menu","parentId":"10000000","orderNum":3,"url":"/builder/supplierManagement","component":None,"icon":"供应商管理","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179271","name":"项目管理","type":"menu","parentId":"10000000","orderNum":4,"url":"/builder/projectManagement","component":None,"icon":"项目管理","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179266","name":"职务管理","type":"menu","parentId":"10000000","orderNum":6,"url":"/builder/positionManagement","component":None,"icon":"职务管理","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179269","name":"企业人员","type":"menu","parentId":"10000000","orderNum":7,"url":"/builder/enterprise","component":None,"icon":"企业人员","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179273","name":"应用配置","type":"dir","parentId":"10000000","orderNum":21,"url":"/builder-setting-web","component":None,"icon":"应用配置","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1713851790359179276","name":"进度报警","type":"menu","parentId":"1713851790359179274","orderNum":9,"url":"/main/baseSettings/entWarnRule","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/plan/"},{"id":"1713851790359179275","name":"日历模板","type":"menu","parentId":"1713851790359179274","orderNum":8,"url":"/main/baseSettings/entCalendarTemplate","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/plan/"},{"id":"1713851790359179278","name":"安全管理","type":"dir","parentId":"1713851790359179273","orderNum":11,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1782612929997176833","name":"删除","type":"btn","parentId":"1713851790359179267","orderNum":2,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1713851790359179284","name":"数据字典","type":"menu","parentId":"10000000","orderNum":20,"url":"/builder/data-dictionary","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179282","name":"流程模板","type":"menu","parentId":"10000000","orderNum":19,"url":"/builder/flow-template","component":None,"icon":"流程模板","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179270","name":"从业人员","type":"menu","parentId":"10000000","orderNum":8,"url":"/builder/personnel","component":None,"icon":"从业人员","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1713851790359179272","name":"角色管理","type":"menu","parentId":"10000000","orderNum":5,"url":"/builder/role","component":None,"icon":"角色管理","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1783326061879099392","name":"操作","type":"btn","parentId":"1713851790359179272","orderNum":5,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1783326061883293696","name":"授权","type":"btn","parentId":"1713851790359179272","orderNum":5,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1713851790359179277","name":"项目进展节点配置","type":"menu","parentId":"1713851790359179274","orderNum":10,"url":"/main/baseSettings/progressNode","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/plan/"},{"id":"1723997045709606934","name":"属性模板","type":"menu","parentId":"1713851790359179273","orderNum":18,"url":"/builder/attributeTemplate","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1714451949827661842","name":"行为积分库","type":"menu","parentId":"1713851790359179278","orderNum":15,"url":"/baseSetting/actionPointsLib/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1713851790359179280","name":"安全风险库","type":"menu","parentId":"1713851790359179278","orderNum":12,"url":"/baseSetting/safetyRisk/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1713851790359179281","name":"考试题库","type":"menu","parentId":"1713851790359179278","orderNum":13,"url":"/baseSetting/questionsBank/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1726905695791513617","name":"防护用品库","type":"menu","parentId":"1713851790359179278","orderNum":14,"url":"/baseSetting/materialWarehouse/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1722440040501309488","name":"物联配置","type":"menu","parentId":"1713851790359179273","orderNum":26,"url":"/builder/iotConfig","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1722440040501309461","name":"质量检查库","type":"menu","parentId":"1722440040501309460","orderNum":17,"url":"/baseSetting/checkLibrary/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1713851790359179267","name":"组织结构","type":"menu","parentId":"10000000","orderNum":2,"url":"/builder/companyprofile","component":None,"icon":"组织管理","path":None,"pathId":None,"isLink":None,"redirect":"/admin/#/login"},{"id":"1782612929992982528","name":"修改","type":"btn","parentId":"1713851790359179267","orderNum":2,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1782612929997176832","name":"新增","type":"btn","parentId":"1713851790359179267","orderNum":2,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1782327411560415234","name":"删除","type":"btn","parentId":"1713851790359179272","orderNum":5,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1713851790359179274","name":"进度管理","type":"dir","parentId":"1713851790359179273","orderNum":8,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714451949827661843","name":"安全评分","type":"menu","parentId":"1713851790359179278","orderNum":16,"url":"/baseSetting/securityScore/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1713851790359179279","name":"安全检查库","type":"menu","parentId":"1713851790359179278","orderNum":11,"url":"/baseSetting/checkLibrary/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1722440040501309460","name":"质量管理","type":"dir","parentId":"1713851790359179273","orderNum":17,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591856","name":"安全管理","type":"dir","parentId":"10000001","orderNum":39,"url":"/sphere-safety-web","component":None,"icon":"安全管理","path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1714256290457591866","name":"整改记录","type":"menu","parentId":"1714256290457591863","orderNum":45,"url":"/inspect/rectification/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591865","name":"巡检任务","type":"menu","parentId":"1714256290457591863","orderNum":44,"url":"/inspect/patrolTask/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591869","name":"岗前教育","type":"menu","parentId":"1714256290457591868","orderNum":47,"url":"/safetyActivity/preEducation","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591844","name":"隐患排查","type":"menu","parentId":"1714256290457591843","orderNum":31,"url":"/inspect/hiddenDangerCheck/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591893","name":"防护用品","type":"menu","parentId":"1714256290457591892","orderNum":65,"url":"/occupationHealth/protectiveArticle/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591894","name":"健康检查","type":"menu","parentId":"1714256290457591892","orderNum":66,"url":"/occupationHealth/HealthCheck/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591881","name":"安全活动","type":"dir","parentId":"1714256290457591856","orderNum":57,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591884","name":"专项活动","type":"menu","parentId":"1714256290457591881","orderNum":59,"url":"/safetyActivity/specialTraining","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591883","name":"安全会议","type":"menu","parentId":"1714256290457591881","orderNum":58,"url":"/safetyActivity/safetyConference","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591882","name":"安全交底","type":"menu","parentId":"1714256290457591881","orderNum":57,"url":"/technicExplain/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591889","name":"目标管理","type":"dir","parentId":"1714256290457591856","orderNum":39,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1719605864688582738","name":"目标责任书","type":"menu","parentId":"1714256290457591889","orderNum":63,"url":"/goalManagement/dutyConclusion/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1719605864688582739","name":"目标考核","type":"menu","parentId":"1714256290457591889","orderNum":64,"url":"/goalManagement/dutyAssessment/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591895","name":"基础设置","type":"dir","parentId":"1714256290457591856","orderNum":68,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591896","name":"安全检查库","type":"menu","parentId":"1714256290457591895","orderNum":68,"url":"/baseSetting/checkLibrary/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591898","name":"考试题库","type":"menu","parentId":"1714256290457591895","orderNum":70,"url":"/baseSetting/questionsBank/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591897","name":"行为积分库","type":"menu","parentId":"1714256290457591895","orderNum":69,"url":"/baseSetting/actionPointsLib/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591902","name":"编号规则","type":"menu","parentId":"1714256290457591895","orderNum":74,"url":"/baseSetting/codeRule/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591900","name":"安全评分","type":"menu","parentId":"1714256290457591895","orderNum":72,"url":"/baseSetting/securityScore/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591899","name":"防护用品库","type":"menu","parentId":"1714256290457591895","orderNum":71,"url":"/baseSetting/materialWarehouse/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591860","name":"岗位职责","type":"menu","parentId":"1714256290457591857","orderNum":41,"url":"/system/duty/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591858","name":"管理制度","type":"menu","parentId":"1714256290457591857","orderNum":39,"url":"/system/manageRegime/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591859","name":"组织机构","type":"menu","parentId":"1714256290457591857","orderNum":40,"url":"/system/orginationStructure","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1719259302770151525","name":"安全报告","type":"menu","parentId":"1714256290457591856","orderNum":67,"url":"/report/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591892","name":"职业健康","type":"dir","parentId":"1714256290457591856","orderNum":63,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591885","name":"安全经费","type":"menu","parentId":"1714256290457591856","orderNum":64,"url":"/securityFunding","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591901","name":"安全风险库","type":"menu","parentId":"1714256290457591895","orderNum":73,"url":"/baseSetting/safetyRisk/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591857","name":"安保体系","type":"dir","parentId":"1714256290457591856","orderNum":40,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591877","name":"应急管理","type":"dir","parentId":"1714256290457591856","orderNum":65,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591879","name":"应急演练","type":"menu","parentId":"1714256290457591877","orderNum":55,"url":"/contingencyManagement/emergencyDrills","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591878","name":"应急预案","type":"menu","parentId":"1714256290457591877","orderNum":54,"url":"/emergencyManagement/emergencyPlan","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591880","name":"应急资源","type":"menu","parentId":"1714256290457591877","orderNum":56,"url":"/emergencyManagement/emergencySupplies","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591886","name":"事故管理","type":"menu","parentId":"1714256290457591856","orderNum":66,"url":"/accidentManage","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591876","name":"危大工程","type":"menu","parentId":"1714256290457591856","orderNum":53,"url":"/riskProject","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591861","name":"设备管理","type":"dir","parentId":"1714256290457591856","orderNum":42,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591862","name":"设备信息","type":"menu","parentId":"1714256290457591861","orderNum":42,"url":"/equipmentManagement/deviceInfo","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591873","name":"安全风险","type":"dir","parentId":"1714256290457591856","orderNum":51,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591874","name":"辨识评估","type":"menu","parentId":"1714256290457591873","orderNum":51,"url":"/dangerManage/dangerAssess","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591875","name":"分级管控","type":"menu","parentId":"1714256290457591873","orderNum":52,"url":"/dangerManage/dangerManage","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591887","name":"临电管理","type":"dir","parentId":"1714256290457591856","orderNum":62,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591888","name":"配电箱","type":"menu","parentId":"1714256290457591887","orderNum":62,"url":"/electricManage/electricBox","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591868","name":"安全教育","type":"dir","parentId":"1714256290457591856","orderNum":43,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591872","name":"安全考核","type":"menu","parentId":"1714256290457591868","orderNum":50,"url":"/safetyActivity/score","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591871","name":"安全培训","type":"menu","parentId":"1714256290457591868","orderNum":49,"url":"/safetyActivity/safetyTrain","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591838","name":"质保体系","type":"dir","parentId":"1714256290457591837","orderNum":27,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591870","name":"教育考试","type":"menu","parentId":"1714256290457591868","orderNum":48,"url":"/safetyActivity/exam","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786125","name":"进度管理","type":"dir","parentId":"10000001","orderNum":80,"url":"/plan-manager-web","component":None,"icon":"进度管理","path":None,"pathId":None,"isLink":None,"redirect":"/plan/"},{"id":"1714256290461786126","name":"进度计划","type":"menu","parentId":"1714256290461786125","orderNum":80,"url":"/main/schedule/list","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786127","name":"实际进度","type":"menu","parentId":"1714256290461786125","orderNum":81,"url":"/main/actual/list","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786135","name":"基础设置","type":"dir","parentId":"1714256290461786125","orderNum":87,"url":"/#","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786136","name":"日历模板","type":"menu","parentId":"1714256290461786135","orderNum":87,"url":"/main/baseSettings/calendarTemplate","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786137","name":"进度报警","type":"menu","parentId":"1714256290461786135","orderNum":88,"url":"/main/baseSettings/warnRule","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1716687262993223720","name":"BIM沙盘","type":"menu","parentId":"1714256290461786125","orderNum":84,"url":"/main/sandbox","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786132","name":"进度报告","type":"dir","parentId":"1714256290461786125","orderNum":85,"url":"/#","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786134","name":"项目进展月报","type":"menu","parentId":"1714256290461786132","orderNum":86,"url":"/main/report/monthProgress","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786133","name":"投资进度月报","type":"menu","parentId":"1714256290461786132","orderNum":85,"url":"/main/report/monthInvest","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591840","name":"组织机构","type":"menu","parentId":"1714256290457591838","orderNum":28,"url":"/system/orginationStructure","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591841","name":"岗位职责","type":"menu","parentId":"1714256290457591838","orderNum":29,"url":"/system/duty/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457690000","name":"责任书","type":"menu","parentId":"1714256290457591838","orderNum":30,"url":"/system/responsibilityLetter/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591839","name":"管理制度","type":"menu","parentId":"1714256290457591838","orderNum":27,"url":"/system/manageRegime/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780769265700306944","name":"流程表单管理","type":"menu","parentId":"1714256290457591848","orderNum":38,"url":"/configuration/formFlowConfig","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/basic-data/"},{"id":"1714256290461786117","name":"BIM管理","type":"dir","parentId":"10000001","orderNum":23,"url":"/bim-web","component":None,"icon":"BIM管理","path":None,"pathId":None,"isLink":None,"redirect":"/bim/"},{"id":"1714256290461786130","name":"整改记录","type":"menu","parentId":"1714256290461786128","orderNum":83,"url":"/main/progressTrack/rectificationRecord","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786129","name":"进度报警","type":"menu","parentId":"1714256290461786128","orderNum":82,"url":"/main/progressTrack/warnList","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591837","name":"质量管理","type":"dir","parentId":"10000001","orderNum":27,"url":"/sphere-quality-web","component":None,"icon":"质量管理","path":None,"pathId":None,"isLink":None,"redirect":"/sphere/"},{"id":"1720716936518553644","name":"质量报告","type":"menu","parentId":"1714256290457591837","orderNum":35,"url":"/report/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591843","name":"质量检查","type":"dir","parentId":"1714256290457591837","orderNum":31,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591845","name":"巡检任务","type":"menu","parentId":"1714256290457591843","orderNum":32,"url":"/inspect/patrolTask/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591846","name":"整改记录","type":"menu","parentId":"1714256290457591843","orderNum":33,"url":"/inspect/rectification/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591863","name":"安全检查","type":"dir","parentId":"1714256290457591856","orderNum":44,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591864","name":"隐患排查","type":"menu","parentId":"1714256290457591863","orderNum":43,"url":"/inspect/hiddenDangerCheck/SECURITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591867","name":"安全评分","type":"menu","parentId":"1714256290457591863","orderNum":46,"url":"/inspect/inspect","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780769265687724032","name":"流程表单管理","type":"menu","parentId":"1714256290457591895","orderNum":75,"url":"/configuration/formFlowConfig","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/basic-data/"},{"id":"1780769265696112640","name":"流程表单管理","type":"menu","parentId":"1714256290461786135","orderNum":89,"url":"/configuration/formFlowConfig","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/basic-data/"},{"id":"1714256290461786128","name":"进度跟踪","type":"dir","parentId":"1714256290461786125","orderNum":82,"url":"/#","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1719671740694642733","name":"质量检查库","type":"menu","parentId":"1714256290457591848","orderNum":36,"url":"/baseSetting/checkLibrary/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786118","name":"模型管理","type":"dir","parentId":"1714256290461786117","orderNum":76,"url":"/#","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786120","name":"DWG模型","type":"menu","parentId":"1714256290461786118","orderNum":77,"url":"/main/modelManager/dwg","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786119","name":"BIM模型","type":"menu","parentId":"1714256290461786118","orderNum":76,"url":"/main/modelManager/bim","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786124","name":"WBS映射","type":"menu","parentId":"1714256290461786117","orderNum":79,"url":"/main/wbsOperate","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290461786123","name":"场景管理","type":"menu","parentId":"1714256290461786117","orderNum":78,"url":"/main/projectManager","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591829","name":"基础数据","type":"dir","parentId":"10000001","orderNum":22,"url":"/basic-data-web","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/basic-data/"},{"id":"1723997045709606939","name":"WBS模板","type":"menu","parentId":"1714256290457591829","orderNum":22,"url":"/configuration/wbsTemplate","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591832","name":"人员信息","type":"menu","parentId":"1714256290457591829","orderNum":24,"url":"/configuration/personaInfo","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1723997045709606940","name":"WBS实例","type":"menu","parentId":"1714256290457591829","orderNum":23,"url":"/configuration/wbsInstance","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591834","name":"基础设置","type":"dir","parentId":"1714256290457591829","orderNum":25,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591836","name":"工作区域","type":"menu","parentId":"1714256290457591834","orderNum":26,"url":"/configuration/workArea","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591835","name":"作业班组","type":"menu","parentId":"1714256290457591834","orderNum":25,"url":"/configuration/operationTeams","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591847","name":"技术交底","type":"menu","parentId":"1714256290457591837","orderNum":34,"url":"/technicExplain/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591848","name":"基础设置","type":"dir","parentId":"1714256290457591837","orderNum":36,"url":None,"component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1714256290457591855","name":"编号规则","type":"menu","parentId":"1714256290457591848","orderNum":37,"url":"/baseSetting/codeRule/QUALITY","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1717107432192331908","name":"GIS管理","type":"menu","parentId":"1717078831549894755","orderNum":92,"url":"/main/modelManager/gis","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1717078831549894756","name":"FBX模型","type":"menu","parentId":"1717078831549894755","orderNum":91,"url":"/main/fbxManager","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1717078831549894755","name":"基础数据","type":"dir","parentId":"10000003","orderNum":91,"url":"/bim-web","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":"/bim/"},{"id":"1767787790370316289","name":"指挥大屏","type":"dir","parentId":"10000005","orderNum":14,"url":"/","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780830415708225538","name":"数据大屏","type":"menu","parentId":"1780830240604422144","orderNum":6,"url":"/config/screen","component":None,"icon":"leixingshujudapingzhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1767787790370316288","name":"BI配置","type":"dir","parentId":"10000006","orderNum":35,"url":"/bi/","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1767789605354708992","name":"数据集","type":"menu","parentId":"1767787790370316288","orderNum":7,"url":"/config/dataset","component":None,"icon":"leixingshujujizhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1767788068465254400","name":"数据大屏","type":"menu","parentId":"1767787790370316288","orderNum":6,"url":"/config/screen","component":None,"icon":"leixingshujudapingzhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1767790030002823168","name":"模板管理","type":"menu","parentId":"1767787790370316288","orderNum":9,"url":"/config/template","component":None,"icon":"leixingmobanguanlizhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1767789814692421632","name":"数据源","type":"menu","parentId":"1767787790370316288","orderNum":8,"url":"/config/datasource","component":None,"icon":"leixingshujuyuanzhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780830240604422144","name":"BI配置d","type":"dir","parentId":"10000006","orderNum":35,"url":"/bi/","component":None,"icon":None,"path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780830415704031232","name":"数据集","type":"menu","parentId":"1780830240604422144","orderNum":7,"url":"/config/dataset","component":None,"icon":"leixingshujujizhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780830415708225536","name":"模板管理","type":"menu","parentId":"1780830240604422144","orderNum":9,"url":"/config/template","component":None,"icon":"leixingmobanguanlizhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None},{"id":"1780830415708225537","name":"数据源","type":"menu","parentId":"1780830240604422144","orderNum":8,"url":"/config/datasource","component":None,"icon":"leixingshujuyuanzhuangtaioff","path":None,"pathId":None,"isLink":None,"redirect":None}],"hasSelectedMenuIds":["1713851790359179267","1713851790359179268","1713851790359179271","1713851790359179272","1713851790359179266","1713851790359179269","1713851790359179270","1713851790359179282","1713851790359179284","1713851790359179273","1782612929997176833","1782612929992982528","1782612929997176832","1783326061879099392","1783326061883293696","1782327411560415234","1713851790359179274","1713851790359179278","1722440040501309460","1723997045709606934","1722440040501309488","1713851790359179275","1713851790359179276","1713851790359179277","1713851790359179279","1713851790359179280","1713851790359179281","1726905695791513617","1714451949827661842","1714451949827661843","1722440040501309461","1714256290457591829","1714256290461786117","1714256290457591837","1714256290457591856","1714256290461786125","1723997045709606939","1723997045709606940","1714256290457591832","1714256290457591834","1714256290461786118","1714256290461786123","1714256290461786124","1714256290457591838","1714256290457591843","1714256290457591847","1720716936518553644","1714256290457591848","1714256290457591889","1714256290457591857","1714256290457591861","1714256290457591868","1714256290457591863","1714256290457591873","1714256290457591876","1714256290457591881","1714256290457591887","1714256290457591892","1714256290457591885","1714256290457591877","1714256290457591886","1719259302770151525","1714256290457591895","1714256290461786126","1714256290461786127","1714256290461786128","1716687262993223720","1714256290461786132","1714256290461786135","1714256290457591835","1714256290457591836","1714256290461786119","1714256290461786120","1714256290457591839","1714256290457591840","1714256290457591841","1714256290457690000","1714256290457591844","1714256290457591845","1714256290457591846","1719671740694642733","1714256290457591855","1780769265700306944","1719605864688582738","1719605864688582739","1714256290457591858","1714256290457591859","1714256290457591860","1714256290457591862","1714256290457591869","1714256290457591870","1714256290457591871","1714256290457591872","1714256290457591864","1714256290457591865","1714256290457591866","1714256290457591867","1714256290457591874","1714256290457591875","1714256290457591882","1714256290457591883","1714256290457591884","1714256290457591888","1714256290457591893","1714256290457591894","1714256290457591878","1714256290457591879","1714256290457591880","1714256290457591896","1714256290457591897","1714256290457591898","1714256290457591899","1714256290457591900","1714256290457591901","1714256290457591902","1780769265687724032","1714256290461786129","1714256290461786130","1714256290461786133","1714256290461786134","1714256290461786136","1714256290461786137","1780769265696112640","1717078831549894755","1717078831549894756","1717107432192331908","1767787790370316289","1767787790370316288","1780830240604422144","1767788068465254400","1767789605354708992","1767789814692421632","1767790030002823168","1780830415708225538","1780830415704031232","1780830415708225537","1780830415708225536"],"linkageSwitch":1}}
    import jsonpath
    Assertions.assert_list_repetition(jsonpath.jsonpath(rs, "$..sysMenuTypes[?(@.id)]..id"))
    Assertions.assert_dictOrList_eq(jsonpath.jsonpath(rs, "$..sysMenuTypes[?(@.id)]..id"),rs1.get("data").get("hasSelectedMenuIds"))


