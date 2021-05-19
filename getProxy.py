
import threading

import requests
import os
from colorama import Fore,init
import platform

init()

__dirname = os.path.abspath(os.path.dirname(__file__))
RDIR = ["logs"]
for DIR in RDIR:
    if not os.path.isdir(__dirname+'/'+DIR):
        os.mkdir(__dirname+'/'+DIR)

s_print_lock = threading.Lock()
def s_print(*a, **b):
    """Thread safe print function"""
    with s_print_lock:
        print(*a, **b)


def GetProxy(ThreadNo,ProxyList,ProxyCount,MaxRequestFails,PingCheck):
    fails = 0
    i = 0

    if str(platform.system() == "Linux"):
        spaces = "\033[0H" + ("\n"*(ThreadNo+1))
    else:
        spaces = ""

    while i < ProxyCount:
        try:
            s = requests.get("https://public.freeproxyapi.com/api/Proxy/Medium")

            if s.status_code == 200:
                res = s.json()
                
                if res['isAlive'] == True and res['proxyLevel'] in ["Anonymous","Elite"]: # just skip the proxy if it's considered 'dead', i dont value this as error.
                    proxy = str(res['host'])+":"+str(res['port'])
                    if ProxyList.count(proxy) == 0:
                        if PingCheck:
                            pass

                        ProxyList.append(proxy)
                        i = i + 1
                        s_print(spaces+Fore.GREEN+"Thread["+str(ThreadNo)+"] Got["+str(i)+"]: "+str(res['host'])+":"+str(res['port'])+(" "*10))


            elif fails >= MaxRequestFails:
                i = ProxyCount
                break
            elif s.status_code != 200:
                raise ConnectionError("s.status_code: "+str(s.status_code))

        except Exception as err:
            fails = fails + 1
            s_print(spaces+Fore.RED+"Thread["+str(ThreadNo)+"] Failed."+Fore.RESET)
            LOGFILE = __dirname+"/logs/Thread["+str(ThreadNo)+"].log"
            MODE = 'a' if os.path.isfile(LOGFILE) else 'w'
            with open(LOGFILE,MODE,encoding='utf-8') as log:
                log.write(str(err)+"\n")

    s_print(spaces+Fore.YELLOW+"Thread["+str(ThreadNo)+"] Finished Job."+(" "*20))

def setup():
    options = {'Threads':'int','Proxy Count':'int','Max Fails':int}
    settings = []
    

    return settings #Threads, ProxyLoopCount, MaxFails, PingCheck


if __name__ == '__main__':


    Threads, ProxyLoopCount, MaxFails, PingCheck = setup()


    ProxyListShared = []
    TasksList = []
    
    for i in range(Threads):
        CT = threading.Thread(target=GetProxy, args=(i,ProxyListShared,int(round(ProxyLoopCount / Threads,0)),MaxFails,PingCheck,),daemon=True )
        TasksList.append(CT)
        CT.start()

    for Task in TasksList:
        Task.join()


    if str(platform.system() == "Linux"):
        spaces = "\033[0H" + ("\n"*(Threads+1))
    else:
        spaces = ""

    print(spaces+"Result: "+str(len(ProxyListShared))+"/"+str(ProxyLoopCount)+" Proxys saved.")
    MODE = 'a' if os.path.isfile('SyncList.txt') else 'w'
    with open('SyncList.txt',MODE,encoding='utf-8') as FinalSync:
        for proxy in ProxyListShared:
            FinalSync.write(proxy+"\n")

    print("\n"+spaces+Fore.RESET)