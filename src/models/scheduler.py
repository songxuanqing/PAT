import schedule
import time
import requests
import pandas
import models.database as Database

class Scheduler():
    def __init__(self):
        self.dataManager = Database.Database()
        schedule.every().day.at("08:50").do(self.job)
        schedule.every().day.at("15:20").do(self.job)

    def job(self):
        params = []
        params.append("Open")
        params.append("Close")
        list = {'코드': [], '종목명': [], '예상가': [], '시종가구분': [], '예측일': []}
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
                    type = "시가"
                else:
                    type = "종가"
                list['코드'].append(stockCode)
                list['종목명'].append(stockName)
                list['예상가'].append(price)
                list['시종가구분'].append(type)
                list['예측일'].append(forecastDate)
                num += 1
        df = pandas.DataFrame(list, columns=['코드', '종목명', '예상가', '시종가구분', '예측일'])
        self.dataManager.updateCSVFile('pats_piggle_dao_most_voted.csv', df)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)