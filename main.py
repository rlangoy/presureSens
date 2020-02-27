from MicroWebSrv2 import *
from time         import sleep
from _thread       import allocate_lock
from machine import ADC,Pin
import os
import ujson

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



adc = ADC(Pin(33))            # create ADC object on ADC pin
adc.atten(ADC.ATTN_11DB)    # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)

mws2 = MicroWebSrv2()
mws2.SetEmbeddedConfig()
@WebRoute(GET, '/show-recoredsessions', name='Show recordings')
def RequestTestPost(microWebSrv2, request) :
    strFiles=os.listdir("www")
    htmlFiles=""
    for file in strFiles :
        htmlFiles=htmlFiles+ '<a href="' + file + '">'+file+'</a>' + '<br>'
    
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

def OnWebSocketAccepted(microWebSrv2, webSocket) :
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
# ============================================================================
# ============================================================================




def OnWebSocketTextMsg(webSocket, msg) :
    #print('WebSocket text --message: %s' % msg)
    global _voltage       # Acess the global voltage value
    global _logging       # Acess the global voltage value
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
#    _logFilePtr.write("Amplitude")
        
def stopLogging():
    global _logging           # Acess the global loging state
    _logging=False
    _logFilePtr.close()  # close the log file

def deleteLogging():
    global _logging           # Acess the global loging state
    global _logFilePtr
    _logging=False
    if(_logFilePtr!=None):
        _logFilePtr.close()  # close the log file
    strFiles=os.listdir("www/"+_logDir)    
    for file in strFiles :
        try:
            os.remove("www/"+_logDir+"/"+file)        
        except:
            print("error rem file")
    


# Loads the WebSockets module globally and configure it,
wsMod = MicroWebSrv2.LoadModule('WebSockets')
wsMod.OnWebSocketAccepted = OnWebSocketAccepted

mws2.StartManaged()

cnt=0
# Main program loop until keyboard interrupt,
try :
    while True :
        _voltage = (adc.read()*100/4095.0)+.01
        #print(_voltage)
        if(_voltage > 100):
            _voltage=0
         
        sleep(.1)        
        
except KeyboardInterrupt :
    mws2.Stop()
