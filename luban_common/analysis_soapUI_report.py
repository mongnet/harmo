# -*- coding:utf8 -*-
#encoding = utf8
__author__ = 'hubiao'

from xml.etree import ElementTree as ET
import os,re,sys
reload(sys)
sys.setdefaultencoding("utf8")

class SoapUIFileInfo(object):
    '''
    获取soapUI文件信息
    '''
    def getRepot(self,Directory):
        '''
        获取SoapUI结果报告信息
        :param file: 报告文件路径目录
        :return: 返回json对象
        '''
        #指定要获取的报告为report.xml
        files = Directory+'/report.xml'
        tree = []
        root=ET.parse(files).getroot()
        for suite in root.findall('testsuite'):
            #print suite.get("name")
            tempSuite = {'time': suite.get("time"), 'name': suite.get("name"), 'tests': suite.get("tests"),'case':[]}
            # print tempSuite
            for case in suite.findall('testcase'):
                # print "-"+case.get("name")
                tempCase = {'time': case.get("time"), 'name': case.get("name"),'failure':[]}
                tempStep = {}
                for step in case.findall('failure'):
                    if step.text:
                        Fstep = SoapUIFileInfo.getStrAndFilterHtml(self,'b',step.text)
                        Finfo = SoapUIFileInfo.getStrAndFilterHtml(self,'pre',step.text)
                        tempStep ={'step': Fstep, 'message': Finfo}
                    else:
                        tempStep = {'step': "Case执行异常，未生成step", 'message': step.get("message")}
                if tempStep:
                    tempCase['failure'].append(tempStep)
                else:
                    tempCase.pop('failure')
                tempSuite['case'].append(tempCase)
            tree.append(tempSuite)
        return tree

    def getStrAndFilterHtml(self,tag,text,filte=True):
        '''
        从HTMl中获取字符串并对HTML进行过滤
        :param tag: 要过滤的HTML标签，不包含尖括号
        :param text: 要过滤的文本
        :param filte: 是否过滤，True或False，默认为过滤
        :return:返回html标签中的文本信息
        '''
        data = re.search('<'+tag+'>(.+?)</'+tag+'>',text, re.S)
        if filte:
            filterHtml = re.compile('<[^>]+>')
            result = filterHtml.sub("", data.group())
        else:
            result = data.group()
        return result

    def getSuite_Case_steps(self,file):
        '''
        获取SoapUI工程文件中的测试集、测试用例、测试步骤信息
        :param file: 工程文件路径
        :return: 返回工程信息json对象
        '''
        tree = {'projcet':[],'suite':[],'case':[],'step':[],'stats':True,'msg':''}
        root=ET.parse(file).getroot()
        #处理xml命名空间问题
        import re
        site = re.findall('{(.+?)}',root.tag)
        if site:
            namespaces = {'con': site[0]}
        else:
            namespaces = None
        # 如果根节点中存在id和name属性就执行解析，否则不执行
        if root.attrib.has_key('id'):
            # print root.get('name') + root.get('id')
            tree['projcet'].append({'id': root.get("id"), 'name': root.get("name")})
            for suite in root.findall('con:testSuite',namespaces):
                # print suite.get("name")+suite.get("id")
                tree['suite'].append({'id': suite.get("id"), 'name': suite.get("name"),'disabled':True if suite.get("disabled")=='true'else False})
                for case in suite.findall('con:testcase',namespaces):
                    # print "-"+case.get("name")+case.get("id")
                    tree['case'].append({'id': case.get("id"), 'name': case.get("name"),'disabled':True if case.get("disabled")=='true'else False})
                    for step in case.findall('con:testStep',namespaces):
                        # print "--"+step.get("name")+step.get("id")
                        tree['step'].append({'id':step.get("id"),'name':step.get("name"),'disabled':True if step.get("disabled")=='true'else False})
        else:
            tree['stats'] = False
            version = root.get('soapui-version')
            tree['msg'] = '当前工程使用的是SoapUI '+version+'创建，SoapUI 5.0.0及之前的版本不会自动生成ID属性，请检查工程文件'
        return tree

    def executeSoapUI(self,file,Directory):
        '''
        执行soapui工程并获取报告信息
        :param file:要执行的soapui工程，相对于当前文件
        :param Directory:生成报告的路径
        :return:
        '''
        try:
            tempfile = file.decode('utf8').encode('GBK')
            os.system(r'testrunner.bat -r -j "%s" -f "%s"'% (tempfile,Directory))
            tree = SoapUIFileInfo.getRepot(self,Directory)
        except Exception as e:
            return e
        return tree

#a = SoapUIFileInfo()
#a.executeSoapUI('Project/BV/EDS-工.xml','Project/BV/report')
#import json
#print json.dumps(a.getRepot('Project/test/report'))
#a.getSuite_Case_steps(file='Project/Test/soapui.xml')
