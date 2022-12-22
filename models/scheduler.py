#-*- coding: utf-8 -*-
import schedule
import time
import requests
import pandas
import models.database as Database
import openJson

class Scheduler():
    def __init__(self):
        self.msg, self.params = openJson.getJsonFiles()
        self.dataManager = Database.Database()
        schedule.every().day.at("08:50").do(self.job)
        schedule.every().day.at("15:20").do(self.job)

    def job(self):
        codeVal = self.params['kiwoomRealTimeData']['piggleDaoMostVotedList']['code']
        nameVal = self.params['kiwoomRealTimeData']['piggleDaoMostVotedList']['name']
        expectedPriceVal = self.params["mainWindow"]["createPiggleDaoMostVotedFile"]["expectedPrice"]
        priceTypeVal = self.params["mainWindow"]["createPiggleDaoMostVotedFile"]["priceType"]
        expectedDateVal = self.params["mainWindow"]["createPiggleDaoMostVotedFile"]["expectedDate"]
        openVal = self.params['kiwoomRealTimeData']['piggleDaoMostVotedList']['open']
        closeVal = self.params['kiwoomRealTimeData']['piggleDaoMostVotedList']['close']

        params = []
        params.append("Open")
        params.append("Close")
        list = {codeVal: [], nameVal: [], expectedPriceVal: [], priceTypeVal: [], expectedDateVal: []}
        num = 0
        for i in params:
            url = "https://piggle-dao.shop/forecast/selectMostVotedAppInfoList?type="+i
            response = requests.get(url)
            arr = response.json()['stock_info_arr']
            for j in arr:
                stockCode = j['stockCode']
                stockName = j['stockName']
                price = j['price']
                forecastDate = j['forecastDate']
                if i == "Open":
                    type = openVal
                else:
                    type = closeVal
                list[codeVal].append(stockCode)
                list[nameVal].append(stockName)
                list[expectedPriceVal].append(price)
                list[priceTypeVal].append(type)
                list[expectedDateVal].append(forecastDate)
                num += 1
        df = pandas.DataFrame(list, columns=[codeVal, nameVal, expectedPriceVal, priceTypeVal, expectedDateVal])
        self.dataManager.updateCSVFile('pats_piggle_dao_most_voted.csv', df)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)