#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/4/3 15:00
# @Author  : hubiao
# @Email   : 250021520@qq.com
import os
import subprocess

def run_mitmdump_script():
    # 定义 mitmdump 命令和参数
    addons_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "addons.py")
    command = ['mitmdump', '-s', addons_py_path]
    print("录制已开始，请设置好代理并开始操作，按 ctrl+C 结束录制.")
    # 使用 subprocess.Popen 来启动命令并获取输出
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=os.environ, encoding="utf-8") as process:
        try:
            # 实时获取并打印 mitmdump 的输出
            for line in process.stdout:
                print(line, end='')  # 使用 end='' 避免每次打印后出现额外的换行符
        except KeyboardInterrupt:
            # 如果需要，可以在这里处理 KeyboardInterrupt 异常
            # 例如，可以通过 process.terminate() 终止进程
            process.terminate()
            print("录制被手动终止.")
        finally:
            # 等待进程结束并获取退出码
            # process.wait()
            # exit_code = process.returncode
            print(f"录制结束.")

if __name__ == '__main__':
    run_mitmdump_script()