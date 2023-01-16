#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2019/3/27 16:04
# @Author  : hubiao
# @File    : youdu.py
import os

import requests

from luban_common.operation.ini_file import ManageConfig
from luban_common import base_utils


def send_msg(title, content, sendTo, file=None, session=0, sessionType=1):
    """
    发送有度消息
    :param title: 消息窗口标题
    :param content: 消息内容
    :param sendTo: 发送给谁，多个用户之间用下划线分隔，如“胡彪_邵君兰”
    :param file: 要发送文件的路径
    :param session: 会话，当session=0时，会新建一个新的会话窗口，默认为0
    :param sessionType: 会话类型，1：sendTo+title的md5，2：sendTo的md5，默认为1
    :return: 返回当前会话的session,当session为0时，会返回一个新的session，不为0时返回当前session
    """
    if not all([title,content,sendTo]):
        raise SyntaxError("必填参数不能为None False 空列表/空字符串/空元组/空/数字0")
    file = None if file == "None" else file
    # 求sendTo+title的md5来判断是否要新启会话
    session_md5 = base_utils.getStrMD5(sendTo+title) if sessionType == 1 else base_utils.getStrMD5(sendTo)
    # 读取session
    current_path = os.path.dirname(os.path.realpath(__file__))
    cf = ManageConfig(file_path=f"{current_path}/../config/youdu_session.ini")
    cf_session_md5 = cf.getConfig("session").get(session_md5)
    cf_session = cf_session_md5 if cf_session_md5 is not None else session
    body = {
        "session": session if session == 0 else cf_session,
        "members":sendTo,
        "title":title,
        "cont":content
    }
    filepath = base_utils.file_is_exist(file) if file is not None else file
    response = requests.request("post","http://192.168.2.203/zentao/www/index.php?m=api&f=setYouduFileMsg",data=body,files=None if file is None else {"file":open(filepath, "rb")})
    res_session = response.text
    assert response.status_code == 200,"有度消息发送失败，响应信息不等于200"
    assert len(res_session) != 0,"有度消息发送失败，标题或内容超过长度"
    # 写入session
    cf.writeConfig(section="session", key=session_md5, value=res_session)
    return res_session


if __name__ == "__main__":
    filepath = "../../data/Quality_check_lib.xls"
    send_msg(title="测试消息", content="测试消息内容\n换行", sendTo="胡彪")


