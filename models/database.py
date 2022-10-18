import csv
import os
import pandas as pd

class Database():
    def __init__(self):
        print("create database")

    def createCSVFile(self,filename,columnArray):
        print(""+os.path.abspath(os.getcwd()))
        if os.path.exists(os.path.abspath(os.getcwd())+"\\"+filename)==False:
            print("CreateCSVFile")
            f = open(filename,'a', newline='')
            wr = csv.writer(f)
            wr.writerow(columnArray)
            f.close()

    def appendCSVFile(self,filename,df):
        df.to_csv(filename, mode='a', encoding='cp949', header=False, index=False)
        # with open(filename, 'a', newline='') as f:
        #     wr = csv.writer(f)
        #     wr.writerow(dataArray)
        #     f.close()

    def readCSVFile(self,filename):
        # df = pd.read_csv(filename,dtype ='str',encoding='cp949')
        # return df
        df = pd.read_csv(
            filename,encoding='cp949',
            converters={
                "종목코드": str,  # Ensure serialno is read as string, maintaining leading 0's
            })
        return df
        # f = open(filename, 'r', encoding='utf-8')
        # rdr = csv.reader(f)
        # for line in rdr:
        #     print(line)
        # f.close()
        #rows를 dataframe으로 리턴한다.

