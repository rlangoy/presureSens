from MicroWebSrv2 import *
from time         import sleep
from _thread       import allocate_lock

mws2 = MicroWebSrv2()
mws2.AddMimeType('.gz', 'application/gz')

#@staticmethod
#AddMimeType('.tar', 'application/x-tar')
#def AddMimeType('.gz', 'application/gz')


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
# ============================================================================
# ============================================================================

#global _voltage
_voltage = 1
_webSockets = [ ]

def OnWebSocketTextMsg(webSocket, msg) :
    #print('WebSocket text --message: %s' % msg)
    global _voltage       # Acess the global voltage value
  #  _voltage=_voltage+7
  #  if(_voltage >99):
  #       _voltage=1
    JSONmessage = "{\"A0\":\"" + str(_voltage)+"\"}";
    webSocket.SendTextMessage(JSONmessage)
    #webSocket.SendTextMessage('%s' % _voltage)

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
        _voltage = _voltage + 1
        if(_voltage > 100):
            _voltage=0
         
        sleep(.01)
#        for ws in _webSockets :
#            JSONmessage = "{\"A0\":\"" + str(_voltage)+"\"}";
#            ws.SendTextMessage(JSONmessage)

        
except KeyboardInterrupt :
    mws2.Stop()
