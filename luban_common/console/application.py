#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2020/8/15 20:00
# @Author  : hubiao

from cleo.application import Application as BaseApplication
from luban_common.__version__ import __version__
from .cases_command import CasesCommand
from .weixin_msg_command import WeixinMsgCommand
from .swagger_command import SwaggerCommand
from .new_command import NewCommand


class Application(BaseApplication):
    def __init__(self):
        super(Application, self).__init__("luban", __version__)

        for command in self.get_default_commands():
            self.add(command)

    def get_default_commands(self):  # type: () -> list
        commands = [
            NewCommand(),
            SwaggerCommand(),
            WeixinMsgCommand(),
            CasesCommand()
        ]

        return commands


if __name__ == "__main__":
    Application().run()