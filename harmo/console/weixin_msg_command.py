#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/28 20:00
# @Author  : hubiao

from cleo.commands.command import Command
from cleo.helpers import argument, option
from harmo.msg.robot import WeiXin

class WeixinMsgCommand(Command):
    name = "weixin"
    description = "发送企业微信消息"
    arguments = [
        argument(
            "hookkey",
            description="webhook的key，必填"
        ),
        argument(
            "content",
            description="消息内容，必填"
        )
    ]
    options = [
        option(
            "mobilelist",
            "m",
            description="手机号字符串，多个手机号用|隔开，如：13800138000|13700137000",
            flag=False,
            default=None
        ),
        option(
            "title",
            "t",
            description="消息标题",
            flag=False,
            default=None
        ),
        option(
            "option",
            "o",
            description="消息类型，三种消息类型text、card、markdown",
            flag=False,
            default="text"
        ),
        option(
            "url",
            "u",
            description="点击后跳转的链接",
            flag=False,
            default=None
        ),
        option(
            "picurl",
            "p",
            description="图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150",
            flag=False,
            default=None
        ),

    ]
    def handle(self):
        send = WeiXin()
        if self.option("option") == "text":
            mlist = None if self.option("mobilelist") is None else str(self.option("mobilelist")).split("|")
            send.send_message_text(hookkey=self.argument("hookkey"),content=self.argument("content"),mentioned_mobile_list=mlist)
        elif self.option("option") == "card":
            send.send_message_card(hookkey=self.argument("hookkey"), content=self.argument("content"),title=self.option("title"),url=self.option("url"),picurl=self.option("picurl"))
        elif self.option("option") == "markdown":
            send.send_message_markdown(hookkey=self.argument("hookkey"),content=self.argument("content"))
        else:
            raise TypeError("消息类型只支持 text、card、markdown 三种类型")


