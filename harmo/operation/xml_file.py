#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2019/1/7 19:52
# @Author  : hubiao
# @File    : xml_file.py
from pathlib2 import Path

from harmo.base_utils import file_is_exist

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

class xml:
    def pytestXml(self,file_path):
        try:
            file = file_is_exist(file_path)
            if Path(file).suffix == ".xml":
                # 打开XML文档
                tree = ET.parse(file)
                # 获得文档根节点
                root = tree.getroot()
                # 获取当前节点标签的所有属性信息，并会以字典形式输出
                result = root.attrib
                return result
            else:
                raise RuntimeError("The file format must be xml")

        except BaseException as e:
            print("解析失败！", str(e))

if __name__ == "__main__":
    xml = xml()
    result = xml.pytestXml(file_path='../../data/ProjectCatalog.xml')
    print(result)
    print(result["text"])