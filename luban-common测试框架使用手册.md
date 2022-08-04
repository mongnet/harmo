# 测试框架使用手册 V1.0.0

## 一、介绍

luban-common 是一款面向鲁班内部的 HTTP(S) 协议的通用测试框架。他的设计理念是把所有接口看成一个个的模块，像搭积木一样，把相关接口进行组装，行成场景测试用例；说到场景用例那肯定有单接口测试，单接口测试会直接通过框架来生成，无需人工参与或少量参与即可完成，我们的目标是把可标准化、重复性的工作让机器来完成，让测试人员更多的关注场景和其它异常类测试。

### 1.1 为什么创建这套框架

有如下几方面原因致使我们创建这个框架：

**统一技术栈**：确定框架选型，确定人员技术栈，不用纠结用什么框架，学什么语言

**方便推广**：技术、经验可更好的积累和传播

**方便管理**：有问题和需求可统一实现和修改，主框架调整不影响已有接口和数据，目录结构统一后，其它人员介入也变得简单

**技术可控**：世面上是有很多框架，但要找到适合自己项目的几乎没有，或多或少都要进行部分修改，二次开发的工程量也不小，我们可以基于一个比较成熟的开源框架开发和优化想要的功能，由于功能都是自己开发和修改的，有问题有需求能快速调整。



### 1.2 核心特性

- 基于 `pytest` 扩展，继承 `pytest` 的全部特性，测试前后支持完善的 hook 机制

- 继承 `Requests` 的全部特性，轻松实现 HTTP(S) 的各种测试需求

- 采用 `YAML` 的形式保存环境配置，可动态指定配置文件

- 支持完善的测试用例分层机制，充分实现复用

- 响应结果支持丰富的校验机制

- 通过 `luban new` 创建项目脚手架命令，可快速构建一个完整的项目目录结构

- 通过 `luban swagger` 生成 `swagger` 接口命令，可快速生成接口方法

- 通过 `luban swaggerCase` 生成测试用例命令，可快速生成简单的测试用例

  

## 二、安装

### 2.1 安装方式

PyPI安装(版本稳定后会托管到PyPI上)

```python
pip install luban-common
```

本地安装

```python
pip install luban_common-0.5.27-py3-none-any.whl
```

从git安装

```python
pip install git+https://github.com/mongnet/luban_common@master
```

### 2.2 版本升级

假如你之前已经安装过了 luban-common，现在需要升级到最新版本，那么你可以使用 `-U` 参数。

```python
pip install -U luban-common
pip install -U git+https://github.com/mongnet/luban_common@master
或
pip install -U luban_common-0.5.27-py3-none-any.whl
```

### 2.3 安装验证

运行如下命令，若正常显示版本号，则说明 luban-common 安装成功

```
C:\Users\admin>luban -V
Luban version 0.4.0
```



## 三、框架结构

luban-common 框架项目结构如下：

```python
├─config
│   ├─blacklist.yaml
│   ├─default_parame.yaml
│   ├─global_default.yaml
│   └─interface.mustache
├─console
│   ├─analysis_swagger.py
│   ├─application.py
│   ├─new_command.py
│   └─swagger_command.py
├─msg
│   ├─weixin.py
│   └─youdu.py
├─operation
│   ├─excel_file.py
│   ├─ini_file.py
│   ├─xml_file.py
│   └─yaml_file.py
├─base_assert.py
├─base_requests.py
└─base_utils.py
```

> **config**：中放的是一些配置文件

> **blacklist.yaml**：白名单列表，在生成swagger接口时，会过滤这些字段（不把这些参数加放到方法上）

> **default_parame.yaml**：默认参数，在生成swagger接口时，会把匹配到的参数设置上默认值

> **global_default.yaml**：其它默认配置项

> **interface.mustache**：模生成swagger接口时的板文件，一般不需要动

> **console**：命令行工具的一些实现方法，现实现了新建项目、生成swagger方法二个功能，这块可以不用了解

> **msg**：消息模块

> **weixin.py**：企业微信消息模块

> **youdu.py**：有度消息模块

> **operation**：封装了四种文通用件的操作方法

> **excel_file.py**：excel 文件的操作方法

> **ini_file.py**：ini 文件的操作方法

> **xml_file.py**：xml 文件的操作方法

> **yaml_file.py**：yaml 文件的操作方法

> **base_assert.py**：封装了一些通用断言，方便后续调整

> **base_requests.py**：封装了requests库

> **base_utils.py**：封装了一些工具方法，比如：获取文件名、MD5、生成手机号、生成邮箱等



### 3.1 msg 模块 

消息模块，封装了 `企业微信机器人`消息推送功能

#### 3.1.1 企业微信消息

当前微信机器人消息封装了5种消息格式，分别为 `文本`、`卡片`、`markdown`  、`发送图片`  、`发送文件`  消息，可针对不同场景使用对应消息，消息样式如下

![image-20210724192416549](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20210724192416549.png)



##### 3.1.1.1 文本消息

send_message_text() 函数可发送文本消息，需要传三个参数，调用方式如下：

```python
send.send_message_text(hookkey,content,mentioned_mobile_list)
```

> **hookkey**：webhook的key

> **content**：消息内容

> **mentioned_mobile_list**：手机号列表，提醒手机号对应的群成员(@某个成员)，例如：["13800001111"]

例：

```python
from luban_common.msg.robot import WeiXin

send = WeiXin()
send.send_message_text(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",content="发现一个公众号：彪哥的测试之路，很不错。",mentioned_mobile_list=["13916829124"] )
```



##### 3.1.1.2 卡片消息

send_message_textcard() 函数可发送卡片消息，传三个参数，调用方式如下：

```python
send.send_message_textcard(,hookkey,title,url,content,picurl)
```

> **title**：消息标题

> **content**：消息内容

> **hookkey**：webhook的key

> **title**：消息标题

> **url**：点击后跳转的链接

> **picurl**：图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。



例：

```python
from luban_common.msg.robot import WeiXin

send = WeiXin()
send.send_message_card(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",title="测试开发",content="发现一个公众号：彪哥的测试之路，很不错，可以点击查看更多跳转到网页",url="http://")
```



##### 3.1.1.3 markdown消息

send_message_markdown() 函数可发送 markdown 消息，需要传二个参数，调用方式如下：

```python
send.send_message_markdown(hookkey,content)
```

> **content**：消息内容

> **hookkey**：webhook的key

例：

```python
from luban_common.msg.robot import WeiXin

send = WeiXin()
markdown_content = """
                        ># 这是`markdown`消息
                        >事　项：<font color=\"info\">公众号</font>
                        >组织者：@彪哥的测试之路
                        >
                        >会议室：<font color=\"info\">上海</font>
                        >日　期：<font color=\"warning\">2020年8月18日</font>
                        >时　间：<font color=\"comment\">上午9:00-11:00</font>
                        >
                        >请**准时**参加会议。
                        >
                        >如需修改会议信息，请点击：[这里还可以有连接](https://work.weixin.qq.com)"""
send.send_message_markdown(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",content=markdown_content)
```



##### 3.1.1.4 发送图片

send_image() 发送图片，最大不能超过2M，支持JPG,PNG格式，调用方式如下：

```python
send.send_image(hookkey,file)
```

> **imgBase64**：图片（base64编码）最大不能超过2M，支持JPG,PNG格式

> **hookkey**：webhook的key

例：

```python
from luban_common.msg.robot import WeiXin

send = WeiXin()
send.send_image(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",file="../../data/20201222101200.png")
```



##### 3.1.1.5 发送文件

send_file() 发送其它文件，调用方式如下：

```python
send.send_file(hookkey,file)
```

> **file**：文件相对路径

> **hookkey**：webhook的key

例：

```python
from luban_common.msg.robot import WeiXin

send = WeiXin()
send.send_file(hookkey="ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42",file="weixin.py")
```





------

### 3.2 operation 模块

操作模块、封装了对 `excel`、`xml`、`ini`、`yaml` 文件的操作方法

#### 3.2.1 excel文件

excel操作方法比较简单，暂时未做过多的封装，共封装四个方法，`获取总行数`、`获取总列数`、`获取指定行`、`获取指定单位格`

##### 3.2.1.1 获取总行数

get_lines() 可获取excel表的的总行数，调用格式如下：

```python
from luban_common.operation.excel_file import OperationExcel

oper = OperationExcel(file_path="../../data/Quality_check_lib.xls",sheetID=0)
oper.get_lines()
```



##### 3.2.1.2 获取总列数

get_cells() 可获取excel表的的总列数，调用格式如下：

```python
from luban_common.operation.excel_file import OperationExcel

oper = OperationExcel(file_path="../../data/Quality_check_lib.xls",sheetID=0)
oper.get_cells()
```



##### 3.2.1.3 获取指定行

get_line(number) 可获取excel表的指定行，需要传一个参数，表示要取第几行的数据，调用格式如下：

```python
from luban_common.operation.excel_file import OperationExcel

oper = OperationExcel(file_path="../../data/Quality_check_lib.xls",sheetID=0)
oper.get_line(0)
```

> **number**：指定行数，从0开始



##### 3.2.1.4 获取指定单元格

get_cell(number1,number2) 可获取指定单元格数据，需要传二个参数，单元格的x和y轴坐标，调用格式如下：

```python
from luban_common.operation.excel_file import OperationExcel

oper = OperationExcel(file_path="../../data/Quality_check_lib.xls",sheetID=0)
oper.get_cell(0,0)
```

> **number1**：指定行数，从0开始

> **number2**：指定行数，从0开始



#### 3.2.2 xml文件

待完善...



#### 3.2.3 ini文件

配置管理，现实现了对 ini 文件的读取和写入

##### 3.2.3.1 获取指定节点配置

getConfig() 获取指定节点下的项目信息，调用格式如下：

```python
from luban_common.operation.ini_file import ManageConfig

cf = ManageConfig(file_path='../../data/intranet.ini')
rf = cf.getConfig(section='openapi')
rf["openapiurl"]
```

> **file_path**：文件路径

> **section**：节点名



##### 3.2.3.2 获取全部节点配置

getAllConfig() 获取全部节点配置信息，调用格式如下：

```python
from luban_common.operation.ini_file import ManageConfig

cf = ManageConfig(file_path='../../data/intranet.ini')
allconf = cf.getAllConfig()
allconf['openapi']["openapiurl"]
```

> **file_path**：文件路径



##### 3.2.3.3 向指定节点写配置

writeConfig() 写入配置信息到指定的节点，调用格式如下：

```python
from luban_common.operation.ini_file import ManageConfig

cf = ManageConfig(file_path='../../data/intranet.ini')
#写入信息
cf.writeConfig(section='pds',key='cas',value='http://cas.com')
```

> **file_path**：文件路径

> **section**：节点名

> **key**：配置的key信息

> **value**：配置的value信息



#### 3.2.4 yaml文件

yaml操作模板当前只支持获取yaml数据功能，其它功能未实现

##### 3.2.4.1 获取ymal文件数据

get_yaml_data() 传入yaml文件路径，返回yaml文件内的数据，返回类型为dcit，调用格式如下：

```python
from luban_common.operation.yaml_file import get_yaml_data

get_yaml_data(file_path='../../data/config.yaml')
```

> **file_path**：文件路径



------

### 3.3 base_requests.py

封装了 requests 库，处理了单点登录时302跳转问题



------

### 3.4 base_assert.py

封装了大部分assert方法，建议用这里面的方法来进行断言，方便后续基于断言的一些其它应用

#### 3.4.1 校验status_code和code

assert_all_code()函数可校验接口的http响应值和接口code值，调用格式如下：

```python
Assertions.assert_all_code(response, expected_http_code, expected_code)
```

> **response**：响应数据

> **expected_http_code**：预期的http状态码

> **expected_code**：预期code状态码

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_all_code(response,200,200)
```

注：推荐使用 assert_code()



#### 3.4.2 校验等于预期值

assert_equal_value()函数可校实际值是否等于验预期值，调用格式如下：

```python
Assertions.assert_equal_value(reality_value, expected_value)
```

> **reality_value**：实际值

> **expected_value**：预期值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_equal_value(response["code"][0],200)
```



#### 3.4.3 校验数据集中指定key的值

assert_assign_attribute_value()函数可校验接口的http响应值和接口code值，只支持 list 、str，调用格式如下：

```python
Assertions.assert_assign_attribute_value(data, key, expected_value)
```

> **data**：校验的data

> **key**：预期key

> **expected_value**：预期值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_assign_attribute_value(response,"key_name","胡彪")
```



#### 3.4.4 校验数据集中存在预期值

assert_in_value()函数可校验一组数据中是否存在指定的值，只支持 list 、str，调用格式如下：

```python
Assertions.assert_in_value(data, expected_value)
```

> **data**：校验的data

> **expected_value**：预期值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_in_value(data,200)
```



#### 3.4.5 校验字典中存在预期key

assert_in_key()函数可校验字典中存在指定的key，只支持 dict，调用格式如下：

```python
Assertions.assert_in_key(data, key)
```

> **data**：校验的data

> **key**：预期key

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_in_key(data,"key_name")
```



#### 3.4.6 校验数据集中不存在预期值

assert_not_in_value()函数可校验一组数据中是否不存在指定的值，支持 list 、str，调用格式如下：

```python
Assertions.assert_not_in_value(data, expected_value)
```

> **data**：校验的data

> **expected_value**：预期值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_not_in_value(data,"hubiao")
```



#### 3.4.7 校验字典中不存在预期key

assert_not_in_key()函数可校验字典中不存在指定的key，只支持 dict，调用格式如下：

```python
Assertions.assert_not_in_key(data, expected_key)
```

> **data**：校验的data

> **expected_key**：预期key

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_not_in_key(data,"key_name")
```



#### 3.4.8 校验以预期值开头

assert_startswith()函数可校验以预期值开头，只支持字符串，调用格式如下：

```python
Assertions.assert_startswith(response, expected_value)
```

> **data**：校验的data

> **expected_value**：预期值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_startswith(data["url"],"http://")
```



#### 3.4.9 校验以预期值结尾

assert_endswith()函数可校验以预期值结尾，只支持字符串，调用格式如下：

```python
Assertions.assert_endswith(response, expected_value)
```

> **data**：校验的data

> **expected_value**：预期值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_endswith(data["url"],"163.com")
```



#### 3.4.10 校验是否等于None

assert_isNone()函数可校验指定的值是否为None，调用格式如下：

```python
Assertions.assert_isNone(reality_value)
```

> **reality_value**：实际值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_isNone(data["name"])
```



#### 3.4.11 校验时间小于预期

assert_time()函数可校验实际时间小于预期时间，调用格式如下：

```python
Assertions.assert_time(reality_time, expected_time)
```

> **reality_time**：预期的http状态码

> **expected_time**：预期code状态码

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_time(reality_time,expected_time)
```



#### 3.4.12 校验字典或列表是否相等

assert_dictOrList_eq()函数可校验字典和列表是否相等，调用格式如下：

```python
Assertions.assert_dictOrList_eq(reality, expected)
```

> **reality**：实际值

> **expected**：预期值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_dictOrList_eq(dict1,dict2)
```



#### 3.4.13 校验列表中是否有重复项

assert_list_repetition()函数可校验列表中是否有重复项，调用格式如下：

```python
Assertions.assert_list_repetition(list)
```

> **list**：实际值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_list_repetition(list)
```



#### 3.4.14 校验code或status_code

assert_code()函数可校验response响应体中的code或status_code状态码，调用格式如下：

```python
Assertions.assert_code(response, reality_code, expected_code)
```

> **response**：响应数据

> **reality_code**：预期的code状态码

> **expected_code**：实际code状态码

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_code(response, 200, 200)
```



#### 3.4.15 校验为空

assert_isEmpty()函数可校验传传入的数据是为空，当传入值为None、False、空字符串""、0、空列表[]、空字典{}、空元组()都会判定为空，调用格式如下：

```python
Assertions.assert_isEmpty(reality_value)
```

> **reality_value**：实际值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_isEmpty(reality_value)
```



#### 3.4.16 校验不为空

assert_isNotEmpty()函数可校验传传入的数据是不为空，当传入值为None、False、空字符串""、0、空列表[]、空字典{}、空元组()都会判定为空，调用格式如下：

```python
Assertions.assert_isEmpty(reality_value)
```

> **reality_value**：实际值

例：

```python
from luban_common.base_assert import Assertions

Assertions.assert_isNotEmpty(reality_value)
```



------

### 3.5 base_utils.py

封装了一些常用工具，比如获取md5、时间戳、文件名、文件大小、生成手机号等方法

#### 3.5.1 获取文件MD5

调用格式如下：

```python
getFileMD5(file_Path)
```

> **file_Path**：文件路径可以是相对路径，也可以是相对路径

例：

```python
from luban_common import base_utils

base_utils.getFileMD5("data/image/178k.png")
```



#### 3.5.2 获取文件大小

调用格式如下：

```python
getFileSize(file_Path)
```

> **file_Path**：文件路径可以是相对路径，也可以是相对路径

例：

```python
from luban_common import base_utils

base_utils.getFileSize("data/image/178k.png")
```



#### 3.5.3 获取文件名

调用格式如下：

```python
getFileName(file_Path)
```

> **file_Path**：文件路径可以是相对路径，也可以是相对路径

例：

```python
from luban_common import base_utils

base_utils.getFileName("data/image/178k.png")
```



#### 3.5.4 判断文件是否存在

调用格式如下：

```python
file_is_exist(file_Path)
```

> **file_Path**：文件路径可以是相对路径，也可以是相对路径

例：

```python
from luban_common import base_utils

base_utils.file_is_exist("data/image/178k.png")
```



#### 3.5.5 获取字符串的MD5

调用格式如下：

```python
getStrMD5(String)
```

> **String**：字符串

例：

```python
from luban_common import base_utils

base_utils.getStrMD5("公众号：彪哥的测试之路")
```



#### 3.5.6 字符串Sha1加密

调用格式如下：

```python
getStrSha1(String)
```

> **String**：字符串

例：

```python
from luban_common import base_utils

base_utils.getStrSha1("公众号：彪哥的测试之路")
```



#### 3.5.7 字符串转Base64编码

调用格式如下：

```python
ToBase64(String)
```

> **String**：字符串

例：

```python
from luban_common import base_utils

base_utils.ToBase64("公众号：彪哥的测试之路")
```



#### 3.5.8 Base64编码转字符串

调用格式如下：

```python
FromBase64(String)
```

> **String**：Base64编码的字符串

例：

```python
from luban_common import base_utils

base_utils.FromBase64("公众号：彪哥的测试之路")
```



#### 3.5.9 获取时间戳

调用格式如下：

```python
getUnix(date=None)
```

> **date**：传入的时间，格式为：'2017-05-09 18:31:22'，不传表单获取当前时间

例：

```python
from luban_common import base_utils

base_utils.getUnix()
```



#### 3.5.10 时间戳转时间

调用格式如下：

```python
UnixToTime(unix)
```

> **unix**：unix 时间戳

例：

```python
from luban_common import base_utils

base_utils.UnixToTime("1598586432000")
```



#### 3.5.11 获取近一个月的开始时间

获取近一个月的开始时间,比如今天是2016-12-15 12:25:00，那么返回的时间为2016-11-15 00:00:00，调用格式如下：

```python
getRecentMonthOfDay()
```

例：

```python
from luban_common import base_utils

base_utils.getRecentMonthOfDay()
```



#### 3.5.12 根据年月，返回当月天数

调用格式如下：

```python
calday(month, year)
```

> **month**：月份

> **year**：年份

例：

```python
from luban_common import base_utils

base_utils.calday(8,2015)
```



#### 3.5.13 执行CMD命令

调用格式如下：

```python
shell(cmd)
```

> **cmd：cmd**命令

例：

```python
from luban_common import base_utils

base_utils.shell("dir")
```



#### 3.5.14 生成随机字符串

调用格式如下：

```python
generate_random_str(randomlength=8)
```

> **randomlength**：随机字符串的长度，默认8位

例：

```python
from luban_common import base_utils

base_utils.generate_random_str()
```



#### 3.5.15 生成随机邮件地址

调用格式如下：

```python
generate_random_mail()
```

例：

```python
from luban_common import base_utils

base_utils.generate_random_mail()
```



#### 3.5.16 生成随机手机号

调用格式如下：

```python
generate_random_mobile()
```

> **file_Path**：文件路径可以是相对路径，也可以是

例：

```python
from luban_common import base_utils

base_utils.generate_random_mobile()
```



#### 3.5.17 通过数据生成字典

调用格式如下：

```python
ResponseData(indict)
```

> **indict**：接口响应的数据

> **return**：重新组装dict，之前嵌套的dict 会组装成”dict_dict“的形式

例：

```python
from luban_common import base_utils

base_utils.ResponseData(Response)
```



#### 3.5.18 搜索指定html标签内是否有指定文本

调用格式如下：

```python
Search_tag_text(url,tag,text)
```

> **url**：指定要检查的连接地址

> **tag**：指定要检查的html或xml标签，不要尖括号，如:h2

> **text**：指定要检查是否存在的文本

例：

```python
from luban_common import base_utils

base_utils.Search_tag_text(url="http://www.lubansoft.com",tag="h1",text="鲁班软件")
```



#### 3.5.19 获取时间差

调用格式如下：

```python
time_difference(start_time,end_time)
```

> **start_time**：开始时间

> **end_time**：结束时间

例：

```python
from luban_common import base_utils

base_utils.time_difference(start_time="2020-08-28 12:16:26.132615",end_time="2020-08-28 12:16:27.133615")
```



#### 3.5.20 jsonpath封装

调用格式如下：

```python
jpath(data,check_key,check_value=None,sub_key=None)
```

> **data**：需要获取的数据,类型必须是dict,否侧返回False

> **check_key**：检查key,例子中的functionKey

> **check_value**：检查value,辅助定位,例子中的'D-2'

> **sub_key**：检查子key,辅助定位,例子中的openStatus,当指定sub_key时,只返回sub_key对应的values,其它数据不返回

> **return**：返回一个list,当匹配不到数据时,返回False

例：

```python
from luban_common import base_utils
# jsonpath的写法
# jsonpath.jsonpath(data,$..[?(@.functionKey=='D-2')]..openStatus)

base_utils.jpath(data,check_key="functionKey",check_value="D-2",sub_key="openStatus")
```



### 3.6 Global_Map.py

全局变量函数，效果同 `global_cache` ，为什么有了 `global_cache` 还要再搞一个 Global_Map 了，因为 `global_cache` 是一个 fixture 函数，调用会有局限性，它只能在 fixture 函数或测试方法下调用，但实际场景有时候需要在其它函数中获取全局变量

#### 3.6.1 set 设置变量

设置变量到全局

调用格式如下：

```python
Global_Map.set(key, value)
```

> **key**：变量名称

> **value**：变量值

```python
from luban_common.global_map import Global_Map
Global_Map.set("username","hubiao")
```



#### 3.6.2 sets 设置多变量



调用格式如下：

```python
Global_Map.sets(**keys)
```

> **keys**：设置参数变量，支持

```python
from luban_common.global_map import Global_Map
Global_Map().sets(age=20,shcool="luban")
```



#### 3.6.3 del_key 删除指定变量

从全局变量中删除指定的变量

调用格式如下：

```python
Global_Map.del_key(key)
```

> **del_map**：需要删除的变量名

例：

```python
from luban_common.global_map import Global_Map
Global_Map.del_key("username")
```



#### 3.6.4 get 获取指定变量

从全局变量中获取指定的变量

调用格式如下：

```python
Global_Map.get(*args)
```

> **args**：需要获取的变量名，支持传元组

```python
from luban_common.global_map import Global_Map
Global_Map.get("username")
或
Global_Map().get('username','age')
```



## 四、框架能力

### 4.1 命令行工具

在 luban-common 安装成功后，系统中会新增如下命令：

`luban` ：核心命令，不可单独执行，必须携带参数

#### 4.1.1 新建项目

`luban new`：可通过 `new` 快速构建一个完整的项目目录结构，格式如下：

```python
luban new <name>
```

> **name**：项目名称

例：

```python
luban new centerApi
```



#### 4.1.2 通过Swagger生成接口文件

`luban swagger`：生成 `swagger` 接口命令，可快速生成接口方法，格式如下：

```python
luban swagger [-p [<...>]] <swagger-url-json> <project-directory>
```

> **swaggger-url-json**：swagger url 地址（必须要是json地址），必填参数

> **project-directory**：生成到指定的目录，必填参数

> **-p**：项目名或**basePath**地址，如指定会把他和接口地址合并成新的接口地址（接口文件中的 resource 字段），可选参数

例：生成接口文件到 `builder` 目录

```python
luban swagger http://192.168.13.197:8989/builder/v2/api-docs builder
```

例：生成接口文件到 `builder` 目录，且指定项目名为 `builder` 

```python
luban swagger http://192.168.13.197:8989/builder/v2/api-docs builder -p builder
```



#### 4.1.3 通过Swagger生成Case（推荐）

`luban swaggerCase`：生成测试用例命令，可快速生成简单测试用例，格式如下：
注：必须要在项目根目录下执行，会在对应的 `swagger` 和 `testcases` 目录下同时生成swagger接口方法和对应测试用例，如果指定了 `-p` 参数时会在 `testcases` 目录下生成对应的项目目录，并把测试用例放在里面

```python
luban swaggerCase [-p [<...>]] [-b] [-t <...>] [-s] <swagger-url-json> <project-directory> <case-directory>
```

> **swaggger-url-json**：swagger url 地址（必须要是json地址），必填参数

> **project-directory**：接口文件生成到的目录，一般为接口所属项目名称，会在 swagger 目录下生成指定的目录，也会做为 case 脚本中的引用文件路径，必填参数

> **case-directory**：用例生成到的目录，一般为用例分类，会在 testcases 目录下生成指定的目录，必填参数

> **-p**：项目名或**basePath**地址，如指定会把他和接口地址合并成新的接口地址（接口文件中的 resource 字段），可选参数

> **-b**：是否生成请求体，当接口有请求体时，默认生成请求体，可选项

> **-t**：生成的默认 token fixture 名称，默认为 `token`，可选参数

> **-s**：是否生成 swagger 脚本，默认生成 swagger 脚本，可选项

例：生成接口文件到 `builder` 目录，生成测试用例到 `center` 目录

```python
luban swaggerCase http://192.168.13.197:8989/builder/v2/api-docs builder center
```

例：生成接口文件到 `builder` 目录，生成测试用例到 `center` 目录，且指定项目名为 `builder` 

```python
luban swaggerCase http://192.168.13.197:8989/builder/v2/api-docs builder center -p builder
```



#### 4.1.4 发送微信消息

`luban weixin`：发送 `企业微信机器人` 消息命令，格式如下：

```python
luban weixin [-m <...>] [-t <...>] [-u <...>] [-o <...>] <hookkey> <content>
```

> **hookkey**：webhook连接中的key，必填参数

> **content**：消息内容，必填参数

> **-m**：手机号字符串，多个手机号用|隔开，如："13800138000|13700137000"，`text` 消息时有效，可选参数

> **-t**：消息标题，`card` 消息时有效，可选参数

> **-u**：点击后跳转的链接，`card` 消息时有效，可选参数

> **-o**：消息类型，三种消息类型`text`、`card`、`markdown`，可选参数，类型为 `markdown` 时，content 支持微信机器人官方支持的 `markdown` 语法



例：发送 `text` 消息

```python
luban weixin ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42 "彪哥的测试之路" -m "13916829124"
```

例：发送 `card` 消息

```python
luban weixin ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42 "彪哥的测试之路" -o "card" -t "测试开发" -u "http://demo.com"
```

例：发送 `markdown` 消息

```python
luban weixin ae0fdeb8-8b10-4388-8abb-d8ae21ab8d42 "# Hello！`彪哥的测试之路` " -o "markdown"
```



### 4.2 pytest.ini 配置

在项目根目录的 `pytest.ini` 文件中新增如下配置：

- `--lb-env`：环境配置文件，如 `dev`、`enterprise`、`preRelease`、`release`

  通过如下方式可在命令行中指定需要测试的环境配置

  ```python
  pytest --lb-env config/dev/config.yaml
  ```

- `--lb-driver`： UI自动化时使用的 driver 类型可从命令行或配置文件浏览器

  ```
  pytest --lb-driver firefox
  ```

- `--lb-base-url`： UI自动化或接口自动化时可从命令行或配置文件指定url地址

  ```
  pytest --lb-base-url http://www.lbuilder.cn
  ```

- `globalConf` ：通用配置文件，把固定不变的内容配置到这里

- `message_switch` ：有度消息通知开关，True为开启消息通知，Flase为关闭消息通知，默认为Flase

- `success_message` ： 成功时是否发送消息通知，默认为False

- 默认使用 `pytest-html` 插件生成报告，生成在当前执行目录的 `reports/report.html` 中

- 其它，指定了 `pytest` 的最低版本号为 `5.0` ，只到 `testcases`、 `testsuites` 下搜索用例



### 4.3 自定义fixture

在根目录的 `conftest.py` 中自定义了部分通用 `fixture` ，`fixture` 使用非常简单，只要把你想使用的 `fixture` 当参数传入对应的函数即可，`fixture`  可以当参数传入任意 `fixture`  或 测试方法中。

> **限制**：fixture 只能应用到 fixture 函数和测试用例上，其它函数不支持，但可以通过 fixture 函数传到其它函数实现数据共享

如下 `Send` 不是一个 `fixture` 函数，但他通过 `lbbv` 这个 `fixture` 实现了数据共享

```python
@pytest.fixture(scope="session")
def lbbv(iworks_app_cas, env_conf, global_cache):
    '''
    获取LBBV登录凭证
    :return:
    '''
    LBBV = base_requests.Send(global_cache.get("lbbv", False), env_conf, global_cache)
    yield LBBV
```



####  4.3.1 global_cache（推荐使用Global_Map）

全局缓存生命周期内产生的数据，主要用来解决数据依赖问题，比如 serverUrl 返回的项目地址、企业ID、项目部ID等通用数据

`global_cache` 提供了二个函数 `set`、`get`

##### 4.3.1.1 set 函数

用来设置需要缓存的数据，需要传二个参数，第一个参数是要设置的变量名称，第二个是要设置的数据，使用方式为：

```python
global_cache.set("rootid",rootid)
```

例：设置部署类型

```python
def getDeployType(self,global_cache):
    '''
    获取部署类型
    :return:
    '''
    resource = '/rs/centerLogin/deployType'
    response = self.CenterLogin.request('get', resource)
    Assertions().assert_code(response, response["status_code"], 200)
    deployType = response["Response_body"]
    global_cache.set('deployType', deployType)
```

当设置的变量名称已存在时，会进行覆盖操作。



##### 4.3.1.2 get 函数

用来获取缓存中的数据，需要传二个参数，第一个参数是要获取的变量名称，第二个是当获取的变量不存在时，默认返回什么，使用方式为：

```python
global_cache.get("builder", False)
```

例：获取企业id

```python
def switchCompany(self,global_cache):
    '''
    切换到指定企业
    :return:
    '''
    resource = f"/rs/casLogin/casLogin"
    body = {"epid": global_cache.get("epid", False)}
    response = self.casLogin.request('post', resource,body)
    Assertions.assert_code(response, response.get("status_code"), 200)
```



#### 4.3.2 env_conf

环境配置，合并了 `pytest.ini` 配置中 `--lb-env` 和 `globalConf` 文件中的 yaml 数据，使用字典的方式取值，使用方法为：

```python
env_conf.get("center").get("username")
```

例：获取产品id、header信息等

```python
def __init__(self,username,password,envConf,global_cache):
    self.cache = global_cache
    self.productId = envConf['iworksWebProductId']
    self.username = username
    self.password = password
    self.header = envConf["headers"]["json_header"]
    self.casLogin = base_requests.Send(envConf['pds'], envConf, global_cache=self.cache)
    self.epid = ''
```



#### 4.3.3 base_url

基础URL，当参数传入对应的函数即可，使用方法为：

```
web框架时使用，暂未
```



## 五、如何开始

### 5.1 创建项目

定位到需要创建项目的目录，如：`E:\Automation` ，然后在命令行中输入如下命令并回车

```python
luban new CenterAutomation
```

> **luban**：框架提供的命令入口

> **new**：创建项目命令

> **CenterAutomation**：项目名称，可修改为自己想要的名称

看到 `Successfully Created CenterAutomation` 表示项目创建成功，生成的项目结构如下

```python
├─business
│   └─__init__.py
├─config
│   ├─dev
│   │	└─config.yaml
│   ├─enterprise
│   │	└─config.yaml
│   ├─preRelease
│   │	└─config.yaml
│   ├─release
│   │	└─config.yaml
│   └─globalConf.yaml
├─data
├─reports
├─swagger
│   ├─__init__.py
│   └─builder
│  	    ├─org.py
│   	└─__init__.py
├─testcases
│   └─__init__.py
├─testsuites
│   ├─__init__.py
│   └─test_center_demo.py
├─utils
│   ├─__init__.py
│   └─utils.py
├─.gitignore
├─conftest.py
└─pytest.ini
```

> **business**：存放和当前业务相关代码的包

> **config**：配置文件夹

> **config.yaml**：默认生成4个环境的配置文件，对应 “开发”、“企业部署”、“预发布”、“正式”环境，可自己修改

> **globalConf.yaml**：全局配置文件，把不会随环境变化或固定的配置放这里，比如产品ID、请求头等

> **data**：存放测试数据的文件夹

> **reports**：默认测试报告存放文件夹

> **swagger**：通过 swagger 生成的接口方法存放在这里，每个项目一个子文件夹，`builder` 是一个演示项目，里面放的是相关接口

> **testcases**：测试用例文件夹，后面单接口用例都放这里面

> **testsuites**：测试集文件夹，test_center_demo.py 是一个测试的demo

> **utils**：工具类，用来存放自定义方法

> **.gitignore**：默认的git配置

> **conftest.py**：定义了大部分通用 `fixture`

> **pytest.ini**：pytest 配置文件，有些默认配置



### 5.2 执行测试

生成项目时默认会生成一份演示数据，进入 `CenterAutomation`  目录，执行测试有二种方式

**使用默认配置执行**：在命令行中输入如下命令，表示使用 `pytest.ini` 中的默认配置执行测试

```python
pytest
```

**指定环境执行**：在命令行中输入如下命令，表示使用 `dev` 环境配置执行测试

```python
pytest --lb-env config/dev/config.yaml
```



## 六、项目实战

框架默认已封装了 `运维后台`、`Center`、`iworksAPP`、`iworksWeb`、`OpenAPI`、`Bimapp`、`Mylubanweb`、`Bussiness`、`算量` 产品的登录功能，直接调用对应的 `fixture` 即可，目前登录功能封装在 `business/public_login.py` 文件中，后续会封装成pytes库，直接安装即可。

### 6.1 已封装产品

以 iworksweb 的进度计划为例，新建一个进度计划的测试用例。

#### 6.1.1 创建测试项目

新建一个名称为 iworksweb 的测试项目，在 CMD 中进入需要新建项目的目录，并输入命令如下

```
luban new iworksweb
```

看到 `Successfully Created iworksweb` 表示项目创建成功，生成的项目信息可参考“如何开始”，命令问题可查看“命令行工具”中命令的具体介绍

#### 6.1.2 通过swagger生成Case和接口方法

在 CMD 中进入 `iworksweb` 目录，然后找到要生成case的 swagger 接口地址，如下图

![image-20200901200704750](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20200901200704750.png)

> 第1个是swagger地址

> 第2个是swagger对应的json地址，这个地址就是我们需要的地址

在命令行中输入如下命令生成用例和接口方法

```python
luban swaggerCase http://192.168.13.246:8182/Plan/rs/swagger/swagger.json plan plan
```

![image-20210918145537477](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20210918145537477.png)

看到 `Successfully generate` 表示接口生成成功，我们用 pycharm 打开 `iworksweb` 项目，生成后的样子如下

![image-20210918153406255](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20210918153406255.png)

打开 `webPlanCalendar.py` 接口文件，看看生成的接口方法是什么样子，查看到 `setPlanCalenDar` 方法如下

![image-20210918153115409](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20210918153115409.png)

生成好的接口文件就可以直接在用例中调用了，调用方式和程序的类和方法调用方式一样，没有区别.

打开 `test_webPlanCalendar.py` 文件，看看生成的测试用例是什么样子，查看到 `test_setPlanCalenDar` 测试用例如下

![image-20210918153630759](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20210918153630759.png)

生成的测试用例中，默认会带有请求体（如果有），也可以不生成，只要在生成用例时添加-b 参数即可，可根据自己的实际情况确定是否生成



#### 6.1.3 修改测试用例文件





#### 6.1.4 修改账号配置文件

进入 config 目录，由于现在演示的这个项目是企业部署项目，所以我们进入了 enterprise 目录，我复制了一个 yaml 配置文件，命名为 202_config.yaml ，修改后的配置内容如下

![image-20200901210924480](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20200901210924480.png)

> **注意**：账号和地址信息必须要按默认文件的方式，建议大家在不了解运行机制时，只修改登录地址、用户名、密码，不要调整格式，如果需要添加信息，按已有样式添加即可



#### 6.1.5 修改pytest.ini配置文件

在 `iworksweb` 根目录找到 `pytest.ini` 文件，定位到 `--lb-env` 配置，把 `--lb-env` 配置修改为我们刚新建的 `Config/enterprise/202_config.yaml` 调整后的样子如下图

![image-20200901211726879](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20200901211726879.png)



#### 6.1.6 运行测试

进入 `testsuites` 目录，新建一个 `test_plan_add.py` 文件



### 6.2 未封装产品



#### 6.2.1 调整全局配置文件

一般情况不需要调整全局配置文件，由于之前没有把 iworksweb 的产品ID加进来，所以我们要加一下，进入 config 目录，找到 globalConf.yaml 配置文件，这是一个全局配置文件，把不变的配置都放在这里，比如产品ID，请求头信息等，加了一个 `iworksWebProductId: 192` 的配置，修改后的配置内容如下

![image-20200901212519261](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20200901212519261.png)

> **注意**：建议大家在不了解运行机制时，不要调整格式，如果要添加产品ID，按已有样式添加即可