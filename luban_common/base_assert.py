#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2019/4/3 15:12
# @Author  : hubiao
# @File    : base_assert.py
import operator
import allure

class Assertions:
    '''
    公共断言方法
    '''

    @classmethod
    @allure.step('校验status_code和code')
    def assert_all_code(self, response, expected_http_code, expected_code):
        '''
        校验status_code和code状态码
        :param response: 响应数据
        :param expected_http_code: 预期的http状态码
        :param expected_code: 预期code状态码
        :return:
        '''
        assert response.get("status_code") == expected_http_code,f'校验失败,实际值为:{response.get("status_code")},预期值为:{expected_http_code},响应信息为:{response.get("source_response")}'
        assert response.get("code")[0] == expected_code,f'校验失败,实际值为:{response.get("code")[0]},预期值为:{expected_code},响应信息为:{response.get("source_response")}'

    @allure.step('校验状态码，实际值为:{2},预期值为:{3}')
    def assert_code(self, response, reality_code, expected_code):
        '''
        验证response响应体中的code或status_code状态码
        assert_code 后期会废弃，建议统一使用 assert_equal_value 方法
        :param response: 响应数据
        :param reality_code: 响应体中的code或status_code状态码
        :param expected_code: 预期code或status_code状态码
        :return:
        '''
        assert reality_code == expected_code, f'校验失败,实际值为:{reality_code},预期值为:{expected_code},响应信息为:{response.get("source_response")}'

    @classmethod
    @allure.step('校验数据集中指定key的值，预期key为:{2}，预期值为:{3}')
    def assert_assign_attribute_value(self, data,key,expected_value):
        """
        校验数据集中指定key的值
        :param data:校验的data
        :param key:预期key
        :param expected_value:预期值
        :return:
        """
        if isinstance(data[key], list):
            if expected_value != data[key]:
                if [False for value in expected_value if value not in data[key]]:
                    assert False, '预期值不等于实际值'
        elif isinstance(data[key], str):
            assert data[key] != "" and data[key] != None, '实际值不能为空'
            assert data[key] == expected_value, '预期值不等于实际值'
        else:
            assert False, '只支持list和str的校验，其余暂不支持'

    @classmethod
    @allure.step('校验数据集中存在预期值，预期值为:{2}')
    def assert_in_value(self, data,expected_value):
        """
        校验数据集中存在预期值
        :param data: 校验的data
        :param expected_value:预期值
        :return:
        """
        if isinstance(data, (list,str)):
            if isinstance(expected_value,list):
                assert set(expected_value) <= set(data)
            else:
                assert expected_value in data,f'响应结果中不存在预期值为：{expected_value} 的数据'
        else:
            assert False, '只支持list、str的校验，其余暂不支持'

    @classmethod
    @allure.step('校验以预期值开头，预期值为:{2}')
    def assert_startswith(self, data,expected_value):
        """
        校验以预期值开头
        :param data: 校验的data
        :param expected_value: 预期值
        :return:
        """
        if isinstance(data,str):
            assert data.startswith(expected_value),f"没有以预期值：{expected_value} 开头"
        else:
            assert False, '只支持 str 的校验，其余暂不支持'

    @classmethod
    @allure.step('校验以预期值结尾，预期值为:{2}')
    def assert_endswith(self, data,expected_value):
        """
        校验以预期值结尾
        :param data: 校验的data
        :param expected_value: 预期值
        :return:
        """
        if isinstance(data,str):
            assert data.endswith(expected_value),f"没有以预期值：{expected_value} 结尾"
        else:
            assert False, '只支持 str 的校验，其余暂不支持'

    @classmethod
    @allure.step('校验字典中存在预期key，预期值为:{2}')
    def assert_in_key(self, data,key):
        """
        校验字典中存在预期key
        :param data: 响应数据
        :param key: 预期key值
        :return:
        """
        if isinstance(data, dict):
            assert key in data.keys(),f"结果中不存在预期为:{key} 的数据"
        else:
            assert False, '只支持dict的校验，其余暂不支持'

    @classmethod
    @allure.step('校验数据集中不存在预期值，预期值为:{2}')
    def assert_not_in_value(self, data,expected_value):
        """
        校验数据集中不存在预期值
        :param data: 响应数据
        :param expected_value: 预期值
        :return:
        """
        if isinstance(data, (list,str)):
            assert expected_value not in data,"结果中存在预期值"
        else:
            assert False, '只支持list、str的校验，其余暂不支持'

    @classmethod
    @allure.step('校验字典中不存在预期key，预期值为:{2}')
    def assert_not_in_key(self, data,expected_key):
        """
        验证check_value中不存在预期key
        :param data: 响应数据
        :param expected_key: 预期key
        :return:
        """
        if isinstance(data, dict):
            assert expected_key not in data.keys(),"校验结果中存在预期key"
        else:
            assert False, '只支持dict的校验，其余暂不支持'

    @classmethod
    @allure.step('校验等于预期值，预期值为:{2}')
    def assert_equal_value(self, reality_value, expected_value):
        """
        校验等于预期值
        :param reality_value: 实际值
        :param expected_value: 预期值
        :return:
        """
        if isinstance(reality_value, (str,int)):
            assert expected_value == reality_value, "校验结果不等于预期值"
        else:
            assert False, '只支持str和int的校验，其余暂不支持'

    @classmethod
    @allure.step('校验是否等于None')
    def assert_isNone(self, reality_value):
        """
        校验是否等于None
        :param reality_value: 实际值
        :return:
        """
        if reality_value is None:
            assert True
        else:
            assert False, "校验值不等于None"

    @classmethod
    @allure.step('校验时间小于预期，实际值为:{2}，预期值为:{3}')
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
            assert False, '响应持续时间大于预期值'

    @classmethod
    @allure.step('校验字典或列表是否相等，实际值为:{1}，预期值为:{2}')
    def assert_dictOrList_eq(self,reality, expected):
        """
        校验字典或列表是否相等
        :param reality: 实际值
        :param expected: 预期值
        :return:
        """
        if isinstance(reality, dict) and isinstance(expected, dict):
            if operator.eq(reality,expected):
                assert True
            else:
                assert False,'二个字典不相等'
        elif isinstance(reality, list) and isinstance(expected, list):
            if list(set(reality).difference(set(expected))) == [] and list(set(expected).difference(set(reality))) == []:
                assert True
            else:
                assert False, '二个列表不相等'
        else:
            assert False, '传入的数据不是字典或列表'

if __name__ == '__main__':
    dict1 = {"projId":113692,"ppid":130817,"projName":"BW接口用工程-勿删160711"}
    dict2 = {"projId":113692,"projName":"BW接口用工程-勿删160711","ppid":130817}
    dict3 = {'hu':[1111,'adfaf','胡彪']}
    list1 = [1111,'adfaf','胡彪']
    list2 = [1111,'胡彪','adfaf']
    str2 = {'hu':'adf'}
    Assertions.assert_dictOrList_eq(dict1,dict2)
    Assertions.assert_dictOrList_eq(list1,list2)
    Assertions.assert_assign_attribute_value(str2, 'hu', 'adf')
    Assertions.assert_assign_attribute_value(dict3, "hu", ['adfaf',1111, '胡彪'])
