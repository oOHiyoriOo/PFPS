import requests
import os
import sys

__dirname = os.path.abspath(os.path.dirname(__file__))

if not os.path.isdir(__dirname+'/lists'):
    os.mkdir(__dirname+'/lists')

try:
    i = 0
    while True:
        if i <= 5000:
            try:
                s = requests.get("https://public.freeproxyapi.com/api/Proxy/Mini")
            except Exception as err:
                print("Request => "+str(err)+" <=")
                break
            if s.status_code == 200:
                res = s.json()
                MODE = 'a' if os.path.isfile(res['type']+"_"+res['proxyLevel']+'.txt') else 'w'

                with open(__dirname+'/lists/'+str(res['type'])+"_"+str(res['proxyLevel'])+'.txt',MODE,encoding='utf-8') as output:
                    output.write(str(res['host'])+":"+str(res['port'])+"\n")
                os.system("echo "+str(res['host'])+":"+str(res['port'])+">> bigProxy.txt")
                i = i +1
                print("Got["+str(i)+"]: "+str(res['host'])+":"+str(res['port'])+(" "*70),end="\r")
            else:
                break
        else:
            FProxy = []
            with open('bigProxy.txt','r',encoding='utf-8') as BigBoi:
                proxys = BigBoi.readlines()

            x = 0
            for proxy in proxys:
                
                if FProxy.count(proxy) == 0:
                    FProxy.append(proxy)
                x = x + 1

                # this is just a loading bar :D
                LSYM = 70
                PRC = (x / len(proxys)) * 100
                SYM = round((PRC * LSYM) / 100, 0)

                PROG = ("="* int( round(SYM -1,0) ))
                EMPTPROG = (" "* int( round( (LSYM - (SYM-1)),0) ) )
                print("Sorting "+str(round(PRC,2))+"% |"+PROG+">"+EMPTPROG+"| "+str(x)+" / "+str(len(proxys))+"        ",end="\r")


            with open('bigProxy.txt','w',encoding='utf-8') as BigBoi:
                BigBoi.writelines(FProxy)   
            
            FProxy = None
            proxys = None
            BigBoi = None
            x = None
            proxy = None
            LSYM = None
            PRC = None
            SYM = None
            PROG = None
            EMPTPROG = None

            i = 0

except KeyboardInterrupt:
    quit()
    sys.exit()