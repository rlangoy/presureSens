from MicroWebSrv2 import *
from time         import sleep
from _thread       import allocate_lock
from machine import ADC,Pin
adc = ADC(Pin(33))            # create ADC object on ADC pin
adc.atten(ADC.ATTN_11DB)    # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)

mws2 = MicroWebSrv2()
mws2.SetEmbeddedConfig()
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


# ============================================================================
# ============================================================================
# ============================================================================

#global _voltage
_voltage = 1



def OnWebSocketTextMsg(webSocket, msg) :
    print('WebSocket text --message: %s' % msg)
    global _voltage       # Acess the global voltage value
  #  _voltage=_voltage+7
  #  if(_voltage >99):
  #       _voltage=1
    
    webSocket.SendTextMessage('%s' % _voltage)

# ------------------------------------------------------------------------

def OnWebSocketBinaryMsg(webSocket, msg) :
    print('WebSocket binary message: %s' % msg)

# ------------------------------------------------------------------------

def OnWebSocketClosed(webSocket) :
    print('WebSocket %s:%s closed' % webSocket.Request.UserAddress)

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
        _voltage = adc.read()*100/4095.0
        #print(_voltage)
        if(_voltage > 100):
            _voltage=0
         
        sleep(.1)
except KeyboardInterrupt :
    mws2.Stop()
