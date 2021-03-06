
import threading
import requests
import os
import platform
import json
import datetime

from pydoc import locate
from colorama import Fore,init

init()

__dirname = os.path.abspath(os.path.dirname(__file__))
RDIR = ["logs"] # rewuired directorys
for DIR in RDIR:
    if not os.path.isdir(__dirname+'/'+DIR):
        os.mkdir(__dirname+'/'+DIR)

# Fix print issue when using Threading
s_print_lock = threading.Lock()
def s_print(*a, **b):
    """Thread safe print function"""
    with s_print_lock:
        print(*a, **b)

def PingCheckFunc(Enabled,host):
    if not Enabled: # Shortcut if the check is disabled.
        return True
    else:
        silence = " >/dev/null 2>&1" if str(platform.system() == 'Linux') else " >nul 2>&1"
        response = os.system("ping "+("-c" if str(platform.system() == "Linux") else "-n ")+"1 " + host+silence)
        if response == 0:
            return True
        else:
            return False

def GetProxy(ThreadNo,ProxyList,ProxyListSplit,ProxyCount,MaxRequestFails,PingCheck,ForceLinuxOutput,ExportGeoJson,GeoJson):
    """Main Function for scraping proxys from the free api."""
    fails = 0
    i = 0

    if str(platform.system() == "Linux") or ForceLinuxOutput:
        spaces = "\033[0H" + ("\n"*(ThreadNo+1))
    else:
        spaces = ""

    while i < ProxyCount:
        try:
            s = requests.get("https://public.freeproxyapi.com/api/Proxy/Medium")

            if s.status_code == 200 and fails < MaxFails:
                res = s.json()
                
                # ["Anonymous","Elite"] are the only proxy types usefull, the others are snitches.
                if res['isAlive'] == True and res['proxyLevel'] in ["Anonymous","Elite"]: # just skip the proxy if it's considered 'dead', i dont value this as error.
                    proxy = str(res['host'])+":"+str(res['port'])

                    if ProxyList.count(proxy) == 0 and PingCheckFunc(PingCheck,res['host']):

                        ProxyList.append(proxy)
                        i = i + 1
                        s_print(spaces+Fore.GREEN+"Thread["+str(ThreadNo)+"] Got["+str(i)+"]: "+str(res['host'])+":"+str(res['port'])+(" "*10))

                        if ProxyListSplit['enabled'] == True: # Splitting and collecting more information.
                            # Create Basic data sructure if needed.
                            # [ True,Finnland: {'Socks4': { 'Elite':{ 'x.x.x.x:xxxx':'lan;lon' }, 'Anonymouse':{ 'x.x.x.x:xxxx':'lan;lon' } } } ]
                            if not res['countryName'] in ProxyListSplit:
                                ProxyListSplit[res['countryName']] = {}
                            
                            if not res['type'] in ProxyListSplit[res['countryName']]:
                                ProxyListSplit[res['countryName']][res['type']] = {}

                            if not res['proxyLevel'] in ProxyListSplit[res['countryName']][res['type']]:
                                ProxyListSplit[res['countryName']][res['type']][res['proxyLevel']] = {}
                            
                            proxy = str(res['host'])+":"+str(res['port'])
                            pos = str(res['latitude']) + ";" + str(res['longitude'])
                            ProxyListSplit[res['countryName']][res['type']][res['proxyLevel']][proxy] = pos

                        if ExportGeoJson:
                            CProxy = {} # current Proxy
                            CProxy['type'] = 'Feature'
                            CProxy['properties'] = {}
                            CProxy['properties']['name'] = res['host']
                            CProxy['properties']['address'] = res['countryName']
                            CProxy['properties']['marker-color'] = '#FF0000'
                            CProxy['geometry'] = {}
                            CProxy['geometry']['type'] = 'Point'
                            CProxy['geometry']['coordinates'] = []
                            (CProxy['geometry']['coordinates']).append(res['longitude'])
                            (CProxy['geometry']['coordinates']).append(res['latitude'])

                        (GeoJson['features']).append(CProxy)

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
    options = {'Threads':'int','Proxy Count':'int','Max Fails':'int','Ping Check':'bool','Split Lists?':'bool','Export Advanced':'bool','Force Linux Output':'bool','Export Geo.Json':'bool'}
    settings = [1,10,2,False,False,False,False,True]
    print("Just use 'enter' to use default Value shown in the []")
    for i, e in enumerate(options):
    #for e in options:
        res = input(e+" ("+options[e]+") ["+str(settings[i])+"]: ")
        if res.replace(" ","") != "":
            tmp = locate(options[e])
            valid = False
            while not valid:
                try:
                    tmp(res)
                    settings[i] = tmp(res)
                    valid = True
                except:
                    valid = False

    os.system('cls' if os.name == 'nt' else 'clear')
    return settings #Threads, ProxyLoopCount, MaxFails, PingCheck


if __name__ == '__main__':

    try:
        Threads, ProxyLoopCount, MaxFails, PingCheck, SplitLists, AdvancedOutput, ForceLinuxOutput, ExportGeoJson = setup()

        ProxyListShared = [] # all Proxys
        ProxyListSplit = {} # Proxy List with there type.
        TasksList = [] # List with all Threads, to 'Sync' them later 
        
        GeoJson = {} if ExportGeoJson else None
        if ExportGeoJson: # build the frame for the geoJson
            GeoJson['type'] = 'FeatureCollection'
            GeoJson['features'] = []


        ProxyListSplit['enabled'] = (True if SplitLists else True if AdvancedOutput else False)

        for i in range(Threads):
            CT = threading.Thread(target=GetProxy, args=(i,ProxyListShared,ProxyListSplit,int(round(ProxyLoopCount / Threads,0)),MaxFails,PingCheck,ForceLinuxOutput,ExportGeoJson,GeoJson,),daemon=True )
            TasksList.append(CT)
            CT.start()

        for Task in TasksList:
            Task.join()


        if str(platform.system() == "Linux") or ForceLinuxOutput: # Cursor position only works on linux as expected. (sometimes works on windows sometimes not.)
            spaces = "\033[0H" + ("\n"*(Threads+1)) # line reset with spacing.
        else:
            spaces = ""

        print(spaces+"Result: "+str(len(ProxyListShared))+"/"+str(ProxyLoopCount)+" Proxys, saving...")
        
        # Percentage of fullfilling the requested Proxys
        PRC = (len(ProxyListShared) / ProxyLoopCount) * 100 # what we got / what we wanted * 100
        print(str(round(PRC,2))+"% Sucess rate.") # round to 2 digits.
        print("") # just get some space :P

        MODE = 'a' if os.path.isfile('AllProxys.txt') else 'w' # we just append if the file exist, to now override existing proxys.
        with open('AllProxys.txt',MODE,encoding='utf-8') as FinalSync:
            for proxy in ProxyListShared:
                FinalSync.write(proxy+"\n")

        if AdvancedOutput:
            if not os.path.isdir('advancedExport'):
                os.mkdir('advancedExport')
            print(spaces+"Dumping advanced output...")
            
            date_time = datetime.datetime.now()
            Filename = str(date_time.strftime("%Y-%m-%d %H_%M_%S"))
            Filename = Filename.replace(" ","_")

            with open(__dirname+'/advancedExport/'+Filename+".json",'w',encoding='utf-8') as AOut:
                AOut.write(json.dumps(ProxyListSplit))

        if ExportGeoJson:
            if not os.path.isdir('geoExport'):
                os.mkdir('geoExport')

            date_time = datetime.datetime.now()
            Filename = str(date_time.strftime("%Y-%m-%d %H_%M_%S"))
            Filename = Filename.replace(" ","_")

            with open(__dirname+'/geoExport/'+Filename+".json",'w',encoding='utf-8') as AOut:
                AOut.write(json.dumps(GeoJson))

        print("\n"+spaces+Fore.RESET)

    except KeyboardInterrupt:
        exit() # it happend for me, exit alone dont work so ill quit if it's not working
        quit()
        
    except Exception as err:
        LOGFILE = __dirname+"/logs/Main.log" # main error
        MODE = 'a' if os.path.isfile(LOGFILE) else 'w'
        with open(LOGFILE,MODE,encoding='utf-8') as log:
            log.write(str(err)+"\n")
