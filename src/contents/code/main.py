#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restrictions
# * Modications to this file must be reported to above email
 
#import PyQt4
import PyKDE4
try:
    from PyQtAbstractions import *
except:
    print "You need to install PyQtAbstractions from https://github.com/ekholm/PyQtAbstractions/"
    sys.exit(1)

if Qt.isPySide: import pyside_resource
if Qt.isPyQt4:  import pyqt4_resource

import weather

QtGui.QApplication.setApplicationName('weather')

class Main(Qt.MainObject):
    _mainForm  = ":/forms/main.ui"
        
    def _connectUI(self):
        self._settings.beginGroup("general")
        self._country = self._settings.value('country', 'Sweden')
        self._city    = self._settings.value('city',    'Stockholm')
        self._unit    = self._settings.value('unit',    'Metric')
        self._settings.endGroup()

        if Qt.isPyKDE4: self.setHasConfigurationInterface(True)
        if Qt.isPyKDE4: self.setAspectRatioMode(Plasma.IgnoreAspectRatio)

        self.checkWeather()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkWeather)
        self.timer.start(0.5 * 60000)

    def _closeUI(self):
        return True
    
    # change this!!!
    # def createConfigurationInterface(self, dlg):
    # shall just a tab or so?!
    # /usr/lib64/python2.7/site-packages/PyKDE4/plasmascript.py
    # def configChanged(self):
    #  def saveState(self, config):
    def showConfigurationInterface(self):
        defaultConfig = {
            "city"    : self._city,
            "country" : self._country,
            "unit"    : self._unit}


        config = weather.Config(self, defaultConfig)

        if config.run() == QtGui.QDialog.Accepted:
            self._city     = config.getCity()
            self._country  = config.getCountry()
            self._unit     = config.getUnit()

            self._settings.beginGroup("general")
            self._settings.setValue('country', self._country)
            self._settings.setValue('city',    self._city)
            self._settings.setValue('unit',    self._unit)
            self._settings.endGroup()
            
            self.checkWeather()

    def checkWeather(self):
        wi = weather.Weather(self._city + "," + self._country, self._unit)

        self._ui.Location.setText(wi['location'])
        self._ui.Temp.setText(wi['temp'])
        self._ui.Condition.setText(wi['condition'])
        self._ui.Humidity.setText(wi['humidity'])
        self._ui.Direction.setText(wi['direction'])
        self._ui.Speed.setText(wi['speed'])

        self._ui.WindUnit.setText(wi['wind-unit'])
        self._ui.TempUnit.setText(wi['temp-unit'])

        for i in range(1, 4):
            getattr(self._ui, "Day_%d" % i).setText(wi['day_%d' % i])
            getattr(self._ui, "Min_%d" % i).setText(wi['min_%d' % i])
            getattr(self._ui, "Max_%d" % i).setText(wi['max_%d' % i])

            getattr(self._ui, "MinUnit_%d" % i).setText(wi['temp-unit'])
            getattr(self._ui, "MaxUnit_%d" % i).setText(wi['temp-unit'])

        for i in range(4):
            fileName = wi.getIcon(wi['condition_%d' % i])
            getattr(self._ui, "Icon_%d" % i).setPixmap(QtGui.QPixmap(fileName))
            getattr(self._ui, "Icon_%d" % i).setToolTip(wi['condition_%d' % i])

    def paintInterface(self, painter, option, rect):
        pass

def CreateApplet(parent):
    return Main(parent)

if __name__ == '__main__':
    app = Qt.Application("qrSign", "0.9", "ekholm.se", "Mattias Ekholm", sys.argv)
    m = Main()
    m.show()
    app.exec_()
