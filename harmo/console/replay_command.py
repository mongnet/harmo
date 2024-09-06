#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/7/15 20:00
# @Author  : hubiao
import re

from cleo.commands.command import Command
from harmo.mitm import replay
from cleo.helpers import argument, option

class ReplayCommand(Command):
    name = "replay"
    description = "流量回放"
    arguments = []
    options = [
        option(
            "modelName",
            "m",
            description="场景或模块名称，用于归类用例，可选",
            default=None,
            flag=False
        )
    ]

    def handle(self):
        # 模块名称
        modelName = self.option("modelName")
        if modelName:
            ret = re.findall(f'[/:*?"<>|]',modelName)
            if ret:
                raise RuntimeError(
                    f'Destination <fg=yellow>{self.option("modelName")}</> '
                    "The model name Contains illegal characters, "
                    f"Illegal characters: {ret}"
                )
        # 执行
        replay.Replay().run(modelName)

if __name__ == '__main__':
    pass
