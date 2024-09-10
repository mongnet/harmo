#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/7/15 20:00
# @Author  : hubiao
import os

from cleo.commands.command import Command
from cleo.helpers import argument, option
from harmo.mitm import record

class RecordCommand(Command):
    name = "record"
    description = "流量录制"
    arguments = []
    options = [
        option(
            "init",
            "i",
            description="初始化流量录制相关配置文件，可选",
            default=None,
            flag=True
        )
    ]

    def handle(self):
        if self.option("init"):
            template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mitm", "template")
            for root, dirs, files in os.walk(template_path):
                relative_path = root.replace(template_path, "").lstrip("\\").lstrip("/")
                if dirs:
                    for dir in dirs:
                        self.create_folder(os.path.join(relative_path, dir))
                        if relative_path:
                            self.line(f"Created folder: <fg=green>{os.getcwd()}\\{relative_path}\\{dir}</>")
                        else:
                            self.line(f"Created folder: <fg=green>{os.getcwd()}\\{dir}</>")
                if files:
                    for file in files:
                        with open(os.path.join(root, file), mode="rb") as f:
                            self.create_file(os.path.join(relative_path, file.replace(".template", "")),
                                                     f.read())
                            self.line(
                                f"Created file: <fg=green>{os.getcwd()}\\{relative_path}\\{file.replace('.template', '')}</>")
        else:
            record.run_mitmdump_script()

    def create_folder(self,folder):
        os.makedirs(folder, mode=0o777)

    def create_file(self,file, file_content):
        with open(file, mode="wb") as ff:
            ff.write(file_content)

if __name__ == '__main__':
    pass
