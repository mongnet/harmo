#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/15 20:00
# @Author  : hubiao
import os

import chevron
from cleo import Command as BaseCommand
from luban_common.global_map import Global_Map
from pathlib2 import Path
from ..console.analysis_swagger import AnalysisSwaggerJson
from datetime import datetime


class CasesCommand(BaseCommand):
    """
    Test cases generated from Swagger need to be executed in the root of the project. Both the Swagger interface method and the corresponding testcases are generated in the corresponding 'Swagger' and 'testcases' directories

    swaggerCase
        {swagger-url-json : Swagger URL address, must be a JSON address, required parameter}
        {project-directory : Interface project name, required parameters}
        {case-directory : Use case classification, required parameters}
        {--p|project=? : Project name, which merges the project name and interface address into a new interface address (the Resource field in the interface file), optional}
    """

    def handle(self):
        Global_Map().set("prompt", False)
        Global_Map().set("replace", False)
        js = AnalysisSwaggerJson(self.argument("swagger-url-json"))
        data = js.analysis_json_data()
        if not isinstance(data,dict):
            raise RuntimeError(
                f"Destination <fg=yellow>{self.argument('swagger-url-json')}</> "
                "The data must be dict"
            )
        if self.argument("project-directory").find("/") != -1:
            raise RuntimeError(
                f"Destination <fg=yellow>{self.argument('project-directory')}</> "
                "The directory cannot contain /"
            )
        for key, values in data.items():
            if "groups" in key:
                path = Path.cwd() /"swagger"/ Path(self.argument("project-directory"))
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
                    testcases_init = Path.cwd() /"swagger"/ "__init__.py"
                    testcases_init.touch(exist_ok=True)
                current_path = os.path.dirname(os.path.realpath(__file__))
                # overlay file
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
                        with interface_file.open("w", encoding="utf-8") as f:
                            f.write(interfaces.replace("'$","").replace("$'","").replace("$",""))
                        self.line("Created file: <fg=green>{}</>".format(interface_file))
                self.line("<fg=green>Successfully generate swagger</>")
                self.line("")
        Global_Map().set("prompt", False)
        Global_Map().set("replace", False)
        directory = self.argument("case-directory")[1:] if self.argument("case-directory").startswith("/") else self.argument("case-directory")
        case_directory = directory.split('/')
        for key, values in data.items():
            if "groups" in key:
                path = Path.cwd() / f"testcases/{directory}"
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
                if Path.cwd().glob(f"testcases/__init__.py"):
                    testcases_init = Path.cwd() /"testcases"/ "__init__.py"
                    testcases_init.touch(exist_ok=True)
                for cas in range(len(case_directory)):
                    if Path.cwd().glob(f'testcases/{Path("/".join(case_directory[0:cas + 1]))}/__init__.py'):
                        directory_init = Path.cwd() /"testcases" / Path("/".join(case_directory[0:cas + 1])) /"__init__.py"
                        directory_init.touch(exist_ok=True)
                current_path = os.path.dirname(os.path.realpath(__file__))
                # overlay file
                for group in values:
                    if not Global_Map().get("prompt") and not Global_Map().get("replace") and list(path.glob(f"test_{group['file_name']}.py")):
                        self.line("")
                        question = (f"Some file already exists, do you want to replace it?")
                        if self.confirm(question, True):
                            self.line("<fg=green>Replace</>")
                            Global_Map().set("prompt",1)
                        else:
                            Global_Map().set("replace",1)
                    if Global_Map().get("replace") and list(path.glob(f"test_{group['file_name']}.py")):
                        # file already exists.
                        self.line(f"<fg=red>test_{group['file_name']}.py</> file already exists, Don't replace")
                        continue
                    group = {**group,**{"generated_time":datetime.now().strftime('%Y/%m/%d %H:%M'),"project-directory":self.argument("project-directory")}}
                    # generate file
                    with open(f'{current_path}/../config/cases.mustache', 'r') as mustache:
                        interfaces = chevron.render(mustache, group)
                        interface_file = path/f"test_{group['file_name']}.py"
                        with interface_file.open("w", encoding="utf-8") as f:
                            f.write(interfaces.replace("'$","").replace("$'","").replace("$",""))
                        self.line("Created file: <fg=green>{}</>".format(interface_file))
                self.line("<fg=green>Successfully generate cases</>")
