#!/usr/bin/env python
#######################################################
#
# @Author: Hardik Mehta <hard.mehta@gmail.com>
#    Classes: Info, Weather
# ...and Mattias Ekholm <code@ekholm.se>
#    rest of the code and updates to the Info and Weather classes
# 
# @version: 0.1 basic script
#
########################################################

__all__ = []
 
from PyQtAbstractions import *

import urllib

import xml.dom
import xml.dom.minidom

map = {
    "clear"    : ":/images/sunny.svg",
    "cloud"    : ":/images/cloudy.svg",
    "drizzle"  : ":/images/drizzle.svg",
    "fair"     : ":/images/sunny.svg",
    "flurries" : ":/images/snow.svg",
    "fog"      : ":/images/foggy.svg",
    "haze"     : ":/images/haze.svg",
    "na"       : ":/images/not-available.svg",
    "overcast" : ":/images/cloudy.svg",
    "rain"     : ":/images/showers.svg",
    "shower"   : ":/images/showers.svg",
    "smok"     : ":/images/smoky.svg",
    "snow"     : ":/images/snow.svg",
    "storm"    : ":/images/thunderstorms.svg",
    "sunny"    : ":/images/sunny.svg",
    "thunder"  : ":/images/thunderstorms.svg",
    "windy"    : ":/images/windy.svg",
    "wintry"   : ":/images/snow.svg",
    }

def getIcon(condition):
    lower_condition = condition.lower()

    for c in map.keys():
        if c in lower_condition:
            return map[c]

    return map['na']

class Info:
    def __init__(self, location):
        #self._urlPart = "http://www.google.com/ig/api?weather="
        #self.url = "http://www.google.de/ig/api?weather=" + location
        self._urlPart = "http://www.google.com/ig/api?"

        self.general = {"location": "N/A", "unit":"Metric","city":"N/A"}
        self.current = {"condition":"N/A","temp_c":"N/A","temp_f":"N/A","humidity":"N/A","wind_condition":"N/A"}
        self.forecast = [{"day_of_week":"N/A","low":"N/A","high":"N/A","condition":"N/A"}]    
        
        self._parse(location)

    def _parse(self, location):
        #strUrl = self._urlPart + location
        strUrl = self._urlPart + urllib.urlencode({'weather' : location}) 
        #+'&' + urllib.urlencode({'hl':'it'})
         
        try:
            sock = urllib.urlopen(strUrl)
        except IOError:
            self.general["location"] = "Connection Error"
            return
        
        #encoding = sock.headers['Content-type'].split('charset=')[1]
        #print encoding;
        
        #strUtf = strResponse.decode(encoding).encode('utf-8')
    
        #doc = minidom.parseString(strUtf)
        
        doc = xml.dom.minidom.parse(sock)
        nodes = doc.getElementsByTagName("forecast_information")

        # fetch general info
        if len(nodes) <> 0:
            node = nodes[0]
            self.general["location"] = (node.getElementsByTagName("postal_code")[0]).getAttribute("data")
            self.general["city"] = (node.getElementsByTagName("city")[0]).getAttribute("data")
            self.general["unit"] = (node.getElementsByTagName("unit_system")[0]).getAttribute("data")
        
        # fetch current conditions
        nodes = doc.getElementsByTagName("current_conditions")
        if len(nodes) <> 0:
            node = nodes[0]
            for key in self.current.keys():
                self.current[key] = (node.getElementsByTagName(key)[0]).getAttribute("data")
 
        # fetch forecast conditions
        fc = doc.getElementsByTagName("forecast_conditions")
        if len(fc) <> 0:
            fc_conditions = list()
            for elem in fc:
                condition = dict()
                for key in self.forecast[0].keys():
                    condition[key] = (elem.getElementsByTagName(key)[0]).getAttribute("data")
                fc_conditions.append(condition)
            self.forecast = fc_conditions
 
    def show(self):
        for k, v in self.general.iteritems():
            print k, v
        print "\n"
        for k, v in self.current.iteritems():
            print k, v
        print "\n"
        for fc in self.forecast:
            for k, v in fc.iteritems():
                print k, v
            print ""

class Weather:
    @staticmethod
    def getIcon(location):
        return getIcon(location)
        
    def __init__(self, location, reqUnit):
        wi = Info(location)
        self._extractData(wi, reqUnit)

    def __getitem__(self, key):
        if key in self._state:
            return self._state[key]
        else:
            return 'n/a'
    
    def _fromUStoSI(self, temp_in_f):
        return str(int(round((int(temp_in_f) - 32) * 5 / 9.0, 0)))
 
    def _fromSItoUS(self, temp_in_c):
        return str(int(round((int(temp_in_c) * (9.0 / 5.0)) + 32, 0)))
        
    def _fromMilesToKms(self, dist_in_miles):
        return round(1.61 * dist_in_miles,1)
 
    def _fromKmsToMiles(self,dist_in_kms):
        return round(dist_in_kms/1.61, 1)
        
    def _extractData(self, wi, reqUnit):
        self._state = dict()
        self._state['location'] = wi.general["location"]
        
        xmlUnit = wi.general["unit"]
        if xmlUnit == "US":
            xmlUnit = "Imperial"
        else:
            xmlUnit = "Metric"
        
        if reqUnit == "Metric":
            self._state['temp'] = wi.current["temp_c"]
            self._state['temp-unit'] = "&deg;C"
            self._state['wind-unit'] = "km/h"
        elif reqUnit == "Imperial":
            self._state['temp'] = wi.current["temp_f"]
            self._state['temp-unit'] = "&deg;F"
            self._state['wind-unit'] = "mph"
        
        self._state['condition'] = wi.current["condition"]
        self._state['humidity']  = wi.current["humidity"]
        
        strWind = wi.current["wind_condition"]

        # print strWind
        if not strWind:
            if 'wind' in self._state:
                del self._state['wind']
        else:
            # Sometimes strWinds looks like "Wind: mph". It has the wrong format
            try:
                state = strWind.split()
                self._state['direction'] = state[1]
                speed = int(state[3])
                
                if reqUnit == xmlUnit:
                    self._state['speed'] = str(speed)
                elif reqUnit == "Metric":
                    self._state['speed'] = str(self._fromMilesToKms(speed))
                elif reqUnit == "Imperial":
                    self._state['speed'] = str(self._fromKmsToMiles(speed))

            except (IndexError):
                print "EXCEPTION: Wind string is in the wrong format: ",  strWind

        for i in range(len(wi.forecast)):
            forecast = wi.forecast[i]
            self._state['day_%d' % i]       = forecast["day_of_week"]
            self._state['condition_%d' % i] = forecast["condition"]
            self._state['min_%d' % i]       = self.getTemp(forecast["low"],  reqUnit, xmlUnit)
            self._state['max_%d' % i]       = self.getTemp(forecast["high"], reqUnit, xmlUnit)
            
    def getTemp(self, temp, reqUnit, xmlUnit):
        if reqUnit == xmlUnit:
            return temp
        elif reqUnit == "Metric":
            return self._fromUStoSI(temp)
        elif reqUnit == "Imperial":
            self._fromSItoUS(temp)
        
    def show(self):
        print self.location
        print self.current_temperature
        print self.current_condition
        print self.current_humidity
        print self.current_wind
        
        print ""
        
        strprn = " "
        for d in self.fc_dl:
            strprn = strprn + d + " "
        print strprn
        
        print ""
        
        strprn = " "
        for c in self.fc_conditions:
            strprn = strprn + c + " "
        print strprn
        
        print " "
    
        strprn = " "
        for t in self.fc_low_high:
            strprn = strprn + t + " "
        print strprn


class Config(Qt.Object):
    '''
    classdocs
    '''

    _mainForm = ':/forms/config.ui'

    def __init__(self, parent, defaultConfig):
        '''
        Constructor
        '''

        self._default = defaultConfig

        Qt.Object.__init__(self)
        
        self._ui._setParent(self)

    def _connectUI(self):
        self._ui.City.setText(self._default['city'])
        self._ui.Country.setText(self._default['country'])
        idx = self._ui.Unit.findText(self._default['unit'])
        self._ui.Unit.setCurrentIndex(idx)

        # self._ui.show()
    
    def getCity(self):
        return str.strip(str(self._ui.City.text()))
    
    def getCountry(self):
        return str.strip(str(self._ui.Country.text()))
    
    def getUnit(self):
        return str.strip(str(self._ui.Unit.currentText()))
