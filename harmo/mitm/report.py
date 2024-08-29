#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/4/3 15:00
# @Author  : hubiao
# @Email   : 250021520@qq.com

import os
import time,yaml
import jsonpath
from jinja2 import Environment, FileSystemLoader

from harmo.config import Config
from harmo.global_map import Global_Map
from harmo.msg.robot import WeiXin


class ReportUtil:
    def __init__(self):
        self.details = {}

    def createReport(self,modelName:str,replayResult:dict):
        createDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        reporter = "那个谁"
        title = f"{modelName} " if modelName else f"集成测试"
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources","templates")
        env = Environment(loader=FileSystemLoader(templates_dir))
        template_name = 'testRport_template.ejs'
        status = u"成功" if replayResult['result']==[] else u"失败"
        failed = len(jsonpath.jsonpath(replayResult.get('result'),'$..info[?(@.status=="fail")]')) if jsonpath.jsonpath(replayResult.get('result'),'$..info[?(@.status=="fail")]') else 0
        Pass = len(jsonpath.jsonpath(replayResult.get('result'),'$..info[?(@.status=="pass")]')) if jsonpath.jsonpath(replayResult.get('result'),'$..info[?(@.status=="pass")]') else 0
        ignore = len(jsonpath.jsonpath(replayResult.get('result'),'$..info[?(@.status=="ignore")]')) if jsonpath.jsonpath(replayResult.get('result'),'$..info[?(@.status=="ignore")]') else 0
        self.details = {
            'createdate' : createDate,
            # 'reporter' : reporter,
            'title' : title,
            'host' : Global_Map.get('setting').get('baseUrl'),
            'total': Pass+failed+ignore,
            'pass': Pass,
            'failed': failed,
            'ignore': ignore,
            'caseList':[],
			'moduleNameList': replayResult.get('moduleNameList'),
			'moduleCaseTotal':replayResult.get('moduleCaseTotal'),
            'totalTimes': replayResult.get('totalTimes')
		}
        nmber = 0
        for each in replayResult.get('result'):
            if each['info']:
                for eachInfo in each['info']:
                    nmber += 1
                    caseEach = {"nmber":nmber,"moduleName":each['moduleName'],'status':'<p class="pass">通过</p>','url':"",'errorinfo':self._upgradeError(eachInfo)}
                    if eachInfo.get("status") == "pass":
                        caseEach['status'] = '<p class="pass">通过</p>'
                    elif eachInfo.get("status") == "fail":
                        caseEach['status'] = '<p class="fail">失败</p>'
                    else:
                        caseEach['status'] = '<p class="ignore">忽略</p>'
                    caseEach['url'] = f'[{eachInfo.get("method")}] {eachInfo.get("url")}'
                    self.details['caseList'].append(caseEach)
        # 检查模板文件是否存在
        template_path = os.path.join(templates_dir, template_name)
        if not os.path.exists(template_path):
            raise ValueError(f"模板文件 {template_path} 未找到。")
        else:
            # 尝试加载模板
            try:
                template = env.get_template(template_name)
                # 渲染模板
                html = template.render(title=title, status=status, created_when=createDate, details=self.details)
            except Exception as e:
                print(f"加载模板时出错：{e}")
        output_dir = os.path.join(Config.project_root_dir, "output"+os.sep)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        os.chdir(output_dir)
        report_name = 'TestRport_'+str(createDate).replace(' ','_').replace(':','')+'.html'
        with open(report_name, 'w', encoding='utf-8') as fileObjct:
            fileObjct.writelines(html)
        self._send_report(report_name)
        return report_name

    def _send_report(self,file):
        weixin_robot = Global_Map.get('setting').get('weixin_robot')
        if weixin_robot:
            if self.details.get('failed') + self.details.get('failed') != 0:
                markdown_content = f'''
                                    # 警告！`{self.details.get('title')}` 回放出现异常
                                    >通知范围：@所有人
                                    >本次共执行 **{self.details.get('total')}** 条接口
                                    >有 <font color=\'info\'>**{self.details.get('pass')}**</font> 条执行成功
                                    >有 `**{self.details.get('failed')}**` 条执行失败
                                    >有 <font color=\'comment\'>**{self.details.get('ignore')}**</font> 条被忽略
                                    >共耗时 <font color=\'comment\'>**{round(self.details.get('totalTimes'), 2)}**</font> 秒
                                    >
                                    >可点击下方 report 文件查看详情'''
                WeiXin().send_message_markdown(hookkey=weixin_robot, content=markdown_content)
                if file:
                    WeiXin().send_file(hookkey=weixin_robot, file=file)
            else:
                markdown_content = f'''
                                    # 恭喜 <font color=\'info\'>{self.details.get('title')}</font> 回放通过!
                                    >通知范围：@所有人
                                    >本次共执行 **{self.details.get('total')}** 条接口，<font color=\'info\'>**全部执行通过**</font>，耗时 **{round(self.details.get('totalTimes'), 2)}** 秒
                                    >
                                    >可点击下方 report 文件查看详情'''
                WeiXin().send_message_markdown(hookkey=weixin_robot, content=markdown_content)
                if file:
                    WeiXin().send_file(hookkey=weixin_robot, file=file)

    def _upgradeError(self,eachInfo):
        text =''
        if eachInfo:
            if 'contentList' in eachInfo:
                for content in eachInfo['contentList']:
                    if content['key'] == 'resp.diff':
                        text = '<b>数据 diff 失败:</b></br></br>'
                        for line in content['diff_lines']:
                            if line.startswith('- '):
                                text = text+"<span class='line_old'>"+line.replace("<", "&lt;").replace(">", "&gt;")+'</span></br>'
                            else:
                                text = text+"<span class='line_new'>"+line.replace("<", "&lt;").replace(">", "&gt;")+'</span></br>'
                    elif content.get('expect',None) == content.get('actual',None):
                        n = 0
                        for i in range(len(content.get('expect'))):
                            if content['expect'][i] != content['actual'][i] : n = i
                        text = text+"<b>路径:</b> "+str(content['key']).replace('_','.')+'<br>'+" 预期与实际不一致"+'<br>'+" <b>预期:</b><span class='pass'> "+str(content['expect'][n])+"</span><br><b> 实际:</b><span class='fail'> "+str(content['actual'][n])+'</span><br><br>'
                    else:
                        text = text+"<b>路径:</b> "+str(content['key']).replace('_','.')+'<br>'+" 预期与实际不一致"+'<br>'+" <b>预期:</b><span class='pass'> "+str(content['expect'])+"</span><br><b> 实际:</b><span class='fail'> "+str(content['actual'])+'</span><br><br>'
            elif eachInfo.get("status") == "fail":
                text = '<p class="fail">失败</p>'
            elif eachInfo.get("status") == "ignore":
                text = '<p class="ignore">忽略</p>'
            else:
                text = '--'
        else:
            text = '--'
        return text

if __name__ == '__main__':
    data ={
    "result":
    [
        {
            "name": "职务管理-编辑职务",
            "info":
            [
                {
                    "id": "Nge9Fvn5P5",
                    "url": "http://service.lbuilder.cn/auth-server/auth/token?",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "ufojspde2Q",
                    "url": "http://service.lbuilder.cn/auth-server/auth/enterprises",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "1Qh5ptgihV",
                    "url": "http://service.lbuilder.cn/auth-server/auth/enterprise",
                    "method": "PUT",
                    "status": "pass"
                },
                {
                    "id": "ywlWdHVO0y",
                    "url": "http://service.lbuilder.cn/iworks/main-page/list",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "jRgFY1J080",
                    "url": "http://service.lbuilder.cn/auth-server/auth/innerSystemToken/192",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "Xb2kCkkjuo",
                    "url": "http://service.lbuilder.cn/auth-server/auth/enterprise",
                    "method": "PUT",
                    "status": "pass"
                },
                {
                    "id": "vKDKk6WeBX",
                    "url": "http://service.lbuilder.cn/auth-server/user/get-user-detail",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "jFF1gJCoSW",
                    "url": "http://service.lbuilder.cn/pdscommon/rs/userInfo/userPortraitInfo/hubiao",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "WrktTsykR6",
                    "url": "http://service.lbuilder.cn/iworks/main-page/list",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "z8EK8HKBZX",
                    "url": "http://service.lbuilder.cn/pdscommon/rs/fileaddress/longLineDownloadURLs",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "lc2E4NKftk",
                    "url": "http://service.lbuilder.cn/auth-server/user/get-user-detail",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "EyKJKojQVW",
                    "url": "http://service.lbuilder.cn/process/task/statistic/allBusinessTypeCount",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "MLlysZqg0m",
                    "url": "http://service.lbuilder.cn/auth-server/auth/menu/parentId/2517",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "CDMgheZXZf",
                    "url": "http://service.lbuilder.cn/iworks/report-fill/page",
                    "method": "POST",
                    "status": "fail",
                    "contentList":
                    [
                        {
                            "key": "data_items_name",
                            "expect":
                            [
                                "MonNet"
                            ],
                            "actual":
                            [
                                "hubiao"
                            ]
                        }
                    ]
                },
                {
                    "id": "OvcWccd1Uj",
                    "url": "http://service.lbuilder.cn/iworks/report-fill/page",
                    "method": "POST",
                    "status": "fail",
                    "contentList":
                    [
                        {
                            "key": "data_items_name",
                            "expect":
                            [
                                "MonNet"
                            ],
                            "actual":
                            [
                                "hubiao"
                            ]
                        }
                    ]
                },
                {
                    "id": "CIWWR93I2l",
                    "url": "http://service.lbuilder.cn/process/task/statistic/taskDeptStatusCount?businessType=luban-process-inspection",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "3P5dOo30MD",
                    "url": "http://service.lbuilder.cn/auth-server/auth/menu/parentId/2517",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "pRyo35se7k",
                    "url": "http://service.lbuilder.cn/process/task/center/todo",
                    "method": "POST",
                    "status": "fail",
                    "contentList":
                    [
                        {
                            "key": "data_result_deferDay",
                            "expect":
                            [
                                157,
                                0,
                                0,
                                0,
                                362,
                                365,
                                467,
                                0,
                                0,
                                0
                            ],
                            "actual":
                            [
                                158,
                                0,
                                0,
                                0,
                                363,
                                366,
                                468,
                                0,
                                0,
                                0
                            ]
                        }
                    ]
                },
                {
                    "id": "BFtfzxVGWB",
                    "url": "http://service.lbuilder.cn/iworks/knowledge/catalog/0",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "GYn8ZzO69Z",
                    "url": "http://service.lbuilder.cn/iworks/knowledge/page",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "E5qxnfhqm0",
                    "url": "http://service.lbuilder.cn/iworks/report-fill/page",
                    "method": "POST",
                    "status": "fail",
                    "contentList":
                    [
                        {
                            "key": "data_items_name",
                            "expect":
                            [
                                "MonNet"
                            ],
                            "actual":
                            [
                                "hubiao"
                            ]
                        }
                    ]
                },
                {
                    "id": "ay5s2k4Kam",
                    "url": "http://service.lbuilder.cn/iworks/report-template/page",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "SCdWcNcNpG",
                    "url": "http://service.lbuilder.cn/iworks/announce/page",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "M3DjaPa0Us",
                    "url": "http://service.lbuilder.cn/auth-server/auth/authgroup/192",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "viP2f071lk",
                    "url": "http://service.lbuilder.cn/iworks/knowledge/catalog/1",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "T7tuyGms4y",
                    "url": "http://service.lbuilder.cn/iworks/announce/page",
                    "method": "POST",
                    "status": "pass"
                }
            ],
            "moduleName": "Center模块"
        },
        {
            "name": "职务管理-编辑职务",
            "info":
            [
                {
                    "id": "Nge9Fvn5P5",
                    "url": "http://service.lbuilder.cn/auth-server/auth/token?",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "ufojspde2Q",
                    "url": "http://service.lbuilder.cn/auth-server/auth/enterprises",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "1Qh5ptgihV",
                    "url": "http://service.lbuilder.cn/auth-server/auth/enterprise",
                    "method": "PUT",
                    "status": "pass"
                },
                {
                    "id": "ywlWdHVO0y",
                    "url": "http://service.lbuilder.cn/iworks/main-page/list",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "jRgFY1J080",
                    "url": "http://service.lbuilder.cn/auth-server/auth/innerSystemToken/192",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "Xb2kCkkjuo",
                    "url": "http://service.lbuilder.cn/auth-server/auth/enterprise",
                    "method": "PUT",
                    "status": "pass"
                },
                {
                    "id": "vKDKk6WeBX",
                    "url": "http://service.lbuilder.cn/auth-server/user/get-user-detail",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "jFF1gJCoSW",
                    "url": "http://service.lbuilder.cn/pdscommon/rs/userInfo/userPortraitInfo/hubiao",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "WrktTsykR6",
                    "url": "http://service.lbuilder.cn/iworks/main-page/list",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "z8EK8HKBZX",
                    "url": "http://service.lbuilder.cn/pdscommon/rs/fileaddress/longLineDownloadURLs",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "lc2E4NKftk",
                    "url": "http://service.lbuilder.cn/auth-server/user/get-user-detail",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "EyKJKojQVW",
                    "url": "http://service.lbuilder.cn/process/task/statistic/allBusinessTypeCount",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "MLlysZqg0m",
                    "url": "http://service.lbuilder.cn/auth-server/auth/menu/parentId/2517",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "CDMgheZXZf",
                    "url": "http://service.lbuilder.cn/iworks/report-fill/page",
                    "method": "POST",
                    "status": "fail",
                    "contentList":
                    [
                        {
                            "key": "data_items_name",
                            "expect":
                            [
                                "MonNet"
                            ],
                            "actual":
                            [
                                "hubiao"
                            ]
                        }
                    ]
                },
                {
                    "id": "OvcWccd1Uj",
                    "url": "http://service.lbuilder.cn/iworks/report-fill/page",
                    "method": "POST",
                    "status": "fail",
                    "contentList":
                    [
                        {
                            "key": "data_items_name",
                            "expect":
                            [
                                "MonNet"
                            ],
                            "actual":
                            [
                                "hubiao"
                            ]
                        }
                    ]
                },
                {
                    "id": "CIWWR93I2l",
                    "url": "http://service.lbuilder.cn/process/task/statistic/taskDeptStatusCount?businessType=luban-process-inspection",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "3P5dOo30MD",
                    "url": "http://service.lbuilder.cn/auth-server/auth/menu/parentId/2517",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "pRyo35se7k",
                    "url": "http://service.lbuilder.cn/process/task/center/todo",
                    "method": "POST",
                    "status": "fail",
                    "contentList":
                    [
                        {
                            "key": "data_result_deferDay",
                            "expect":
                            [
                                157,
                                0,
                                0,
                                0,
                                362,
                                365,
                                467,
                                0,
                                0,
                                0
                            ],
                            "actual":
                            [
                                158,
                                0,
                                0,
                                0,
                                363,
                                366,
                                468,
                                0,
                                0,
                                0
                            ]
                        }
                    ]
                },
                {
                    "id": "BFtfzxVGWB",
                    "url": "http://service.lbuilder.cn/iworks/knowledge/catalog/0",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "GYn8ZzO69Z",
                    "url": "http://service.lbuilder.cn/iworks/knowledge/page",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "E5qxnfhqm0",
                    "url": "http://service.lbuilder.cn/iworks/report-fill/page",
                    "method": "POST",
                    "status": "fail",
                    "contentList":
                    [
                        {
                            "key": "data_items_name",
                            "expect":
                            [
                                "MonNet"
                            ],
                            "actual":
                            [
                                "hubiao"
                            ]
                        }
                    ]
                },
                {
                    "id": "ay5s2k4Kam",
                    "url": "http://service.lbuilder.cn/iworks/report-template/page",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "SCdWcNcNpG",
                    "url": "http://service.lbuilder.cn/iworks/announce/page",
                    "method": "POST",
                    "status": "pass"
                },
                {
                    "id": "M3DjaPa0Us",
                    "url": "http://service.lbuilder.cn/auth-server/auth/authgroup/192",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "viP2f071lk",
                    "url": "http://service.lbuilder.cn/iworks/knowledge/catalog/1",
                    "method": "GET",
                    "status": "pass"
                },
                {
                    "id": "T7tuyGms4y",
                    "url": "http://service.lbuilder.cn/iworks/announce/page",
                    "method": "POST",
                    "status": "pass"
                }
            ],
            "moduleName": "Center模块2"
        }
    ],
    "moduleNameList":
    [
        "Center模块",
    "Center模块2"
    ],
    "moduleCaseTotal":
    [
        26,22
    ],
    "urlTotal": 52
}

    print(ReportUtil().createReport("模块",data))
