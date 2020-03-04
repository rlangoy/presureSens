from MicroWebSrv2 import *
from time         import sleep,time
from _thread       import allocate_lock
import os
import ujson
import datetime
# Import the ADS1x15 module.
import Adafruit_ADS1x15


global _logging
_logging = False       #Controls the file logging
_voltage = 1
_webSockets = [ ]

_logDir="log"
_logFilePtr=None     # _logFilePtr = open('numbers.csv', 'rw')

#Create logDir if it does not exist
try:
    os.stat("www/"+_logDir)
except:
    os.mkdir("www/"+_logDir)

def GetNewRecordFileName():
    strFiles=os.listdir("www/"+_logDir)
    fileCnt=len(strFiles)
    lastRecordFileNumber=99
    if (fileCnt>0):
        lastRecordFile=max(strFiles)
        lastRecordFileNumber = max([int(sub.split('.')[0]) for sub in strFiles])
    recordFileName=str(lastRecordFileNumber+1)+'.csv'
    return recordFileName

print("Ready to log to file: "+ GetNewRecordFileName() )
mws2 = MicroWebSrv2()

@WebRoute(GET, '/show-recoredsessions', name='Show recordings')
def RequestTestPost(microWebSrv2, request) :
    strFiles=os.listdir("www/"+_logDir)
    strFiles.sort()  # Sort files
    htmlFiles=""
    for file in strFiles :
        htmlFiles=htmlFiles+'<a href="' +_logDir+'/'+ file + '">'+file+'</a>&nbsp;&nbsp; '+str( int((os.path.getsize("www/"+_logDir+'/'+file))/1000))+' KB'+'&nbsp;&nbsp;&nbsp;&nbsp;<a href="lineFile.html?file='  +_logDir+'/'+ file + '">view </a> <br>'
        
       # <a href="https://www.w3schools.com/html/">Visit our HTML tutorial</a>
    content = """\
    <!DOCTYPE html>
    <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1" /> 
            <title>Recorded Seccions</title>
        </head>
        <body>
            <h2>Log Files:</h2>
            %s
        </body>
    </html>
    """ % (htmlFiles)
    request.Response.ReturnOk(content)


#mws2.SetEmbeddedConfig()
voltage=100
def OnWebSocketAccepted(microWebSrv2, webSocket) :
    voltage=100
    print('Example WebSocket accepted:')
    print('   - User   : %s:%s' % webSocket.Request.UserAddress)
    print('   - Path   : %s'    % webSocket.Request.Path)
    print('   - Origin : %s'    % webSocket.Request.Origin)
    webSocket.OnTextMessage   = OnWebSocketTextMsg
    webSocket.OnBinaryMessage = OnWebSocketBinaryMsg
    webSocket.OnClosed        = OnWebSocketClosed
    global _webSockets
    _webSockets.append(webSocket)
    
# ============================================================================

def OnWebSocketTextMsg(webSocket, msg) :
    print('WebSocket text --message: %s' % msg)
    global _voltage       # Acess the global voltage value
    try:
        jsonMsg= ujson.loads(msg)
    
        if(jsonMsg.get('Get') =='isLogging'):
            webSocket.SendTextMessage("{\"isLogging\":\"" + str(_logging)+"\"}")

        if(jsonMsg.get('Get') =='Voltage_A0'):           
            JSONmessage = "{\"Voltage_A0\":\"" + str(_voltage)+"\"}"
            webSocket.SendTextMessage(JSONmessage)            

        if(jsonMsg.get('Enable') =='Logging'):                 
            startLogging()

        if(jsonMsg.get('Disable') =='Logging'):            
            stopLogging()

        if(jsonMsg.get('Delete') =='Loggs'):
            deleteLogging()
            JSONmessage = "{\"Loggs\" : \"Deleted\"}"
            webSocket.SendTextMessage(JSONmessage)            

    except:
        print("OnWebSocketTextMsg Msg not proper JSON formated : " +msg)
    

# ------------------------------------------------------------------------

def OnWebSocketBinaryMsg(webSocket, msg) :
    print('WebSocket binary message: %s' % msg)

# ------------------------------------------------------------------------

def OnWebSocketClosed(webSocket) :
    print('WebSocket %s:%s closed' % webSocket.Request.UserAddress)
    global _webSockets

    if webSocket in _webSockets :
            _webSockets.remove(webSocket)
# ============================================================================
# ============================================================================
# ============================================================================

def startLogging():
    global _logging           # Acess the global loging state
    global _logFilePtr
    global _logDir
    _logging=True
    fname='www/'+_logDir+'/'+GetNewRecordFileName()
    print(fname)
    _logFilePtr = open(fname, 'w')
        
def stopLogging():
    global _logging           # Acess the global loging state
    _logging=False
    _logFilePtr.close()  # close the log file

def deleteLogging():
    global _logging           # Acess the global loging state
    global _logFilePtr
    
    if(_logging==True):
        _logFilePtr.flush()
        _logFilePtr.close()  # close the log file
        _logging=False
        
    strFiles=os.listdir("www/"+_logDir)    
    for file in strFiles :
        try:
            print(file)
            print(_logDir)
            strRemoveFile="www/"+_logDir+"/"+file
            print(strRemoveFile)
            os.remove(strRemoveFile)        
        except:
            print("error rem file")
    


# Loads the WebSockets module globally and configure it,
wsMod = MicroWebSrv2.LoadModule('WebSockets')
wsMod.OnWebSocketAccepted = OnWebSocketAccepted

mws2.StartManaged()
cnt=0

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()
# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 2

# Main program loop until keyboard interrupt,
try :
    while True :
        _voltage = (adc.read_adc(0, gain=GAIN) /320.0)
        
        #sleep(.05)

        if(_logging==True) :
            logStr=str(datetime.datetime.utcnow().timestamp())+','+str(_voltage)+'\n'     
            _logFilePtr.write(logStr)        
        else : 
            sleep(.05)
   
except KeyboardInterrupt :
    mws2.Stop()
 
