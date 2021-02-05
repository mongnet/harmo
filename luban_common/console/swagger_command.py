#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/15 20:00
# @Author  : hubiao
import os

import chevron
from cleo import Command as BaseCommand
from datetime import datetime

from ..global_map import Global_Map
from pathlib2 import Path
from ..console.analysis_swagger import AnalysisSwaggerJson


class SwaggerCommand(BaseCommand):
    """
    Swagger generates file interfaces

    swagger
        {swagger-url-json : Swagger url地址，必须是json地址，必填参数}
        {directory : 生成到指定的目录，一般为项目名称，必填参数}
        {--p|project=? : 项目名，会把项目名和接口地址合并成新的接口地址，接口文件中的 resource 字段，可选参数}
    """

    def handle(self):
        # 提示
        Global_Map().set("prompt", False)
        # 覆盖
        Global_Map().set("replace", False)
        js = AnalysisSwaggerJson(self.argument("swagger-url-json"))
        data = js.analysis_json_data()
        if not isinstance(data,dict):
            raise FileExistsError("数据类型错误，传入的数据必须为dict")
        for key, values in data.items():
            if "groups" in key:
                path = Path.cwd() / Path(self.argument("directory"))
                if path.exists():
                    if list(path.glob("*")):
                        self.line("")
                        question = (f"{path} is not empty, continue to generate?")
                        # Folder or file already exists, do you want to replace it?
                        if self.confirm(question, True):
                            self.line("<fg=green>Generate</>")
                        else:
                            # Directory already exists. Aborting.
                            self.line("")
                            self.line("Destination <fg=yellow>{}</> is not empty".format(path))
                            break
                path.mkdir(mode=0o777, parents=True, exist_ok=True)
                package_init = path / "__init__.py"
                package_init.touch(exist_ok=True)
                current_path = os.path.dirname(os.path.realpath(__file__))
                # 是否覆盖文件
                for group in values:
                    if not Global_Map().get("prompt") and not Global_Map().get("replace") and list(path.glob(f"{group['file_name']}.py")):
                        self.line("")
                        question = (f"Some file already exists, do you want to replace it?")
                        if self.confirm(question, True):
                            self.line("<fg=green>Replace</>")
                            Global_Map().set("prompt",1)
                        else:
                            Global_Map().set("replace",1)
                    if Global_Map().get("replace") and list(path.glob(f"{group['file_name']}.py")):
                        # file already exists.
                        self.line(f"<fg=red>{group['file_name']}.py</> file already exists, Don't replace")
                        continue
                    group = {**group,**{"generated_time":datetime.now().strftime('%Y/%m/%d %H:%M')}}
                    # 生成文件
                    with open(f'{current_path}/../config/interface.mustache', 'r') as mustache:
                        if self.option("project"):
                            # 添加项目名称
                            if self.option("project").startswith("/"):
                                interfaces = chevron.render(mustache, {**group, **{"project":self.option("project")}})
                            else:
                                interfaces = chevron.render(mustache, {**group, **{"project": ''.join(["/",self.option("project")])}})
                        else:
                            interfaces = chevron.render(mustache, group)
                        interface_file = path/f"{group['file_name']}.py"
                        with interface_file.open("w", encoding="utf-8") as f:
                            f.write(interfaces.replace("'$","").replace("$'","").replace("$",""))
                        self.line("Created file: <fg=green>{}</>".format(interface_file))
                self.line("<fg=green>Successfully generate</>")

