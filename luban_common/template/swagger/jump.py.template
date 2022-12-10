#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/7/27 17:55
# @Author  : system
# @File    : jump.py

import allure

class Jump:
    '''
    JumpRestService
    '''

    @allure.step('cas 302 jump接口')
    def jump(self, item_fixture,resource):
        '''
        cas 302 jump接口
        :param item_fixture: item fixture,
        '''
        # resource = f'/rs/jump'
        response = item_fixture.request('GET', resource)
        return response