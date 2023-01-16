#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Created by hu on 2018/4/29

import xlrd
from pathlib2 import Path

from luban_common.base_utils import file_is_exist


class OperationExcel:
    '''
    操作excel
    '''
    def __init__(self,file_path,sheetID=0):
        '''
        :param file_path: excel文件路径
        :param sheetId: sheet ID
        '''
        if Path(file_path).suffix in [".xlsx",".xls"]:
            self.file = file_is_exist(file_path)
        else:
            raise RuntimeError("The file format must be excel")
        self.sheetID = sheetID
        self.data = self.get_data()

    def get_data(self):
        '''
        打开excel,获取指定sheet的数据
        :return: 返回sheet数据
        '''
        xl = xlrd.open_workbook(self.file)
        table = xl.sheet_by_index(self.sheetID)
        return table


    def get_lines(self):
        '''
        返回总行数
        :return:
        '''
        return self.data.nrows

    def get_cells(self):
        '''
        返回总列数
        :return:
        '''
        return self.data.ncols

    def get_line(self,rowx):
        '''
        返回指定行
        :return:
        '''
        return self.data.row(rowx)

    def get_cell(self,rowx,colx):
        '''
        返回指定列
        :return:
        '''
        return self.data.cell(rowx,colx)

if __name__ == '__main__':
    oper = OperationExcel(file_path="../../data/Quality_check_lib.xls",sheetID=0)
    print(oper.get_data())
    print(oper.get_data().nrows)
    print(oper.get_lines())
    print(oper.get_cells())
    print(oper.get_line(0))
    print(oper.get_cell(0,0))
