#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/15 20:00
# @Author  : hubiao
import os

import chevron
from cleo import Command as BaseCommand
from ..global_map import Global_Map
from pathlib2 import Path
from ..console.analysis_swagger import AnalysisSwaggerJson


class SwaggerCommand(BaseCommand):
    """
    Swagger generates file interfaces

    swagger
        {swagger-url-json : Swagger url地址，必须是json地址}
        {--d|directory=? : 生成到指定的目录，可选参数，不指定时生成到当前目录}
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
                if self.option("directory"):
                    path = Path.cwd() / Path(self.option("directory")) / data["config"]["name_en"]
                else:
                    path = Path.cwd() / data["config"]["name_en"]
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
                    # 生成文件
                    with open(f'{current_path}/../config/interface.mustache', 'r') as mustache:
                        interfaces = chevron.render(mustache, group)
                        interface_file = path/f"{group['file_name']}.py"
                        with interface_file.open("w", encoding="utf-8") as f:
                            f.write(interfaces.replace("'$","").replace("$'","").replace("$",""))
                        self.line("Created file: <fg=green>{}</>".format(interface_file))
                self.line("<fg=green>Successfully generate</>")

