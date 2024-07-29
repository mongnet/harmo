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
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=os.environ) as process:
        try:
            # 实时获取并打印 mitmdump 的输出
            for line in process.stdout:
                # 使用 end='' 避免每次打印后出现额外的换行符
                print(line, end='')
        except KeyboardInterrupt:
            # 通过 process.terminate() 终止进程
            process.terminate()
            print("录制被手动终止.")
        except Exception as e:
            process.terminate()
            print(f"录制异常终止: {e}")
        finally:
            print(f"录制已结束.")

if __name__ == '__main__':
    run_mitmdump_script()