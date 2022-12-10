#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/2/15 20:00
# @Author  : hubiao
import os

from cleo import Command as BaseCommand

class NewCommand(BaseCommand):
    """
    Create a new test project

    new
        {name : 测试项目的名称}
    """
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
        NewCommand().create_folder(name)
        self.line(f"Created folder: <fg=green>{name}</>")
        # Get files in template
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../template")
        # generate directories and files in the template
        for root, dirs, files in os.walk(template_path):
            relative_path = root.replace(template_path, "").lstrip("\\").lstrip("/")
            if dirs:
                for dir in dirs:
                    NewCommand().create_folder(os.path.join(name, relative_path, dir))
                    self.line(f"Created folder: <fg=green>{dir}</>")
            if files:
                for file in files:
                    with open(os.path.join(root, file), encoding="utf-8") as f:
                        NewCommand().create_file(os.path.join(name, relative_path, file.replace(".template","")), f.read())
                        self.line(f"Created file: <fg=green>{file.replace('.template','')}</>")
        self.line("Initializing End")
        self.line("")
        self.line(f"<fg=green>Successfully Created {name}</>")

    def create_folder(self,folder):
        os.makedirs(folder, mode=0o777)

    def create_file(self,file, file_content=""):
        with open(file, "w", encoding="utf-8") as f:
            f.write(file_content)

if __name__ == '__main__':
    pass
