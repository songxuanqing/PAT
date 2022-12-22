#-*- coding: utf-8 -*-
import csv
import os
import pandas as pd
import openJson

class Database():
    def __init__(self):
        print("")
        self.msg, self.params = openJson.getJsonFiles()

    def createCSVFile(self,filename,columnArray):
        if os.path.exists(os.path.abspath(os.getcwd())+"\\"+filename)==False:
            f = open(filename,'a', newline='')
            wr = csv.writer(f)
            wr.writerow(columnArray)
            f.close()

    def appendCSVFile(self,filename,df):
        df.to_csv(filename, mode='a', encoding='cp949', header=False, index=False)


    def updateCSVFile(self,filename,df):
        df.to_csv(filename, mode='w', encoding='cp949', header=True, index=False)


    def readCSVFile(self,filename):
        codeVal = self.params['kiwoomRealTimeData']['conditionList']['code']
        df = pd.read_csv(
            filename,encoding='cp949',
            converters={
                codeVal: str,  # Ensure serialno is read as string, maintaining leading 0's
            })
        return df


    def removeRows(self,filename,df):
        df.to_csv(filename, mode='w', encoding='cp949', header=True, index=False)

