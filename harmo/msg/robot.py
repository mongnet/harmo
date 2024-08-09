#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Created by hubiao on 2021/07/03

import json
import requests
import urllib3
from harmo import base_utils
from typing import Optional
urllib3.disable_warnings()

class WeiXin:
    """
    企业微信机器人消息
    """

    @classmethod
    def send_message_text(self,hookkey: str,content: str,mentioned_mobile_list: Optional[list]=None):
        """
        发送文本消息
        :param hookkey: webhook的key
        :param content: 文本内容，最长不超过2048个字节，必须是utf8编码
        :param mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人，例如：["13800001111","@all"]
        :return:
        """
        if len(content.encode()) > 2048:
            raise ValueError("文本内容，最长不超过2048个字节")
        if len(hookkey) != 36:
            raise ValueError("hookkey错误，hookkey应该是一个36位的字符串")
        if not mentioned_mobile_list:
            if isinstance(mentioned_mobile_list, list):
                for m in mentioned_mobile_list:
                    if len(m) == 11 and m.startswith("1"):
                        pass
                    else:
                        raise ValueError(f"{m} 不是一个正确的手机号")
            else:
                raise ValueError("mobile必须是一个列表")
        wechat_json = {
            "msgtype": "text",
            "text": {
                "content": f"{content}",
                "mentioned_mobile_list": ["@all"] if mentioned_mobile_list is None else mentioned_mobile_list
            }
        }
        __webhook = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={hookkey}"
        response = requests.post(__webhook,data=json.dumps(wechat_json),verify=False).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("text消息发送成功")
        else:
            print("text消息发送失败")

    @classmethod
    def send_message_markdown(self,hookkey: str,content: str):
        """
        发送markdown消息
        :param hookkey: webhook的key
        :param content: markdown内容，最长不超过4096个字节，必须是utf8编码
        :return:
        """
        if len(content.encode()) > 4096:
            raise ValueError("文本内容，最长不超过4096个字节")
        if len(hookkey) != 36:
            raise ValueError("hookkey错误，hookkey应该是一个36位的字符串")
        wechat_json = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }

        __webhook = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={hookkey}"
        response = requests.post(__webhook,data=json.dumps(wechat_json),verify=False).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("markdown消息发送成功")
        else:
            print("markdown消息发送失败")

    @classmethod
    def send_message_card(self,hookkey: str,title: str,content: str,url: Optional[str]=None,picurl: Optional[str]=None):
        """
        图文消息
        :param hookkey: webhook的key
        :param title: 标题，不超过128个字节，超过会自动截断
        :param content: 描述，不超过512个字节，超过会自动截断
        :param url: 点击后跳转的链接。
        :param picurl: 图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。
        :return:
        """
        if len(hookkey) != 36:
            raise ValueError("hookkey错误，hookkey应该是一个36位的字符串")
        wechat_json = {
            "msgtype": "news",
            "news": {
               "articles" : [
                   {
                       "title" : "无标题消息" if title == None else title,
                       "description" : content,
                       "url" : "#" if url == None else url,
                       "picurl" : picurl
                   }
                ]
            }
        }

        __webhook = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={hookkey}"
        response = requests.post(__webhook,data=json.dumps(wechat_json),verify=False).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("card消息发送成功")
        else:
            print("card消息发送失败")

    @classmethod
    def send_image(self,hookkey: str,file: str):
        """
        发送图片
        :param hookkey: webhook的key
        :param imgBase64: 图片（base64编码）最大不能超过2M，支持JPG,PNG格式
        :return:
        """
        if len(hookkey) != 36:
            raise ValueError("hookkey错误，hookkey应该是一个36位的字符串")
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

        __webhook = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={hookkey}"
        response = requests.post(__webhook,data=json.dumps(wechat_json),verify=False).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("发送图片成功")
        else:
            print("发送图片失败")

    @classmethod
    def send_file(self,hookkey: str,file: str):
        """
        发送文件
        :param hookkey: webhook的key
        :param file: 文件相对路径
        :return:
        """
        if len(hookkey) != 36:
            raise ValueError("hookkey错误，hookkey应该是一个36位的字符串")
        wechat_json = {
            "msgtype": "file",
            "file": {
                 "media_id": self.__up_file(hookkey,file)
            }
        }

        __webhook = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={hookkey}"
        response = requests.post(__webhook,data=json.dumps(wechat_json),verify=False).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("发送文件成功")
        else:
            print("发送文件失败")

    @classmethod
    def __up_file(self,hookkey: str,file: str):
        """
        上传文件
        :param hookkey: webhook的key
        :param file: 文件大小在5B~20M之间
        :return: media_id
        """
        if base_utils.getFileSize(file) < 5 or base_utils.getFileSize(file) > 204800000:
            raise ValueError("文件大小在5B~20M之间")
        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={hookkey}&type=file"
        files = {"file1": open(file, "rb")}
        response = requests.post(url,files=files,verify=False).json()
        if response["errcode"] == 0 and response["errmsg"] == "ok":
            print("上传文件成功")
        else:
            print("上传文件失败")
        return response["media_id"]

class Feishu:
    """
    飞书自定义机器人消息
    """

    @classmethod
    def send_message_text(self, hookkey: str, content: str, atAll: bool):
        """
        发送文本消息
        :param hookkey: webhook的key
        :param content: 文本内容，最长不超过2048个字节，必须是utf8编码
        :param at: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人，例如：["13800001111","@all"]
        :return:
        """
        if len(content.encode()) > 2048:
            raise ValueError("文本内容，最长不超过2048个字节")
        if len(hookkey) != 36:
            raise ValueError("hookkey错误，hookkey应该是一个36位的字符串")
        wechat_json = {
            "msg_type": "text",
            "content": {
                "text": f"<at user_id=\"all\">所有人</at>\n {content}" if atAll else content
            }
        }
        __webhook = f"https://open.feishu.cn/open-apis/bot/v2/hook/{hookkey}"
        response = requests.post(__webhook,data=json.dumps(wechat_json),verify=False).json()
        if response["code"] == 0 and response["msg"] == "success":
            print("text消息发送成功")
        else:
            print("text消息发送失败")

    @classmethod
    def send_message_card(self,hookkey: str,title: str,content: str,url: Optional[str]=None):
        """
        图文消息
        :param hookkey: webhook的key
        :param title: 标题，不超过128个字节，超过会自动截断
        :param content: 描述，理论上不限制长度
        :param url: 点击后跳转的链接。
        :return:
        """
        if len(hookkey) != 36:
            raise ValueError("hookkey错误，hookkey应该是一个36位的字符串")
        wechat_json = {
            "msg_type": "interactive",
            "card": {
                "elements": [{
                    "tag": "div",
                    "text": {
                        "content": f"{content}",
                        "tag": "lark_md"
                    }
                }, {
                    "actions": [{"tag":"button","text":{"content":f"更多详情:UPPERLEFT:这里","tag":"lark_md"},"url":url,"type":"default","value":{}}] if url else [],
                    "tag": "action"
                }],
                "header": {
                    "title": {
                        "content": f"{title}",
                        "tag": "plain_text"
                    }
                }
            }
        }
        __webhook = f"https://open.feishu.cn/open-apis/bot/v2/hook/{hookkey}"
        response = requests.post(__webhook,data=json.dumps(wechat_json),verify=False).json()
        if response["code"] == 0 and response["msg"] == "success":
            print("card消息发送成功")
        else:
            print("card消息发送失败")


if __name__ == "__main__":
    send = WeiXin()
    sendfeishu = Feishu()
    # send.send_message_text(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",content="这里是消息内容，http://work.weixin.qq.com 使用很方便。",mentioned_mobile_list=["18019463445","13916829124"] )
    # markdown_content = """
    #                         ># 这是`markdown`消息
    #                         >作　者：<font color=\"info\">MonNet</font>
    #                         >公众号：彪哥的测试之路
    #                         >
    #                         >会议室：<font color=\"info\">上海</font>
    #                         >日　期：<font color=\"warning\">2020年8月18日</font>
    #                         >时　间：<font color=\"comment\">上午9:00-11:00</font>
    #                         >
    #                         >请**准时**参加会议。
    #                         >
    #                         >如需修改会议信息，请点击：[这里还可以有连接](https://work.weixin.qq.com)"""
    # markdown_content = f'''
    #                     # 用例 d
    #                     >名称：<font color="comment">名称</font>\n
    #                     >描述：<font color="comment">描述</font>\n
    #                     >位置：<font color="comment">位置</font>\n>原因：<font color="comment">原因</font>'''
    # send.send_message_markdown(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",content=markdown_content)
    # jj = "".join([markdown_content,"\n>我不是一个人"])
    # print(len(jj.encode()))
    # send.send_message_markdown(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",content=jj)
    # send.send_message_card(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",title="这是卡片消息(PASS)",content="这里是消息内容，可以点击查看更多跳转到网页",url="http://",picurl="http://www.lubansoft.com/uploads/1540977656.jpg")
    # send.send_message_card(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",title="这是卡片消息(PASS)",content="这里是消息内容，可以点击查看更多跳转到网页")
    # send.send_file(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",file="weixin.py")
    # send.send_image(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",file="../../data/20201222101200.png")
    sendfeishu.send_message_text(hookkey="73040523-c59b-429e-aebd-3a8c65531a75",content="这里是飞书消息内容",atAll=True)
    sendfeishu.send_message_card(hookkey="73040523-c59b-429e-aebd-3a8c65531a75",title="这是卡片消息(PASS)",content="**西湖**，<at id=all></at> \n~~位于浙江省杭州市西湖区龙井路1号~~，*杭州市区西部*，景区总面积49平方千米，汇水面积为21.22平方千米，湖面面积为6.38平方千米。\n<font color='green'> 绿色文本 </font> \n<font color='red'> 红色文本 </font> \n<font color='grey'> 灰色文本 </font> \n[飞书机器人助手](https://botbuilder.feishu.cn/home)",url="https://work.weixin.qq.com")
    sendfeishu.send_message_card(hookkey="73040523-c59b-429e-aebd-3a8c65531a75",title="这是卡片消息(PASS)",content="**西湖**，<at id=all></at> \n~~位于浙江省杭州市西湖区龙井路1号~~，*杭州市区西部*，景区总面积49平方千米，汇水面积为21.22平方千米，湖面面积为6.38平方千米。\n<font color='green'> 绿色文本 </font> \n<font color='red'> 红色文本 </font> \n<font color='grey'> 灰色文本 </font> \n[飞书机器人助手](https://botbuilder.feishu.cn/home)")