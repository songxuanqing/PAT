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

    def updateCSVFile(self,filename,df):
        df.to_csv(filename, mode='w', encoding='cp949', header=True, index=False)
        # fileDf = pd.read_csv(
        #     filename, encoding='cp949',
        #     converters={
        #         "종목코드": str,  # Ensure serialno is read as string, maintaining leading 0's
        #     })
        # fileDf[key] = df
        # lines = []
        # # 파일을 열어 열들을 가지고 온다음 각 열의 행을 검사한다. 행이 키와 같으면 해당 열을 삭제하고 다시 저장한다.
        #
        # with open(filename, 'a', encoding='cp949') as writeFile:
        #     writer = csv.writer(writeFile)
        #     writer.writerows(lines)


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

    def removeRows(self,filename,df):
        df.to_csv(filename, mode='w', encoding='cp949', header=True, index=False)
        # lines = []
        # #파일을 열어 열들을 가지고 온다음 각 열의 행을 검사한다. 행이 키와 같으면 해당 열을 삭제하고 다시 저장한다.
        # with open(filename, 'r',encoding='cp949') as readFile:
        #     reader = csv.reader(readFile)
        #     for row in reader:
        #         lines.append(row)
        #         for id in row:
        #             for key in keys:
        #                 if id == key:
        #                     lines.remove(row)
        # #처음 컬럼생성하기
        #
        # with open(filename, 'a',encoding='cp949') as writeFile:
        #     writer = csv.writer(writeFile)
        #     writer.writerows(lines)

