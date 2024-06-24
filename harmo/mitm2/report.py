import os
import time,yaml
from jinja2 import Environment, PackageLoader



class ReportUtil:
	def __init__(self):
		pass

	def createReport(self,data):
		with open('config1.yaml', 'r', encoding='utf-8') as file:
			configInfo = yaml.load(file, Loader=yaml.FullLoader)
		createDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		reporter = "菜鸡吴"
		title = u"测试报告"
		env = Environment(loader=PackageLoader('resources', 'templates'))
		template_name = 'testRport_template.ejs'
		status = u"成功" if data['error']==[] else u"失败"
		total = len(data['error'])
		failed = len([each for each in data['error'] if each['info'] !=[]])
		Pass = total - failed
		details = {
            'createdate' : createDate,
            'reporter' : reporter,
            'host' : configInfo['Setting']['Host'],
            'total': total,
            'pass': Pass,
            'failed': failed,
            'caseList':[],
			'moduleNameList': data['moduleNameList'],
			'moduleCaseTotal':data['moduleCaseTotal']
		}
		for each in data['error']:
			caseEach = {"moduleName":each['moduleName'],'caseName':each['name'],'status':'<p class="pass">通过</p>','errorinfo':self._upgradeError(data['error'])}
			if each['info']!=[]: caseEach['status'] = '<p class="fail">通过</p>'
			details['caseList'].append(caseEach)
		template = env.get_template(template_name)
		html = template.render(title=title, status=status, created_when=createDate, details=details)
		current_dir = os.getcwd()
		output_dir = r'D:\demo\demo_new\resources\output'+os.sep
		if not os.path.exists(output_dir):
			os.mkdir(output_dir)
		os.chdir(output_dir)
		report_name = 'TestRport_'+str(createDate).replace(' ','_').replace(':','')+'.html'
		fo = open(report_name, "w",encoding='utf-8')
		fo.writelines(html)
		fo.close()
		os.chdir(current_dir)
		print(f"create {report_name}:", "完成")

	def _upgradeError(self,data):
		text =''
		for each in data:
			if each['info']!=[]:
				text = text +'<div style="width: 100%;word-break: break-word;"> <b>URL</b>: ' + each['info']['url'] + '</div>'
				for content in each['info']['contentList']:
					if len(content['expect']) == len(content['actual']):
						n = 0
						for i in range(len(content['expect'])):
							if content['expect'][i] != content['actual'][i] : n = i
						text = text+"<b>路径:</b> "+str(content['key']).replace('_','.')+'<br>'+" <b>预期:</b> "+str(content['expect'][n])+" <b>实际:</b> "+str(content['actual'][n])+'<br>'+'<br>'
					else:
						text = text + "路径: "+str(content['key']).replace('_','.')+'<br>'+" 预期与实际数量不一致"+'<br>'+" <b>预期:</b> "+str(content['expect'])+" <b>实际:</b> "+str(content['actual'])+'<br>'+'<br>'
			else:
				text = '--'
		return text



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
	data ={
	'error': [{
		'name': '创建表单并完成签名签章',
		'info': [{
			'id': 'oMp3tho7pz',
			'url': 'http://service.lbuilder.cn/luban-data-manage/data/form/page?categoryIdList=364c674f6b784440a34da66727066433&projectIdList=3a456b90b0c7487993db8fc23bf74fb0&catalogIdList=863d56b32f6343009f1fbb2d27f0f959&sectionIdList=8f3097c224b54631825bf5d0ce087913&pageIndex=1&pageSize=10',
			'method': 'GET',
			'contentList': [{
				'key': 'data_result_size',
				'expect': [60825],
				'actual': [60826]
			}]
		}, {
			'id': '3uaOPoiaFh',
			'url': 'http://service.lbuilder.cn/luban-data-manage/common/data/form/DATA_FORM/v1/approval?id=ae5a32012cdf48909fa32403d483684f',
			'method': 'GET',
			'contentList': [{
				'key': 'data_size',
				'expect': [60825],
				'actual': [60826]
			}]
		}, {
			'id': 'bGnHXwZUXa',
			'url': 'http://service.lbuilder.cn/luban-data-manage/data/form/page?categoryIdList=364c674f6b784440a34da66727066433&projectIdList=3a456b90b0c7487993db8fc23bf74fb0&catalogIdList=863d56b32f6343009f1fbb2d27f0f959&sectionIdList=8f3097c224b54631825bf5d0ce087913&pageIndex=1&pageSize=10',
			'method': 'GET',
			'contentList': [{
				'key': 'data_result_startDate',
				'expect': [1692100370000],
				'actual': [1692105210000]
			}, {
				'key': 'data_result_size',
				'expect': [60825],
				'actual': [60826]
			}]
		}, {
			'id': 'GtWhyD5PRT',
			'url': 'http://service.lbuilder.cn/luban-data-manage/common/data/form/DATA_FORM/v1/approval?id=ae5a32012cdf48909fa32403d483684f',
			'method': 'GET',
			'contentList': [{
				'key': 'data_size',
				'expect': [60825],
				'actual': [60826]
			}]
		}, {
			'id': 'AIhq3KxnM1',
			'url': 'http://service.lbuilder.cn/pdscommon/rs/fileaddress/downloadURLs',
			'method': 'POST',
			'contentList': [{
				'key': 'fileSize',
				'expect': [60825,12345],
				'actual': [60826]
			}]
		}]
	}]
}
	ReportUtil().createReport(data)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/