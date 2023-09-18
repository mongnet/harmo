#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2023-9-15 20:12
# @Author : hubiao
# @Email : 250021520@qq.com
# @File : render_template.py

from jinja2 import Template

def rend_template_str(source_str, *args, **kwargs):
    '''
    渲染模板
    :param source_str:
    :param args:
    :param kwargs:
    :return:
    '''
    t = Template(source_str, variable_start_string='${', variable_end_string='}')
    res = t.render(*args, **kwargs)
    if source_str.startswith("${") and source_str.endswith("}"):
        try:
            return eval(res)
        except Exception:  # noqa
            return res
    else:
        return res

def rend_template_dict(source_obj, *args, **kwargs):
    '''
    渲染模板对象
    :param source_obj:
    :param args:
    :param kwargs:
    :return:
    '''
    if isinstance(source_obj, dict):
        for key, value in source_obj.items():
            if isinstance(value, str):
                source_obj[key] = rend_template_str(value, *args, **kwargs)
            elif isinstance(value, dict):
                rend_template_dict(value, *args, **kwargs)
            elif isinstance(value, list):
                source_obj[key] = rend_template_list(value, *args, **kwargs)
            else:
                pass
    return source_obj

def rend_template_list(source_list, *args, **kwargs):
    '''
    渲染模板
    :param source_list:
    :param args:
    :param kwargs:
    :return:
    '''
    if isinstance(source_list, list):
        new_array = []
        for item in source_list:
            if isinstance(item, str):
                new_array.append(rend_template_str(item, *args, **kwargs))
            elif isinstance(item, list):
                new_array.append(rend_template_list(item, *args, **kwargs))
            elif isinstance(item, dict):
                new_array.append(rend_template_dict(item, *args, **kwargs))
            else:
                new_array.append(item)
        return new_array
    else:
        return source_list

def rend_template_any(any_obj, *args, **kwargs):
    '''
    渲染模板对象
    :param any_obj:
    :param args:
    :param kwargs:
    :return:
    '''
    if isinstance(any_obj, str):
        return rend_template_str(any_obj, *args, **kwargs)
    elif isinstance(any_obj, dict):
        return rend_template_dict(any_obj, *args, **kwargs)
    elif isinstance(any_obj, list):
        return rend_template_list(any_obj, *args, **kwargs)
    else:
        return any_obj

if __name__ == "__main__":
    l = [{'Query': {'mobile': '${generate_random_mail()}', 'address': '${lb_driver}'},
         'Validate': [{'assert_code': ['resp.status_code', 200]}, {'assert_code': ['resp.code', '${lb_driver}']}]}]
    l2 = {'Validate': [{'assert_code': ['resp.status_code', 200]}, {'assert_code': ['resp.code', '$lb_driver']}]}
    import base_utils

    context = {}
    context.update({'lb_driver': '223'})
    # context.update(__builtins__)  # noqa 内置函数加载
    context.update(base_utils.__dict__)  # 自定义函数对象
    print(l)
    rend_template_any(l, context)
    print(l)