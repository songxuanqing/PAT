_B='cp949'
_A=False
import csv,os,pandas as pd,openJson
class Database:
	def __init__(A):print('');A.msg,A.params=openJson.getJsonFiles()
	def createCSVFile(D,filename,columnArray):
		A=filename
		if os.path.exists(os.path.abspath(os.getcwd())+'\\'+A)==_A:B=open(A,'a',newline='');C=csv.writer(B);C.writerow(columnArray);B.close()
	def appendCSVFile(A,filename,df):df.to_csv(filename,mode='a',encoding=_B,header=_A,index=_A)
	def updateCSVFile(A,filename,df):df.to_csv(filename,mode='w',encoding=_B,header=True,index=_A)
	def readCSVFile(A,filename):B=A.params['kiwoomRealTimeData']['conditionList']['code'];C=pd.read_csv(filename,encoding=_B,converters={B:str});return C
	def removeRows(A,filename,df):df.to_csv(filename,mode='w',encoding=_B,header=True,index=_A)