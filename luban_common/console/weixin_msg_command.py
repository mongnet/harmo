#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/28 20:00
# @Author  : hubiao

from cleo import Command as BaseCommand
from luban_common.msg.weixin import WeiXinMessage

class WeixinMsgCommand(BaseCommand):
    """
    发送微信消息

    weixin
        {--t|title= : 消息标题}
        {--c|content= : 消息内容}
        {--d|department= : 发送部门ID，这个ID需要到企业微信中查看}
        {--o|option=text: 消息类型，三种消息类型text、card、markdown}
    """

    def handle(self):
        send = WeiXinMessage()
        if self.option("option") == "text":
            send.send_message_text(title=self.option("title"),content=self.option("content"),toparty=self.option("department"))
        elif self.option("option") == "card":
            send.send_message_textcard(title=self.option("title"), content=self.option("content"),toparty=self.option("department"))
        elif self.option("option") == "markdown":
            send.send_message_markdown(content=self.option("content"), toparty=self.option("department"))
        else:
            raise TypeError("只支持 text、card、markdown 类型")


