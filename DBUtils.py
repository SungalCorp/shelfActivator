

import json,requests

def getShelfIDByGondolaIDAndLevel(apiServer,gondolaID,level):
	filter = "filter=displayfixtureID="+str(gondolaID)+ " AND level=" + str(level)
	rTable = getTable(apiServer,"shelfs",filter)
	if  len(rTable) > 0:
		return rTable[0]["shelfID"]
		
	return -1

def deleteRecord(apiServer,tableName,filter):
	url = apiServer + "dbExecuteSQL?sqlstatement=delete from " + tableName 
	if len(filter) > 0:
		url += (" where " + filter)
	
	resultTable = json.loads(requests.get(url).text)
	return resultTable
	
def addRecord(apiServer,tableName,fields,fieldVals):
    
	url = apiServer + "dbInsert?tablename=" + tableName + "&fields={"
	URLAddon=""
	for i in range(len(fields)):
		URLAddon += ('"' + fields[i] + '":"' + str(fieldVals[i]) + '",')

	URLAddon = URLAddon[:len(URLAddon)-1]
	url += (URLAddon + "}")
	return json.loads(requests.get(url).text)

def getPlanogramShelves(apiServer,filter):
	return getTable(apiServer,"planogramShelves",filter)

def getDeviceTypeListForCombo(apiServer):
	# dtList =  getTable(apiServer,"devicetypes","filter=deviceTypeID>=3000")
	# rVal = []
	# [rVal.append(str(dt["deviceTypeID"])+" "+str(dt["deviceTypeName"])) for dt in dtList]
	# return rVal
	return getListForCombo(apiServer,"devicetypes","deviceTypeID","deviceTypeName","filter=deviceTypeID>=3000")

def  getFactoryListForCombo(apiServer):
	return getListForCombo(apiServer,"factorys","factoryID","factoryName","")


def getListForCombo(apiServer,tableName,field1,field2,filter):
	dtList =  getTable(apiServer,tableName,filter)
	rVal = []
	[rVal.append(str(dt[field1])+" "+str(dt[field2])) for dt in dtList]
	return rVal

def getTable(apiServer,tableName,filter):

	url = apiServer + 'dbGet_' + tableName 
	if len(filter) > 0:
		url += '?' + filter
	try:
		resultTable = json.loads(requests.get(url).text)
	except:
		print("Error loading data")
		return []

	
	return [p for p in resultTable ]

# can be consolidated if we pass in list of keyFields of size 1 to n
def getDictionary(apiServer,tableName,keyField):
	rVal = {}
	resultDataSet = getTable(apiServer,tableName,"")
	for record in resultDataSet:
		rVal[str(record[keyField])] = record           
	return rVal

def getDictionary2Keyfields(apiServer,tableName,keyField1,keyField2):
	rVal = {}
	resultDataSet = getTable(apiServer,tableName,"")
	for record in resultDataSet:
		rVal[str(record[keyField1]) + " " + str(record[keyField2])] = record           
	return rVal

def getMaxBatchID(apiServer):
	resultset = getTable(apiServer,'maxBatchID','')
	# print ("resultset for getMaxBatchID =", resultset)
	return resultset[0]["maxbatchID"]

# // example:
# //
# //dbInsert?tablename=displayfixtures&fields={"storeID":1,"level":1,"displayfixtureIDForUser":"testertest","type":"gondola","location":"Detroit"}
# modify this code to do both update and insert

# result = updateDatabaseTable(apiServer,tableName,fieldnameList,valueList,keyField,nextIDValue,self.changeMode,keyField + "=" + str(selectedID))

def updateDatabaseTable(apiServer,tableName,fields,fieldVals,keyField,nextIDValue,changeMode,filter):
    #changeMode is either "A" or "E" for add edit
	operation = ""
	addKeyfieldAddon = ""
	
	# nextIDValue = 0
	URLAddon = '&fields={'
	
	if changeMode.upper()=="A":   #we are adding
		operation = "dbInsert"
		filter = ""
		
		# if (tableName.upper() == "BATCHES"):
			# keyField = "batchID"
			# nextIDValue = getMaxBatchID(apiServer) + 1
		#if (tableName.upper() == "DEVICETYPES"):
			# keyField = "deviceTypeID"	
			# nextIDValue = getMaxDeviceTypeID(apiServer) + 1
		if nextIDValue != 0:
			addKeyfieldAddon = '"' + keyField + '":"' + str(nextIDValue) + '",'
			URLAddon += addKeyfieldAddon

	if changeMode.upper()=="E":
		operation = "dbUpdate"

	

	for i in range(len(fields)):
		URLAddon += ('"' + fields[i] + '":"' + str(fieldVals[i]) + '",')
	# now fill  in  the keyfield for adds
	updateBatchURL = apiServer + operation + "?tablename=" + tableName + URLAddon 
	
	# print("maxbatchID =",getMaxBatchID(apiServer))
	# print("maxDeviceTypeID(apiServer)=",getMaxDeviceTypeID(apiServer))


	filtExp = ""
	if filter !="":	
		filtExp = "&filter=" + filter

	updateBatchURL = updateBatchURL[:len(updateBatchURL)-1] + "}" + filtExp

	print("UPDATING URL = ",updateBatchURL)
	return requests.get(updateBatchURL)
