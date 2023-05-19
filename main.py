from PyQt5 import QtCore, QtGui, QtWidgets
from configparser import ConfigParser
from DBUtils import *
from ShelfActivatorDefs import *
from ShelfActivatorUI import setupUILayout,retranslateUi
# from ShelfActivatorDefs import * # deleteShelvesAndFacings,addFacings,addShelves
import json, requests
shelfTableHeader =  ['Gondola','Shelf','SN','IP Addr','Port','Overhead IP','Overhead Port','Batch', \
                        'Device Type','Factory ID','MF Month','MF Day','MF Year','Device Desc']

configFilePath = r'config.ini'  #ini file path
cfg = ConfigParser()
cfg.read(configFilePath)

apiServer = cfg.get('URLs', 'apiServer')
storeID = cfg.get('storedata','storeID')
columnsInShelftable = 14

gondolaColumn = 0
shelfColumn = 1
snColumn = 2
IPAddressColumn = 3
portColumn = 4
overheadIPColumn = 5
overheadPortColumn = 6
batchIDColumn = 7
deviceTypeColumn = 8
factoryColumn = 9

storewideFilterString = "filter=storeid="+str(storeID)

class Ui_MainWindow(object):

    # to install shelf we need the following information
    # factoryID of shelf manufacturer
    # deviceTypeID of shelf
    # mf day, month, year
    # id address
    # port
    shelfList = []

    devicetypeListForCombo = []
    devicetypeDictionary = {}

    factoryListForCombo = []
    factoryDictionary = {}

    shelfDictionary = {}

    batchDictionary = {}

    selectedShelf = {}

    def setupUi(self, MainWindow):
        self.refreshData()
        MainWindow.setObjectName("MainWindow")
        setupUILayout(self,MainWindow)
        retranslateUi(self,MainWindow)
        self.showShelfTable(self.shelfList)
        self.tableWidget.selectRow(0)
        self.onTableCellClicked(0)
    
    def refreshData(self):
        self.shelfList = getPlanogramShelves(apiServer,"filter=storeid="+str(storeID))
        print("self.shelfList=========",self.shelfList)
        self.devicetypeListForCombo = getDeviceTypeListForCombo(apiServer)
        self.devicetypeDictionary = getDictionary(apiServer,"devicetypes","deviceTypeID")

        self.factoryListForCombo = getFactoryListForCombo(apiServer)
        self.factoryDictionary = getDictionary(apiServer,"factorys","factoryID")
        
        self.shelfDictionary = getDictionary2Keyfields(apiServer,"planogramShelves","gondola","shelf")
        
        self.batchDictionary = getDictionary(apiServer,"batches","batchID")

    def showShelfTable(self,shelfList):
        return self.showTable(shelfList,columnsInShelftable,shelfTableHeader,'gondola')

    # show a noneditable table
    def showTable(self,dataSource,numberOfColums,tableHeader=[],keyfield=""):

        if len(dataSource) == 0:
            return False
        
        backColors = [QtGui.QColor(200,200,200),QtGui.QColor(150,150,150)]

        self.tableWidget.setRowCount(len(dataSource))
        self.tableWidget.setColumnCount(numberOfColums+1)
        # .... dbGet_productUPCs
        row = 0
        i = 0
        previousKeyfield = ""

        for item in dataSource:
            if keyfield != "":            
                if previousKeyfield != item[keyfield]:
                    i+=1
                # previous keyfield became current Gondola
                previousKeyfield = item[keyfield]
            

            col = 0
            fillHeader = False
            if len(tableHeader) <= 0: 
                fillHeader = True 

            for attribute, value in item.items():
 
                if col > columnsInShelftable - 1:
                    break
                if fillHeader:
                    tableHeader.append(attribute) 

                self.tableWidget.setItem(row,col, QtWidgets.QTableWidgetItem(str(value)))
                self.tableWidget.item(row,col).setBackground(backColors[i%2])
                # self.tableWidget.item(row,col).setForeground(textColors[j%2])
                col += 1

            tableHeader.append("status")
            # status are  uninstalled -> blank serial number
            #             installed -> serial number ! blank
            #             active -> serial number, IPAddress,port, overheadID, overhead port !=''
            installed = str(self.shelfList[row]["SN"]).strip() != ""
            
            active  = installed and str(self.shelfList[row]["IPAddress"]).strip() != ""  and \
                        str(self.shelfList[row]["port"]).strip() != "" and \
                        str(self.shelfList[row]["overheadshelfIP"]).strip() != "" and \
                        str(self.shelfList[row]["overheadshelfPort"]).strip() != ""
            
            statusColorTable = {'UNINSTALLED':QtGui.QColor(255,0,0),
                                'INSTALLED': QtGui.QColor(0,0,255),
                                'ACTIVE': QtGui.QColor(0,255,0)}
            
            status = "UNINSTALLED"
            if installed:
                status = "INSTALLED" 
            if active:
                status = "ACTIVE"

            mColor = statusColorTable[status]

    
            self.tableWidget.setItem(row,col, QtWidgets.QTableWidgetItem(status)) 
            self.tableWidget.item(row,col).setBackground(backColors[i%2])
            
            self.tableWidget.item(row,col).setForeground(mColor)
            row += 1

        self.tableWidget.setHorizontalHeaderLabels(tableHeader)  

        header = self.tableWidget.horizontalHeader() 
        for i in range(0,columnsInShelftable+1):     
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)    
                
         

        # self.tableWidget.horizontalHeader().resizeSections
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        return True
  
    def onTableCellClicked(self,row):
        print("cell clicked in row = ",str(row))
        # self.shelfRowSelected = row
        self.gondolaSelected = self.tableWidget.item(row,gondolaColumn).text()
        
        try:
            self.shelfLevelSelected = self.tableWidget.item(row,shelfColumn).text()
            self.shelfSelectedRow = self.tableWidget.currentRow()
            self.IPAddress_input.clear()
            self.port_input.clear()

            self.overheadIP_input.clear()
            self.overheadPort_input.clear()

            self.mfMonth.clear()
            self.mfDay.clear()
            self.mfYear.clear()

            self.IPAddress_input.insert(self.tableWidget.item(row,IPAddressColumn).text())
            self.port_input.insert(self.tableWidget.item(row,portColumn).text())

            self.overheadIP_input.insert(self.tableWidget.item(row,overheadIPColumn).text())
            self.overheadPort_input.insert(self.tableWidget.item(row,overheadPortColumn).text())
            
            mDevicetypeID = self.tableWidget.item(row,deviceTypeColumn).text()
            mFactoryID = self.tableWidget.item(row,factoryColumn).text()

            self.cbDeviceTypes.setCurrentText(mDevicetypeID + " " + self.devicetypeDictionary[mDevicetypeID]["deviceTypeName"])
            self.cbFactorys.setCurrentText(mFactoryID + " " + self.factoryDictionary[mFactoryID]["factoryName"])
            
            currentShelf = self.shelfList[row]
        
            self.mfMonth.insert(str(currentShelf["mfDateMonth"]))
            self.mfDay.insert(str(currentShelf["mfDateDay"]))
            self.mfYear.insert(str(currentShelf["mfDateYear"]))
            
            self.selectedShelf = currentShelf

        except:
            print("ERROR IN ONCELLCLICK EVENT") 
            currentShelf = self.shelfList[row]
            self.selectedShelf = currentShelf

        self.tableWidget.selectRow(row)
        self.noticeLabel.setText("Selected:    Gondola: " + self.gondolaSelected + "     Shelf: " + self.shelfLevelSelected + "     TableRow: " + str(self.shelfSelectedRow + 1))   
        self.noticeLabel.setStyleSheet("QLabel {  color : green; }")
    
    def updateOrInstallShelf(self):
        print("in UpdateOrInstallShelf()")
        
        # see if port or ipaddress changed
        # self.selectedShelf is the current selected shelf
        # self.selectedShelfRow is selected row of the table

        isUpdated = False

        # see if any batch related fields have changed:
        # deviceTypeID
        print("self.cbDeviceTypes.currentText().split(' ')[0]=",self.cbDeviceTypes.currentText().split(' ')[0])
        changedDeviceType = self.cbDeviceTypes.currentText().split(' ')[0].strip()
        currentDeviceType = str(self.selectedShelf["deviceTypeID"]).strip()
        changedFactoryID = self.cbFactorys.currentText().split(' ')[0].strip()
        currentFactoryID = str(self.selectedShelf["factoryID"]).strip()
        changedmfDay = str(self.mfDay.text()).strip()
        currentmfDay = str(self.selectedShelf["mfDateDay"]).strip()
        changedmfMonth = str(self.mfMonth.text()).strip()
        currentmfMonth = str(self.selectedShelf["mfDateMonth"]).strip()
        changedmfYear = str(self.mfYear.text()).strip()
        currentmfYear = str(self.selectedShelf["mfDateYear"]).strip()
        
        serialNumber = str(self.selectedShelf["SN"]).strip()

        if changedDeviceType != currentDeviceType or \
           changedFactoryID != currentFactoryID or \
           changedmfDay != currentmfDay or \
           changedmfMonth != currentmfMonth or \
           changedmfYear != currentmfYear:
           
                batchFields = ["mfDateDay","mfDateMonth","mfDateYear","factoryID","deviceTypeID"]
                batchValues = [changedmfDay,changedmfMonth,changedmfYear,changedFactoryID,changedDeviceType]
                print("Changed devicetype or factoryID ")
                # try to  find an existing batch with these criteria
                # if there is none, create a new one
                # factoryID,deviceTypeID,mfMonth, mfDay, mfYear =
                mFilter = "filter=" 
                for i in range(len(batchFields)):
                    conj = ""
                    if i > 0:
                      conj = " and "
                    mFilter += (conj + batchFields[i] + "=" + batchValues[i])
                    

                # [rVal.append(str(dt[field1])+" "+str(dt[field2])) for dt in dtList] 
                foundBatch = getTable(apiServer,"batches",mFilter)
                batchID = -1
                if len(foundBatch) > 0:
                    batchID = foundBatch[0]["batchID"]
                    print ("BatchNumber = ",batchID)
                else:
                    batchID = getMaxBatchID(apiServer) + 1
                    print ("Batch Not Found, new batch ",batchID," will be created") 
                    # create new batch record with the user-entered field data
                    fieldnameList=["factoryID","deviceTypeID","mfDateDay","mfDateMonth","mfDateYear"]
                    valueList=[changedFactoryID,changedDeviceType,changedmfDay,changedmfMonth,changedmfYear]
                    result = updateDatabaseTable(apiServer,"batches",fieldnameList,valueList,"batchID",batchID,"A","")
                # now we generate serialnumber based on batch and add 
                # a hardwareID record for this shelf
                serialNumber = generateSerialNumber(batchID)
                print("serialNumber = ", serialNumber)
                fieldnameList=["batchID","serialnumber","address","counter"]
                valueList=[batchID,serialNumber,"0","0"]
                result = updateDatabaseTable(apiServer,"hardwareids",fieldnameList,valueList,"hardwareID",0,"A","")

                isUpdated = True

        if (self.IPAddress_input.text().strip() != self.selectedShelf["IPAddress"] or \
            self.port_input.text().strip() != self.selectedShelf["port"]) or \
            self.overheadIP_input.text().strip() != self.selectedShelf["overheadshelfIP"] or \
            self.overheadPort_input.text().strip() != self.selectedShelf["overheadshelfPort"] or \
            isUpdated:
                print("Shelf data has changed, updating shelf Record")
                shelfID = self.selectedShelf["shelfID"]
                fieldnameList = ["IPAddress","port","overheadshelfIP","overheadshelfPort","SN"]
                valueList = [self.IPAddress_input.text().strip(),self.port_input.text().strip(),self.overheadIP_input.text().strip(),self.overheadPort_input.text().strip(),str(serialNumber).strip()]
                result = updateDatabaseTable(apiServer,"shelfs",fieldnameList,valueList,"shelfID",0,"E","shelfID=" + str(shelfID))
                isUpdated = True

        if isUpdated:
                self.refreshData()
                self.showShelfTable(self.shelfList)

    def restoreShelf(self):
        self.onTableCellClicked(self.shelfSelectedRow)

    def exitApp(self):
        QtWidgets.QApplication.quit()
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Windows')
   
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())