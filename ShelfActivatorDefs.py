# this gets updated after KC's changes
import datetime
from random import randint
from PyQt5 import QtWidgets
from DBUtils import *

def encodeToHex(val,places,placeCharacter):    
    return (hex(val)[len("0x"):100]).rjust(places,placeCharacter)

def generateSerialNumber(batchno):
    # returns a string representing hex representation of serial number
    rVal = encodeToHex(int(batchno),6,'0') + encodeToHex(randint(1,16777215),6,'0')
    print ("Serial Number = ",rVal)
    return rVal
    # return encodeToHex(5,6,'0') + encodeToHex(5,6,'0')

def getQLabel(labelText,fixedWidth,fixedHeight):
    rLabel = QtWidgets.QLabel()
    rLabel.setText(labelText)
    if fixedWidth >= 0:
        rLabel.setFixedWidth(fixedWidth)
    if fixedHeight >= 0:
        rLabel.setFixedHeight(fixedHeight)
    return rLabel

                