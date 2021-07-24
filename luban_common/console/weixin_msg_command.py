#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/28 20:00
# @Author  : hubiao

from cleo import Command as BaseCommand
from luban_common.msg.robot import WeiXin

class WeixinMsgCommand(BaseCommand):
    """
    发送微信消息

    weixin
        {hookkey : webhook的key，必填参数}
        {content : 消息内容，必填参数}
        {--m|mobilelist=None : 手机号字符串，多个手机号用|隔开，如："13800138000|13700137000"}
        {--t|title=None : 消息标题}
        {--u|url=None : 点击后跳转的链接}
        {--o|option=text : 消息类型，三种消息类型text、card、markdown}
    """

    def handle(self):
        send = WeiXin()
        if self.option("option") == "text":
            mlist = None if self.option("mobilelist") == "None" else self.option("mobilelist").split("|")
            if isinstance(mlist,list):
                for m in mlist:
                    if len(m) == 11 and m.startswith("1"):
                        pass
                    else:
                        raise ValueError(f"{m} 不是一个正确的手机号")
            send.send_message_text(hookkey=self.argument("hookkey"),content=self.argument("content"),mentioned_mobile_list=mlist)
        elif self.option("option") == "card":
            send.send_message_card(hookkey=self.argument("hookkey"), content=self.argument("content"),title=self.option("title"),url=self.option("url"))
        elif self.option("option") == "markdown":
            send.send_message_markdown(hookkey=self.argument("hookkey"),content=self.argument("content"))
        else:
            raise TypeError("只支持 text、card、markdown 类型")


