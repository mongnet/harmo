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
    arguments = [
        argument(
            "modelName",
            description="场景或模块名称，用于归类用例，必填"
        )
    ]

    def handle(self):
        # 模块名称
        modelName = self.argument("modelName")
        if modelName:
            ret = re.findall(f'[/:*?"<>|]',modelName)
            if ret:
                raise RuntimeError(
                    f'Destination <fg=yellow>{self.option("case-directory")}</> '
                    "The case directory Contains illegal characters, "
                    f"Illegal characters: {ret}"
                )
        else:
            modelName = None
        # 执行
        replay.Replay().run(modelName)

if __name__ == '__main__':
    pass
