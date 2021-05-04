import multiprocessing as mp
from ctypes import c_char_p
###################################
import threading

import requests
import os
from colorama import Fore,init

init()

__dirname = os.path.abspath(os.path.dirname(__file__))
RDIR = ["lists","logs"]
for DIR in RDIR:
    if not os.path.isdir(__dirname+'/'+DIR):
        os.mkdir(__dirname+'/'+DIR)

s_print_lock = threading.Lock()
def s_print(*a, **b):
    """Thread safe print function"""
    with s_print_lock:
        s_print("\033[%d;%dH" % (0, 0))
        print(*a, **b)


def GetProxy(ThreadNo,ProxyList,ProxyCount,MaxRequestFails):
    fails = 0
    i = 0
    spacer = "\n"*(ThreadNo+1)
    while i < ProxyCount:
        try:
            s = requests.get("https://public.freeproxyapi.com/api/Proxy/Mini")

            if s.status_code == 200:
                res = s.json()

                proxy = str(res['host'])+":"+str(res['port'])
                if ProxyList.count(proxy) == 0:
                    ProxyList.append(proxy)
                    i = i + 1
                    s_print(spacer+Fore.GREEN+"Thread["+str(ThreadNo)+"] Got["+str(i)+"]: "+str(res['host'])+":"+str(res['port']))

            elif fails >= MaxRequestFails:
                i = ProxyCount
                break

        except Exception as err:
            fails = fails + 1
            s_print(spacer+Fore.RED+"Thread["+str(ThreadNo)+"] Failed."+Fore.RESET)
            LOGFILE = __dirname+"/logs/Thread["+str(ThreadNo)+"].log"
            MODE = 'a' if os.path.isfile(LOGFILE) else 'w'
            with open(LOGFILE,MODE,encoding='utf-8') as log:
                log.write(str(err)+"\n")
    


if __name__ == '__main__':
    Threads = 20
    ProxyLoopCount = 100000
    MaxFails = 2

    ProxyListShared = []
    TasksList = []
    
    for i in range(Threads):
        CT = threading.Thread(target=GetProxy, args=(i,ProxyListShared,int(round(ProxyLoopCount / Threads,0)),MaxFails,),daemon=True )
        TasksList.append(CT)
        CT.start()

    for Task in TasksList:
        Task.join()

    print("List: "+str(len(ProxyListShared))+"/"+str(ProxyLoopCount))
    MODE = 'a' if os.path.isfile('SyncList.txt') else 'w'
    with open('SyncList.txt',MODE,encoding='utf-8') as FinalSync:
        for proxy in ProxyListShared:
            FinalSync.write(proxy+"\n")