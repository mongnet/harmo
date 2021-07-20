#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2019/1/9 18:15
# @Author  : hubiao
# @File    : send_report.py

import time,sys
sys.path.append('.')
from luban_common.operation.xml_file import *
from luban_common.msg import weixin


# Center项目组
# toparty = 2
# Myluban app项目组
# toparty = 3
# PDS项目组
# toparty = 4
# 运营系统项目组
# toparty = 5

def sendCardReport(title,toparty,PassIsSend=False,file="../report/report.xml"):
    '''
    pytest xml报告,发送报告信息
    :param title: 报告标题
    :param toparty: 发送给的部门
    :param PassIsSend: 用例全部通过时是否发送消息，默认不发送
    :param file: pytest xml报告地址
    :return:
    '''
    #获取pytest报告信息
    ptestReport = xml.pytestXml(file)
    #组装报告信息
    #发送时间
    sendTime = time.strftime("%Y-%m-%d %H:%M")
    times = f"<div class=\"gray\">{sendTime}</div>"
    #用例总数
    cases = f"<div class=\"normal\">执行 {ptestReport['tests']} 个用例</div>"
    #错误数
    errors = f"<div class=\"normal\">报错 {ptestReport['errors']} 个用例</div>"
    #失败数
    failures = f"<div class=\"normal\">失败 {ptestReport['failures']} 个用例</div>"
    #跳过数
    skips = f"<div class=\"normal\">跳过 {ptestReport['skips']} 个用例</div>"
    #持续时间
    durations = f"<div class=\"normal\">消耗 {ptestReport['time']} 秒</div>"
    #其它信息
    more = "<div class=\"gray\">如有疑问请联系相关负责人</div>"
    des = ''
    sendWeixinMsg = weixin.WeiXinMessage()
    if int(ptestReport['errors']) + int(ptestReport['skips']) + int(ptestReport['failures']) == 0:
        if PassIsSend:
            des = times + cases + durations + "用例全部通过，请各位了解" + more
            sendWeixinMsg.send_message_textcard(title=title,content=des,satr="PASS",toparty=toparty)
    else:
        des = times + cases + errors + failures + skips + durations + more
        sendWeixinMsg.send_message_textcard(title=title,content=des,satr="FAIL",toparty=toparty)
        assert False

#发送报告
sendCardReport(title="今日演示企业巡检结果",toparty="2",PassIsSend=True)

if __name__ == '__main__':
    pass
