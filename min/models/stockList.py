class StockList:
	kiwoom=None;arr=[]
	def __init__(A,kiwoom):A.kiwoom=kiwoom;A.setList('0')
	def setList(A,market):
		C=A.kiwoom.dynamicCall('GetCodeListByMarket(QString)',[market]);D=C.split(';')
		for B in D:
			E=A.kiwoom.dynamicCall('GetMasterCodeName(QString)',[B])
			if B!='':A.arr.append(B+' : '+E)
	def getList(A):return A.arr
	def add(A,item):A.arr.append(item)