#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/15 20:00
# @Author  : hubiao
import os

import chevron
from cleo import Command as BaseCommand
from pathlib2 import Path
from luban_common.console.analysis_swagger import AnalysisSwaggerJson


class SwaggerCommand(BaseCommand):
    """
    Swagger generates file interfaces and use cases

    swagger
        {swagger-url-json : Swagger url地址，必须是json地址}
        {--d|directory=? : 生成到指定的目录，可选参数，不指定时生成到当前目录}
    """

    def handle(self):
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
                        # Directory is not empty. Aborting.
                        raise RuntimeError(
                            "Destination <fg=yellow>{}</> "
                            "exists and is not empty".format(path)
                        )

                path.mkdir(mode=0o777, parents=True, exist_ok=True)
                package_init = path / "__init__.py"
                package_init.touch(exist_ok=False)
                current_path = os.path.dirname(os.path.realpath(__file__))
                for group in values:
                    with open(f'{current_path}/../config/interface.mustache', 'r') as mustache:
                        interfaces = chevron.render(mustache, group)
                        interface_file = path/f"{group['file_name']}.py"
                        with interface_file.open("w", encoding="utf-8") as f:
                            f.write(interfaces.replace("'$","").replace("$'","").replace("$",""))
                        self.line("Created file: <fg=green>{}</>".format(interface_file))
                self.line("<fg=green>Successfully generate</>")

