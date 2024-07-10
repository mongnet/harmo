import os
import time,yaml
from jinja2 import Environment, PackageLoader



class ReportUtil:
	def __init__(self):
		pass

	def createReport(self,data):
		with open('config.yaml', 'r', encoding='utf-8') as file:
			configInfo = yaml.load(file, Loader=yaml.FullLoader)
		createDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		reporter = "菜鸡吴"
		title = u"测试报告"
		env = Environment(loader=PackageLoader('resources', 'templates'))
		template_name = 'testRport_template.ejs'
		status = u"成功" if data['error']==[] else u"失败"
		total = len(data['error'])
		failed = len([each for each in data['error'] if each['info']])
		Pass = total - failed
		details = {
            'createdate' : createDate,
            'reporter' : reporter,
            'host' : configInfo['Setting']['Url'],
            'total': total,
            'pass': Pass,
            'failed': failed,
            'caseList':[],
			'moduleNameList': data['moduleNameList'],
			'moduleCaseTotal':data['moduleCaseTotal']
		}
		for each in data['error']:
			print(each)
			caseEach = {"moduleName":each['moduleName'],'caseName':each['name'],'status':'<p class="pass">通过</p>','url':"",'errorinfo':self._upgradeError(each['info'])}
			if each['info']:
				caseEach['status'] = '<p class="fail">失败</p>'
				caseEach['url'] = '<p class="fail">失败</p>'
			details['caseList'].append(caseEach)
		template = env.get_template(template_name)
		html = template.render(title=title, status=status, created_when=createDate, details=details)
		current_dir = os.getcwd()
		output_dir = f'{current_dir}/resources/output'+os.sep
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
			if each:
				text = text +'<div style="width: 100%;word-break: break-word;"> <b>URL</b>: ' + each['url'] + '</div><br>'
				for content in each['contentList']:
					if len(content['expect']) == len(content['actual']):
						n = 0
						for i in range(len(content['expect'])):
							if content['expect'][i] != content['actual'][i] : n = i
						text = text+"<b>路径:</b> "+str(content['key']).replace('_','.')+'<br>'+" <b>预期:</b> "+str(content['expect'][n])+" <b>实际:</b> "+str(content['actual'][n])+'<br><br>'
					else:
						text = text + "路径: "+str(content['key']).replace('_','.')+'<br>'+" 预期与实际数量不一致"+'<br>'+" <b>预期:</b> "+str(content['expect'])+" <b>实际:</b> "+str(content['actual'])+'<br><br>'
			else:
				text = '--'
		return text



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
	data ={
		'error': [
			{
				'name': '职务管理-编辑职务',
				'info': [
					{
						'id': 'a2wrCqV1vY',
						'url': 'http://service.lbuilder.cn/iworks/report-fill/page',
						'method': 'POST',
						'contentList': [
							{
								'key': 'data_items_name',
								'expect': ['MonNet'],
								'actual': ['hubiao']
							}
						]
					},
					{
						'id': 'tkEWFdYvmV',
						'url': 'http://service.lbuilder.cn/iworks/report-fill/page',
						'method': 'POST',
						'contentList': [
							{
								'key': 'data_items_name',
								'expect': ['MonNet'],
								'actual': ['hubiao']
							}
						]
					},
					{
						'id': '4Dzh6gfFRD',
						'url': 'http://service.lbuilder.cn/iworks/report-fill/page',
						'method': 'POST',
						'contentList': [
							{
								'key': 'data_items_name',
								'expect': ['MonNet'],
								'actual': ['hubiao']
							}
						]
					},
					{
						'id': 'rkFIvuAeLb',
						'url': 'http://service.lbuilder.cn/iworks/report-template/page',
						'method': 'POST',
						'contentList': [
							{
								'key': 'data_items_fillProcess_应填_num',
								'expect': [2, 1],
								'actual': [0, 1]
							},
							{
								'key': 'data_items_fillProcess_已填_num',
								'expect': [1, 0],
								'actual': [3, 0]
							}
						]
					}
				],
				'moduleName': 'Center模块'
			}
		],
		'moduleNameList': ['Center模块'],
		'moduleCaseTotal': [1]
	}

	ReportUtil().createReport(data)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/