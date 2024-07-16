#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2020/2/15 20:00
# @Author  : hubiao
import os

from cleo.commands.command import Command
from cleo.helpers import argument, option

class NewCommand(Command):
    name = "new"
    description = "新建测试项目"
    arguments = [
        argument(
            "name",
            description="测试项目的名称，必填"
        )
    ]
    def handle(self):
        from pathlib2 import Path

        path = Path.cwd() / Path(self.argument("name"))
        name = self.argument("name")
        if not name:
            name = path.name

        if path.exists():
            if list(path.glob("*")):
                # Directory is not empty. Aborting.
                raise RuntimeError(
                    "Destination <fg=yellow>{}</> "
                    "exists and is not empty".format(path)
                )
        self.line("Initializing .........")
        self.line("")
        # generate project
        self.create_folder(name)
        self.line(f"Created folder: <fg=green>{os.getcwd()}{name}</>")
        # Get files in template
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../template")
        # generate directories and files in the template
        for root, dirs, files in os.walk(template_path):
            relative_path = root.replace(template_path, "").lstrip("\\").lstrip("/")
            if dirs:
                for dir in dirs:
                    self.create_folder(os.path.join(name, relative_path, dir))
                    if relative_path:
                        self.line(f"Created folder: <fg=green>{os.getcwd()}{name}\\{relative_path}\\{dir}</>")
                    else:
                        self.line(f"Created folder: <fg=green>{os.getcwd()}{name}\\{dir}</>")
            if files:
                for file in files:
                    with open(os.path.join(root, file), mode="rb") as f:
                        self.create_file(os.path.join(name, relative_path, file.replace(".template","")), f.read())
                        self.line(f"Created file: <fg=green>{os.getcwd()}{name}\\{relative_path}\\{file.replace('.template','')}</>")
        self.line("")
        self.line(f"<fg=green>Successfully Created {name}</>")

    def create_folder(self,folder):
        os.makedirs(folder, mode=0o777)

    def create_file(self,file, file_content):
        with open(file, mode="wb") as ff:
            ff.write(file_content)

if __name__ == '__main__':
    pass
