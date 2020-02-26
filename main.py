from MicroWebSrv2 import *
from time         import sleep
from _thread       import allocate_lock
from machine import ADC,Pin
import os
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
        
       # <a href="https://www.w3schools.com/html/">Visit our HTML tutorial</a>
    content = """\
    <!DOCTYPE html>
    <html>
        <head>
            <title>Recorded Seccions</title>
        </head>
        <body>
            <h2>Log Files:</h2>
            %s
        </body>
    </html>
    """ % (htmlFiles)
    request.Response.ReturnOk(content)

global _voltage
_voltage = 1
_webSockets = [ ]
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
# ============================================================================
# ============================================================================


def OnWebSocketTextMsg(webSocket, msg) :
    #print('WebSocket text --message: %s' % msg)
    global _voltage       # Acess the global voltage value
    JSONmessage = "{\"A0\":\"" + str(_voltage)+"\"}";
    webSocket.SendTextMessage(JSONmessage)
  

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
