import os.path
import win32evtlog
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XML, fromstring
import time
from dateutil.parser import parse
import requests
import json

# Get API key from here: https://ipgeolocation.io/ 1k per day
api_key='c1ce57dbefbd44d1bcd44ea921491aac'

log_file_name='failed_rdp.log'

log_file_path=f'C:\ProgramData\{log_file_name}'



#The fake logs we made to train the program
def write_fake_log():
    f = open(log_file_path, "a")
    
    fake_logs=["latitude:47.91542,longitude:-120.60306,destinationhost:samplehost,username:fakeuser,sourcehost:24.16.97.222,state:Washington,country:United States,label:United States - 24.16.97.222,timestamp:2021-10-26 03:28:29" ,
    "latitude:-22.90906,longitude:-47.06455,destinationhost:samplehost,username:lnwbaq,sourcehost:20.195.228.49,state:Sao Paulo,country:Brazil,label:Brazil - 20.195.228.49,timestamp:2021-10-26 05:46:20" ,
    "latitude:52.37022,longitude:4.89517,destinationhost:samplehost,username:CSNYDER,sourcehost:89.248.165.74,state:North Holland,country:Netherlands,label:Netherlands - 89.248.165.74,timestamp:2021-10-26 06:12:56" ,
    "latitude:40.71455,longitude:-74.00714,destinationhost:samplehost,username:ADMINISTRATOR,sourcehost:72.45.247.218,state:New York,country:United States,label:United States - 72.45.247.218,timestamp:2021-10-26 10:44:07" ,
    "latitude:33.99762,longitude:-6.84737,destinationhost:samplehost,username:AZUREUSER,sourcehost:102.50.242.216,state:Rabat-Salé-Kénitra,country:Morocco,label:Morocco - 102.50.242.216,timestamp:2021-10-26 11:03:13" ,
    "latitude:-5.32558,longitude:100.28595,destinationhost:samplehost,username:Test,sourcehost:42.1.62.34,state:Penang,country:Malaysia,label:Malaysia - 42.1.62.34,timestamp:2021-10-26 11:04:45" ,
    "latitude:41.05722,longitude:28.84926,destinationhost:samplehost,username:AZUREUSER,sourcehost:176.235.196.111,state:Istanbul,country:Turkey,label:Turkey - 176.235.196.111,timestamp:2021-10-26 11:50:47" ,
    "latitude:55.87925,longitude:37.54691,destinationhost:samplehost,username:Test,sourcehost:87.251.67.98,state:null,country:Russia,label:Russia - 87.251.67.98,timestamp:2021-10-26 12:13:45" ,
    "latitude:52.37018,longitude:4.87324,destinationhost:samplehost,username:AZUREUSER,sourcehost:20.86.161.127,state:North Holland,country:Netherlands,label:Netherlands - 20.86.161.127,timestamp:2021-10-26 12:33:46" ,
    "latitude:17.49163,longitude:-88.18704,destinationhost:samplehost,username:Test,sourcehost:45.227.254.8,state:null,country:Belize,label:Belize - 45.227.254.8,timestamp:2021-10-26 13:13:25" ,
    "latitude:-55.88802,longitude:37.65136,destinationhost:samplehost,username:Test,sourcehost:94.232.47.130,state:Central Federal District,country:Russia,label:Russia - 94.232.47.130,timestamp:2021-10-26 14:25:33" ]

    for i in fake_logs:
        f.write(f'{i}\n')

#Here we check if the file exists
if os.path.exists(log_file_path) == False:
    f = open(log_file_path, "x")
    write_fake_log()


#We get logs from the event viewer with an infinite loop
while (True):
        time.sleep(1)
        computer = None # None = Local
        logType = "Security"
        h=win32evtlog.OpenEventLog(computer, logType)
        flags= win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
        evtLogs = win32evtlog.ReadEventLog(h, flags, 0)
        evtLogs[0]

        channelName = "Security"
        flags = win32evtlog.EvtQueryReverseDirection
        evtQueryResultNo = 100
        evtQuery = "*[System[(EventID=4625)]]"
        evtQueryTimeout = -1

        #we run it as administrator for proper authorization
        evtQueryResult = win32evtlog.EvtQuery(channelName, flags, evtQuery, None)

        events = win32evtlog.EvtNext(evtQueryResult, evtQueryResultNo, evtQueryTimeout, 0)

        for event in events:
        
                myroot=ET.fromstring(win32evtlog.EvtRender(event, win32evtlog.EvtRenderEventXml))
              
                timeCreated=myroot[0][7].attrib
                dt=parse(timeCreated.get('SystemTime'))
                timestamp=dt.strftime('%Y-%m-%d %H:%M:%S')
                #print('timestamp:',timestamp)
                

                eventid=myroot[0][1].text
                #print('eventid:',eventid)
                
                destinationHost=myroot[0][12].text
                #print('destinationHost:',destinationHost)

                username=myroot[1][5].text
                #print('username:',username)
                
                sourceIp=myroot[1][19].text
                #print('sourceIp:',sourceIp)

                sourceHost=myroot[1][11].text
                #print('sourceHost',sourceHost)
                
                file = open(log_file_path, 'r')   
                content=file.read()

                #In order not to write the same logs twice, we add a condition here using timestamp
                if(content.find(timestamp)==-1 or len(content)==0):
                    time.sleep(1)
                    
                    response = requests.get(f'https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={sourceIp}')
                    result = json.loads(response.content)

                    latitude=result['latitude']
                    longitude=result['longitude']
                    state_prov=result['state_prov']
                    if state_prov=="":
                        state_prov="null"
                    country=result['country_name']
                    if country=="":
                        country="null"
                    
                    log=(f'latitude:{latitude},longitude:{longitude},destinationhost:{destinationHost},username:{username},sourcehost:{sourceIp},state:{state_prov},country:{country},label:{country} - {sourceIp},timestamp:{timestamp}')
                    f = open(log_file_path, "a")
                    f.write(f'{log.encode("utf-8")}\n')
                    print(log)
                #else:
                    
                    # Entry already exists in custom log file. Do nothing, optionally
                    #print('Log Exist..')
       
        

