#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/15 20:00
# @Author  : hubiao
import os

import chevron
from cleo import Command as BaseCommand
from datetime import datetime

from luban_common.operation import yaml_file
from ..global_map import Global_Map
from pathlib2 import Path
from ..console.analysis_swagger import AnalysisSwaggerJson


class SwaggerCommand(BaseCommand):
    """
    Swagger generates file interfaces

    swagger
        {swagger-url-json : Swagger URL address, must be a JSON address, required parameter}
        {project-directory : Interface project name, required parameters}
        {--p|project=? : Project name, which merges the project name and interface address into a new interface address (the Resource field in the interface file), optional}
    """

    def handle(self):
        excludes = ["None", "null", "false", "true", "undefined"]
        if self.option("project") is not None:
            if self.option("project").lower() in [exclude.lower() for exclude in excludes]:
                raise RuntimeError(
                    f'Destination <fg=yellow>{self.option("project")}</> '
                    "project option cannot be None,null,false,true,undefined"
                )
        Global_Map().set("prompt", False)
        Global_Map().set("replace", False)
        js = AnalysisSwaggerJson(self.argument("swagger-url-json"))
        data = js.analysis_json_data()
        if not isinstance(data,dict):
            raise RuntimeError(
                f"Destination <fg=yellow>{self.argument('swagger-url-json')}</> "
                "The data must be dict"
            )
        swagger_directory = self.argument("project-directory").split("/")[1:] if self.argument("project-directory").startswith("/") else self.argument("project-directory").split("/")
        for case in range(len(swagger_directory)):
            if len(swagger_directory[case]) == 0:
                continue
            if not swagger_directory[case].encode( 'UTF-8' ).isalpha():
                raise RuntimeError(
                    f'Destination <fg=yellow>{self.argument("project-directory")}</> '
                    "The swagger directory can only contain letters"
                )
        replace_text = yaml_file.get_yaml_data(f"{os.path.dirname(os.path.realpath(__file__))}/../config/parameConfig.yaml")
        for key, values in data.items():
            if "groups" in key:
                path = Path.cwd() / f'swagger/{"/".join(swagger_directory)}'
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
                            self.line(f"Destination <fg=yellow>{path}</> is not empty")
                            break
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
                                interfaces = chevron.render(mustache, {**group, **{"project":self.option("project")}})
                            else:
                                interfaces = chevron.render(mustache, {**group, **{"project": ''.join(["/",self.option("project")])}})
                        else:
                            interfaces = chevron.render(mustache, group)
                        interface_file = path/f"{group['file_name']}.py"
                        interfaces = interfaces.replace("'$", "").replace("$'", "").replace("$", "")
                        for match in replace_text.get("matchs"):
                            interfaces = interfaces.replace(match.get("match"), match.get("replace"))
                        with interface_file.open("w", encoding="utf-8") as f:
                            f.write(interfaces)
                        self.line("Created file: <fg=green>{}</>".format(interface_file))
                self.line("<fg=green>Successfully generate</>")

