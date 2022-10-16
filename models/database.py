import csv
import os

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

    def appendCSVFile(self,filename,dataArray):
        with open(filename, 'a', newline='') as f:
            wr = csv.writer(f)
            wr.writerow(dataArray)
            f.close()

    def readCSVFile(self,filename):
        print("read file")
        #rows를 dataframe으로 리턴한다.

