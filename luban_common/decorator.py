#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by hubiao on 2017/5/17
from __future__ import  unicode_literals
from functools import wraps
import inspect
from luban_common import log

log = log.MyLog()
def CaseAssertion(attempt=3):
    '''
    用例装饰器
    :param attempt: 重试次数
    :return:
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            att = 0
            while att < attempt:
                try:
                    log.info('--> %s',func.__name__)
                    ret = func(*args, **kwargs)
                    log.info('<-- %s, %s\n',func.__name__,'Success')
                    return ret
                except AssertionError as e:
                    log.error('AssertionError, %s', e)
                    log.error('<-- %s, %s, %s\n',func.__name__,'AssertionError','Fail')
                    raise AssertionError(e)
                except Exception as e:
                    log.error('Exception, %s', e)
                    log.error('<-- %s, %s, %s\n',func.__name__,'Exception','Error')
                    if att ==2:
                        raise Exception(e)
                    att += 1
        return wrapper
    return decorator


def retry(func):
    @wraps(func)
    def wrapper(*args, **kw):
        try:
            funcname = str(func.__name__)
            print(funcname)
            print(func)
            ret = func(*args, **kw)
            return ret
        except Exception as e:
            print(e)
    return wrapper


class wd:
    @classmethod
    @retry
    def rq(self):
        username = "hubiao"
        print("adf")

if __name__ == "__main__":
    a = wd.rq()