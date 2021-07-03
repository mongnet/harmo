#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by hubiao on 2021/07/03
import os
import sys
import time
import json
import requests

from luban_common import base_utils
from luban_common.operation import yaml_file


class WeiXinMessage:
    '''
    发送微信消息提醒功能
    '''

    @classmethod
    def __init__(self):
        self.__webhook = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=3742a454-9e6c-4733-8205-b515d373ec48"

    @classmethod
    def send_message_text(self,content,mentioned_mobile_list=None):
        '''
        发送文本消息
        :param content: 文本内容，最长不超过2048个字节，必须是utf8编码
        :param mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人，例如：["13800001111","@all"]
        :return:
        '''
        wechat_json = {
            "msgtype": "text",
            "text": {
                "content": f"{content}",
                "mentioned_mobile_list": ["@all"] if mentioned_mobile_list is None else mentioned_mobile_list
            }
        }

        response = requests.post(self.__webhook,data=json.dumps(wechat_json),verify=True).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("text消息发送成功")
        else:
            print("text消息发送失败")

    @classmethod
    def send_message_markdown(self,content):
        '''
        发送markdown消息
        :param content: markdown内容，最长不超过4096个字节，必须是utf8编码
        :return:
        '''
        wechat_json = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }

        response = requests.post(self.__webhook,data=json.dumps(wechat_json),verify=True).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("markdown消息发送成功")
        else:
            print("markdown消息发送失败")

    @classmethod
    def send_message_card(self,title,url,content=None,picurl="http://www.lubansoft.com/uploads/1540977656.jpg"):
        '''
        图文消息
        :param title: 标题，不超过128个字节，超过会自动截断
        :param content: 描述，不超过512个字节，超过会自动截断
        :param url: 点击后跳转的链接。
        :param picurl: 图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。
        :return:
        '''
        wechat_json = {
            "msgtype": "news",
            "news": {
               "articles" : [
                   {
                       "title" : title,
                       "description" : content,
                       "url" : url,
                       "picurl" : picurl
                   }
                ]
            }
        }

        response = requests.post(self.__webhook,data=json.dumps(wechat_json),verify=True).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("textcard消息发送成功")
        else:
            print("textcard消息发送失败")

    @classmethod
    def send_image(self,file):
        '''
        发送图片
        :param imgBase64: 图片（base64编码前）最大不能超过2M，支持JPG,PNG格式
        :return:
        '''
        if base_utils.getFileSize(file) > 20480000 or file.split(".")[-1].lower() not in ["png","jpg"]:
            raise ValueError("图片（base64编码前）最大不能超过2M，且只支持JPG,PNG格式")
        imgBase64 = base_utils.toFileBase64(file)
        wechat_json = {
            "msgtype": "image",
            "image": {
                "base64": imgBase64,
                "md5": base_utils.getFileMD5(file)
            }
        }

        response = requests.post(self.__webhook,data=json.dumps(wechat_json),verify=True).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("发送图片成功")
        else:
            print("发送图片失败")

    @classmethod
    def send_file(self,file):
        '''
        发送文件
        :param media_id: 文件id，通过下文的文件上传接口获取
        :return:
        '''
        wechat_json = {
            "msgtype": "file",
            "file": {
                 "media_id": self.up_file(file)
            }
        }

        response = requests.post(self.__webhook,data=json.dumps(wechat_json),verify=True).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("发送文件成功")
        else:
            print("发送文件失败")

    @classmethod
    def up_file(self,file):
        '''
        发送文件
        :param media_id: 文件id，通过下文的文件上传接口获取
        :return:
        '''
        if base_utils.getFileSize(file) < 5 or base_utils.getFileSize(file) > 204800000:
            raise ValueError("文件大小在5B~20M之间")
        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={self.__webhook.split('=')[-1]}&type=file"
        files = {'file1': open(file, 'rb')}
        response = requests.post(url,files=files).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("上传成功")
        else:
            print("上传失败")
        return response["media_id"]

if __name__ == '__main__':
    send = WeiXinMessage()
    # send.send_message_text(content='这里是消息内容，http://work.weixin.qq.com 使用很方便。')
    markdown_content = """
                    ># 这是`markdown`消息
                    >事　项：<font color=\"info\">开会</font>
                    >组织者：@miglioguan
                    >
                    >会议室：<font color=\"info\">上海研发部</font>
                    >日　期：<font color=\"warning\">2020年8月18日</font>
                    >时　间：<font color=\"comment\">上午9:00-11:00</font>
                    >
                    >请**准时**参加会议。
                    >
                    >如需修改会议信息，请点击：[这里还可以有连接](https://work.weixin.qq.com)"""
    # send.send_message_markdown(content=markdown_content)
    # send.send_message_card(title='这是卡片消息(PASS)',content='这里是消息内容，可以点击查看更多跳转到网页',url="www.qq.com")
    # send.send_file(file="weixin.py")
    # send.send_image(file="../../data/20201222101200.png")