from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import pandas

class AccountData():
    kiwoom = None
    arr = []
    def __init__(self,kiwoom):
        super().__init__()
        self.kiwoom = kiwoom
        #이벤트 루프 등록
        self.account_event_loop = QEventLoop()

        # 계좌 관련 변수
        self.account_number = None
        self.total_buy_money = 0
        self.total_evaluation_money = 0
        self.total_evaluation_profit_and_loss_money = 0
        self.total_yield = 0
        self.account_stock_dict = {}

        # 종목 분석 관련 변수
        self.balance_list = {'index': [], 'code': [], 'name': [], 'eval': [], 'roi': [], 'buy': [], 'volume': [],
                             'can_order': [], 'current_price': []}

        # 화면 번호
        self.screen_my_account = "1000"

        #이벤트 TR슬롯 등록록
        self.event_collection()
        self.get_account_info()  # 계좌 번호만 얻어오기
        self.get_account_evaluation_balance()  # 계좌평가잔고내역 얻어오기


    def getAccountInfo(self):
        return self.account_number

    def getBalanceInfo(self):
        return self.df


    def event_collection(self):
        self.kiwoom.OnReceiveTrData.connect(self.tr_slot)  # 트랜잭션 요청 관련 이벤트

    #계좌정보 얻어오기
    def get_account_info(self):
        account_list = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCLIST")
        account_number = account_list.split(';')[0]
        self.account_number = account_number
        print(self.account_number)

    #잔고정보 요청
    def get_account_evaluation_balance(self, nPrevNext=0):
        print("self.account_number"+self.account_number)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)",
                         "계좌번호", self.account_number)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", " ")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "계좌평가잔고내역요청", "opw00018", nPrevNext, self.screen_my_account)

        if not self.account_event_loop.isRunning():
            self.account_event_loop.exec_()

    def tr_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        if sRQName == "계좌평가잔고내역요청":
            if (self.total_buy_money == None or self.total_evaluation_money == None
                    or self.total_evaluation_profit_and_loss_money == None or self.total_yield == None):
                total_buy_money = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
                self.total_buy_money = int(total_buy_money)

                total_evaluation_money = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액")
                self.total_evaluation_money = int(total_evaluation_money)

                total_evaluation_profit_and_loss_money = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액")
                self.total_evaluation_profit_and_loss_money = int(
                    total_evaluation_profit_and_loss_money)

                total_yield = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
                self.total_yield = float(total_yield)

            cnt = self.kiwoom.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            for i in range(cnt):
                stock_code = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                stock_code = stock_code.strip()[1:]

                stock_name = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_name = stock_name.strip()  # 필요 없는 공백 제거.

                stock_evaluation_profit_and_loss = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "평가손익")
                stock_evaluation_profit_and_loss = int(
                    stock_evaluation_profit_and_loss)

                stock_yield = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                stock_yield = float(stock_yield)

                stock_buy_money = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                stock_buy_money = int(stock_buy_money)

                stock_quantity = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                stock_quantity = int(stock_quantity)

                stock_trade_quantity = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")
                stock_trade_quantity = int(stock_trade_quantity)

                stock_present_price = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                stock_present_price = int(stock_present_price)

                if not stock_code in self.account_stock_dict:
                    self.account_stock_dict[stock_code] = {}

                self.balance_list['index'].append(i)
                self.balance_list['code'].append(stock_code)
                self.balance_list['name'].append(stock_name)
                self.balance_list['eval'].append(stock_evaluation_profit_and_loss)
                self.balance_list['roi'].append(stock_yield)
                self.balance_list['buy'].append(stock_buy_money)
                self.balance_list['volume'].append(stock_quantity)
                self.balance_list['can_order'].append(stock_trade_quantity)
                self.balance_list['current_price'].append(stock_present_price)
                # self.account_stock_dict[stock_code].update({'종목명': stock_name})
                # self.account_stock_dict[stock_code].update(
                #     {'평가손익': stock_evaluation_profit_and_loss})
                # self.account_stock_dict[stock_code].update(
                #     {'수익률(%)': stock_yield})
                # self.account_stock_dict[stock_code].update(
                #     {'매입가': stock_buy_money})
                # self.account_stock_dict[stock_code].update(
                #     {'보유수량': stock_quantity})
                # self.account_stock_dict[stock_code].update(
                #     {'매매가능수량': stock_trade_quantity})
                # self.account_stock_dict[stock_code].update(
                #     {'현재가': stock_present_price})

            if sPrevNext == "2":
                self.get_account_evaluation_balance(2)
            else:
                self.cancel_screen_number(self.screen_my_account)
                self.account_event_loop.exit()
                self.df = pandas.DataFrame(self.balance_list,
                                      columns=['index', 'code', 'name', 'eval', 'roi', 'buy', 'volume', 'can_order','current_price'])
                self.df.set_index("index", inplace=True)
                print("account balance",self.df)

        # elif sRQName == "예수금상세현황요청":
        #     deposit = self.kiwoom.dynamicCall(
        #         "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")
        #     self.deposit = int(deposit)
        #
        #     withdraw_deposit = self.kiwoom.dynamicCall(
        #         "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
        #     self.withdraw_deposit = int(withdraw_deposit)
        #
        #     order_deposit = self.kiwoom.dynamicCall(
        #         "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "주문가능금액")
        #     self.order_deposit = int(order_deposit)
        #     self.cancel_screen_number(self.screen_my_account)
        #     self.kiwoom.account_event_loop.exit()

    def cancel_screen_number(self, sScrNo):
        self.kiwoom.dynamicCall("DisconnectRealData(QString)", sScrNo)