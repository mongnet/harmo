import signal,os,sys

# 自定义信号处理函数
def my_handler(signum, frame):
    global stop
    stop = True
    print("终止")

# 设置相应信号处理的handler
signal.signal(signal.SIGINT, my_handler)  # 读取Ctrl+c信号

try:
    name =sys.argv[1]
except:
    name = "NoName"
try:
    retry = sys.argv[2]
except:
    retry = None
stop = False
count =0
while True:
    try:
        # 读取到Ctrl+c前进行的操作
        if stop or retry==True:
            curPath = os.path.abspath(os.path.dirname(__file__))
            rootPath = os.path.split(curPath)[0]
            sys.path.append(rootPath)
            import createScript
            res = createScript.execScript(name)
            if res !=[]:
                print("请建立规则，去掉唯一值对比，如id，时间，日期，等")
            # 中断时需要处理的代码
            break  # break只能退出当前循坏
            # 中断程序需要用 raise
        else:
            if count==0:
                os.system("mitmdump -s addons.py")
                count=1
    except Exception as e:
        print(str(e))
        break