#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/15 20:00
# @Author  : hubiao
import os
import re

import chevron
from cleo.commands.command import Command
from cleo.helpers import argument, option
from datetime import datetime

from luban_common import base_utils

from luban_common.operation import yaml_file
from ..global_map import Global_Map
from pathlib2 import Path
from ..console.analysis_swagger import AnalysisSwaggerJson

class SwaggerCommand(Command):
    name = "swagger"
    description = "通过swagger生成接口方法"
    arguments = [
        argument(
            "swagger-url-json",
            description="swagger 的url或本地json文件（必须是json格式），必填"
        ),
        argument(
            "project-directory",
            description="生成的接口方法存放的目录，通常为接口项目目录，必填"
        )
    ]
    options = [
        option(
            "project",
            "p",
            description="项目名或 basePath 地址，如指定会替换basePath地址并把他和接口地址合并成新的接口地址（接口文件中的 resource 字段），可选",
            flag=False
        ),
        option(
            "header",
            "H",
            description="请求头信息",
            flag=False,
            default=None,
            multiple=True
        )
    ]

    def handle(self):
        excludes = ["None", "null", "false", "true", "undefined"]
        if self.option("project") is not None:
            if self.option("project").lower() in [exclude.lower() for exclude in excludes]:
                raise RuntimeError(
                    f'Destination <fg=yellow>{self.option("project")}</> '
                    "project option cannot be None,null,false,true,undefined"
                )
        swagger_directory = self.argument("project-directory").split("/")[1:] if self.argument("project-directory").startswith("/") else self.argument("project-directory").split("/")
        for case in range(len(swagger_directory)):
            if len(swagger_directory[case]) == 0:
                continue
            ret = re.findall(f'[:*?"<>|]',swagger_directory[case])
            if ret:
                raise RuntimeError(
                    f'Destination <fg=yellow>{self.argument("project-directory")}</> '
                    "The swagger directory Contains illegal characters, "
                    f"Illegal characters: {ret}"
                )
        replace_text = yaml_file.get_yaml_data(f"{os.path.dirname(os.path.realpath(__file__))}/../config/parameConfig.yaml")
        swaggerIsEmpty = True
        __headers = self.option("header")
        __header = {}
        if __headers:
            for h in __headers:
                __tem_header = h.split(":",1)
                if len(__tem_header) == 2 and len(__tem_header[0].strip()) > 0 and len(__tem_header[1].strip()) > 0:
                    __header.update({__tem_header[0].strip():__tem_header[1].strip()})
        js = AnalysisSwaggerJson()
        dataList = js.analysis_json_data(swaggerUrl=self.argument("swagger-url-json"),header=__header)
        for data in dataList:
            if not isinstance(data,dict):
                raise RuntimeError(
                    f"Destination <fg=yellow>{self.argument('swagger-url-json')}</> "
                    "The data must be dict"
                )
            # Generate swagger script
            Global_Map().set("prompt", False)
            Global_Map().set("replace", False)
            for key, values in data.items():
                if "groups" in key:
                    path = Path.cwd() / f'swagger/{"/".join(swagger_directory)}'
                    if path.exists():
                        if list(path.glob("*")) and swaggerIsEmpty:
                            self.line("")
                            question = (f"{path} is not empty, continue to generate?")
                            # Folder or file already exists, do you want to replace it?
                            if self.confirm(question, True):
                                self.line("<fg=green>Generate</>")
                                swaggerIsEmpty = False
                            else:
                                # Directory already exists. Aborting.
                                self.line("")
                                self.line(f"Destination <fg=yellow>{path}</> is not empty")
                                break
                    else:
                        swaggerIsEmpty = False
                    path.mkdir(mode=0o777, parents=True, exist_ok=True)
                    package_init = path / "__init__.py"
                    package_init.touch(exist_ok=True)
                    # generate __init__.py
                    if Path.cwd().glob(f"swagger/__init__.py"):
                        swagger_init = Path.cwd() / "swagger" / "__init__.py"
                        swagger_init.touch(exist_ok=True)
                    for cas in range(len(swagger_directory)):
                        if Path.cwd().glob(f'swagger/{Path("/".join(swagger_directory[0:cas + 1]))}/__init__.py'):
                            directory_init = Path.cwd() / "swagger" / Path(
                                "/".join(swagger_directory[0:cas + 1])) / "__init__.py"
                            directory_init.touch(exist_ok=True)
                    current_path = os.path.dirname(os.path.realpath(__file__))
                    # overlay file
                    for group in values:
                        if len(group['file_name']) < 1:
                            RuntimeError(f"File name cannot be empty")
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
                        # generate file
                        with open(f'{current_path}/../config/interface.mustache', 'r') as mustache:
                            if self.option("project"):
                                # add project
                                if self.option("project").startswith("/"):
                                    base_utils.recursion_replace_dict_key_value(group,{"interface_basePath": self.option("project")})
                                else:
                                    base_utils.recursion_replace_dict_key_value(group,{"interface_basePath": ''.join(["/",self.option("project")])})
                            interfaces = chevron.render(mustache, group)
                            interface_file = path/f"{group['file_name']}.py"
                            interfaces = interfaces.replace("'$", "").replace("$'", "").replace("$", "")
                            for match in replace_text.get("matchs"):
                                interfaces = interfaces.replace(match.get("match"), match.get("replace"))
                            with interface_file.open("w", encoding="utf-8") as f:
                                f.write(interfaces)
                            self.line("Created file: <fg=green>{}</>".format(interface_file))
                    self.line("")
                    self.line("<fg=green>Successfully generate interface</>")

