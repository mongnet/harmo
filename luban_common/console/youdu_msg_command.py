#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/28 20:00
# @Author  : hubiao

from cleo import Command as BaseCommand
from luban_common.msg.youdu import send_msg

class YouduMsgCommand(BaseCommand):
    """
    发送有度消息

    youdu
        {title : 消息标题，必填参数}
        {content : 消息内容，必填参数}
        {sendTo : 发送给谁，多个用户之间用下划线分隔，如“胡彪_邵君兰”}
        {--f|file=None : 发送的文件}
        {--e|session=0 : 会话session，当session=0时，会新建一个新的会话窗口，默认为新建会话窗口}
    """

    def handle(self):
        send_msg(title=self.argument("title"), content=self.argument("content"), sendTo=self.argument("sendTo"), file=self.option("file"), session=self.option("session"))


