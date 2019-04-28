#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Controlling the Raspberry Pi fan
#
# Author: BRZOZA
#
"""
<plugin key="BrzozaPiFan" name="PiFan" author="BRZOZA" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/abrzoza/domoticz_plugins_pi_fan">
    <description>
        <h2>Controlling the Raspberry Pi fan</h2><br/>
        Fan control based on CPU temperature
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Fan control after exceeding the CPU temperature</li>
            <li>Manual fan control</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Switch</li>
            <li>Temperature sensor</li>
        </ul>
        <h3>Configuration</h3>
        <ul style="list-style-type:square">
          <li>PIN to which the fan is connected</li>
          <li>The temperature above which the fan will be turned on</li>
        </ul>        
    </description>
    <params>
      <param field="Mode1" label="Fan pin" width="40px">
        <options>
          <option label="5" value="5"/>
          <option label="6" value="6" default="true" />
          <option label="13" value="13"/>
          <option label="19" value="19"/>
          <option label="26" value="26"/>
        </options>
      </param>
      <param field="Mode2" label="Fan start temperature" width="60px" required="true" default="55"/>
      <param field="Mode6" label="Debug" width="75px">
        <options>
          <option label="True" value="Debug"/>
          <option label="False" value="Normal" default="true"/>
        </options>
      </param>
    </params>
</plugin>
"""
import Domoticz
import os
import wiringpi

class BasePlugin:

    __NrPin = 6
    __MaxTemp = 55
    __Status = False
    __imageFanOff = 7
    __imageFanOn = 7
    __UNIT_CPUTEMP = 1
    __UNIT_FAN = 2

    def __init__(self):
        return

    def onStart(self):
        
        Domoticz.Debug("Start")

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        else:
            Domoticz.Debugging(0)

        self.__NrPin = int(Parameters["Mode1"])
        self.__MaxTemp = int(Parameters["Mode2"])
        
        self.__Status = wiringConf(self)
        
        self.__UNITS = [
            # Unit, Name, Type, Subtype, Options, Used, Image
            [self.__UNIT_CPUTEMP, "CPU temperature", 80, 5, {}, 1, 6],
            [self.__UNIT_FAN, "Fan", 244, 73, {}, 1, 7],
        ]        
        
        if self.__Status == True and len(Devices) == 0:
            for unit in self.__UNITS:
                Domoticz.Device(Unit=unit[0],
                                Name=unit[1],
                                Type=unit[2],
                                Subtype=unit[3],
                                Options=unit[4],
                                Used=unit[5],
                                Image=unit[6]).Create() 

 
        checkTEMP(self.__MaxTemp, self.__NrPin, self.__UNIT_FAN, self.__UNIT_CPUTEMP)

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        
        if Unit == self.__UNIT_FAN:
            Command = Command.strip()
            action, sep, params = Command.partition(' ')
            action = action.capitalize()
            params = params.capitalize()
            
            if action == "On":
                wiringpi.digitalWrite(self.__NrPin, 1)
            else:
                wiringpi.digitalWrite(self.__NrPin, 0)
                
        getFanStatus(self.__UNIT_FAN, self.__NrPin)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        getFanStatus(self.__UNIT_FAN, self.__NrPin)
        checkTEMP(self.__MaxTemp, self.__NrPin, self.__UNIT_FAN, self.__UNIT_CPUTEMP)
        
global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
    
options = {
    "measure_temp": ["temp", "'C"],
    "get_mem gpu": ["gpu", "M"],
    "get_mem arm": ["arm", "M"],
    "measure_volts core": ["volt", "V"],
    "measure_volts sdram_c": ["volt", "V"],
    "measure_volts sdram_i": ["volt", "V"],
    "measure_volts sdram_p": ["volt", "V"],
    "get_throttled": ["throttled", "x0"],
}


def vcgencmd(option):
    if option in options:
        cmd = "/opt/vc/bin/vcgencmd {}".format(option)
        Domoticz.Debug("cmd: {}".format(cmd))
        try:
            res = os.popen(cmd).readline()
            Domoticz.Debug("res: {}".format(res))
            res = res.replace("{}=".format(options[option][0]), "")
            res = res.replace("{}\n".format(options[option][1]), "")
            Domoticz.Debug("res (replaced): {}".format(res))
        except:
            res = "0"
    else:
        res = "0"
    return float(res)    

def getCPUtemperature():
    # Return CPU temperature
    try:
        res = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
    except:
        res = "0"
    return round(float(res)/1000, 1)
    
def wiringConf(self):
    # Config wiring
    try:
        wiringpi.wiringPiSetupGpio()
        NrPin = int(Parameters["Mode1"])
        wiringpi.pinMode(NrPin, 1)
        Domoticz.Debug("Configure wiring Pin {}".format(str(NrPin)))
        WiringStatus = True
    except:
        Domoticz.Debug("Config wiringPi error")
        WiringStatus = False
        
    return WiringStatus
    
def checkTEMP(maxTemp, Pin, Unit, UnitTemp):
    fnumber = getCPUtemperature()
    #UpdateDevice(int(UnitTemp), -1, str(fnumber), AlwaysUpdate=True)
    Devices[UnitTemp].Update(nValue = int(fnumber), sValue = str(fnumber), Image=7)
    Domoticz.Log("CPU temp ..........: -1 {} °C".format(fnumber))
            
    if fnumber > maxTemp:
        wiringpi.digitalWrite(int(Pin), 1)
        getFanStatus(Unit, Pin)
        Domoticz.Log("The fan was turned on when the temperature CPU was exceeded")
        
        return True
    else:
        wiringpi.digitalWrite(Pin, 0)
        getFanStatus(Unit, Pin)
        Domoticz.Log("Lowering the temperature turned off the fan")    
        
        return False
        
def getFanStatus(Unit, Pin):
    if wiringpi.digitalRead(int(Pin)) == 1:
        UpdateDevice(int(Unit), 1, str(1), AlwaysUpdate=True)
        return 1
    else:
        UpdateDevice(int(Unit), 0, str(0), AlwaysUpdate=True)
        return 0
        
def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[
                Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(
                nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)