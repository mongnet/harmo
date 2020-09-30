#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2019/3/27 16:04
# @Author  : hubiao
# @File    : youdu.py

import requests

# http://192.168.2.203/zentao/www/index.php?m=api&f=setYouduMessBySession&session={session}&members={sendTo}&title={title}&cont={content}
# 当session=0时，会得到一个新的session

def send_youdu(title,content,sendTo,session=0):
    '''
    发送有度消息
    :param title: 消息窗口标题
    :param content: 消息内容
    :param sendTo: 发送给谁，多个用户之间用下划线分隔，如“胡彪_邵君兰”
    :param session: 会话session，当session=0时，会新建一个新的会话窗口，默认为新建会话窗口
    :return: 返回当前会话的session,当session为0时，会返回一个新的session，不为0时返回当前session
    '''
    title = title
    content = content
    sendTo = sendTo
    session = session
    res_session = requests.post(
        f"http://192.168.2.203/zentao/www/index.php?m=api&f=setYouduMessBySession&session={session}&members={sendTo}&title={title}&cont={content}")
    return res_session.text

if __name__ == '__main__':
    pass
    print(send_youdu(title="测试消息标题", content="测试消息内容\n换行", sendTo="胡彪"))


