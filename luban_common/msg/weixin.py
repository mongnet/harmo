#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by hubiao on 2017/12/26
import os
import sys
import time
import json
import requests

from luban_common.operation import yaml_file


class WeiXinMessage:
    """
    发送微信消息提醒功能
    """

    @classmethod
    def __init__(self):
        default_parame = yaml_file.get_yaml_data(f"{os.path.dirname(os.path.realpath(__file__))}/../config/parameConfig.yaml").get("weixin")
        self.__CorpID = default_parame["weixin"]["corpid"]
        self.__Secret = default_parame["weixin"]["secret"]
        # 企业应用的id
        self.__AgentId = default_parame["weixin"]["agentid"]
        self.__expire_time = sys.maxsize
        self.__access_token = self.__get_token()
        self.__url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.__access_token}"

    @classmethod
    def __get_token(self):
        """
        获取access_token
        """
        if self.__expire_time >time.time():
            response = requests.get(f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.__CorpID}&corpsecret={self.__Secret}")
            response_json = json.loads(response.content)
            self.__expire_time = time.time() + response_json["expires_in"]
            self.__access_token = response_json["access_token"]
        return self.__access_token

    @classmethod
    def send_message_text(self,title,content,toparty):
        """
        发送文本消息
        :param title:消息的标题
        :param content:消息的内容
        :param toparty:通知的部门
        :return:
        """
        wechat_json = {
            "toparty":f"{toparty}",
            "msgtype":"text",
            "agentid":self.__AgentId,
            "text": {
               "content" : f"消息主题：{title}\n消息内容：{content}"
           },
            "safe":0
        }
        response = requests.post(self.__url,data=json.dumps(wechat_json)).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("发送成功")
        else:
            print("发送失败")

    @classmethod
    def send_message_textcard(self,title,content,toparty,msg_url="#"):
        """
        发送卡片消息
        :param title:消息的标题
        :param content:消息的内容
        :param toparty:通知的部门
        :param msg_url:点击卡片后跳转的连接
        :return:
        """
        wechat_json = {
            "toparty":f"{toparty}",
            "msgtype":"textcard",
            "agentid":self.__AgentId,
            "textcard": {
                "title":f"{title}",
                "description" : content,
                "url":msg_url,
                "btntxt":"查看更多"
           },
            "safe":0
        }
        response = requests.post(self.__url,data=json.dumps(wechat_json)).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("发送成功")
        else:
            print("发送失败")

    @classmethod
    def send_message_markdown(self,content,toparty):
        """
        发送markdown消息
        :param content:消息的内容
        :param toparty:通知的部门
        :return:
        """
        wechat_json = {
            "toparty":f"{toparty}",
            "msgtype" : "markdown",
            "agentid" : self.__AgentId,
            "markdown" : {
                "content" : f"{content}"
                }
            }
        response = requests.post(self.__url,data=json.dumps(wechat_json)).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("发送成功")
        else:
            print("发送失败")


if __name__ == "__main__":
    send = WeiXinMessage()
    send.send_message_text(title="这是文本消息",content="这里是消息内容，\n还可以有<a href=\"http://work.weixin.qq.com\">连接</a>，使用很方便。",toparty=3)
    markdown_content = """这是`markdown`消息
                    >**可以加粗**
                    >事　项：<font color=\"info\">开会</font>
                    >组织者：@miglioguan
                    >
                    >会议室：<font color=\"info\">上海研发部</font>
                    >日　期：<font color=\"warning\">2020年8月18日</font>
                    >时　间：<font color=\"comment\">上午9:00-11:00</font>
                    > 
                    >请准时参加会议。
                    >
                    >如需修改会议信息，请点击：[这里还可以有连接](https://work.weixin.qq.com)"""
    send.send_message_markdown(content=markdown_content,toparty=3)
    send.send_message_textcard(title="这是卡片消息(PASS)",content="这里是消息内容，可以点击查看更多跳转到网页",toparty="3")