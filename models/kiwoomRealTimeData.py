import interface.observerOrderQueue as observer
import datetime
import models.accountData as AccountData
import models.order as Order

class KiwoomRealTimeData(observer.Subject):
    kiwoom = None
    def __init__(self,kiwoom,condition):
        print("real time data"+condition['종목코드'])
        super().__init__()
        self.kiwoom = kiwoom
        self._observer_list = []
        # 실시간 데이터 슬롯 등록
        self.kiwoom.OnReceiveRealData.connect(self._handler_real_data)
        self.code = condition['종목코드']
        self.codeName = condition['종목명']
        self.buyPrice = condition['매수가']
        self.totalBuyAmount = int(condition['총금액'])
        self.buyStartTime = str(condition['시작시간'])
        self.buyEndTime = str(condition['종료시간'])
        self.profitRate = float(condition['부분익절율'])
        self.profitSellVolume = int(condition['부분익절수량'])
        self.maxProfitRate = float(condition['최대익절율'])
        self.lossRate = float(condition['부분손절율'])
        self.lossSellVolume = int(condition['부분손절수량'])
        self.maxLossRate = float(condition['최대손절율'])

        print("생성할때는 제대로 되나?11111111")
        self.accountData = AccountData.AccountData(kiwoom)
        # 평가잔고 정보 가져오기
        self.updateAccountDate()

    def register_observer(self, observer):
        if observer in self._observer_list:
            return "Already exist observer!"
        self._observer_list.append(observer)
        return "Success register!"

    def remove_observer(self, observer):
        if observer in self._observer_list:
            self._observer_list.remove(observer)
            return "Success remove!"
        return "observer does not exist."

    def notify_observers(self,order):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        print("kiwoomRealTimeData notify observer")
        source = "kiwoomRealTimeData"
        for observer in self._observer_list:
            observer.update(source,order)


    def updateAccountDate(self):
        self.balanceDf = self.accountData.get_account_evaluation_balance()
        # self.dataRows = None
        # for idx, row in self.balanceDf.iterrows():
        #     if row['종목코드'] == self.code:
        #         self.dataRows = row
        self.currentProfitRate = 0
        self.buyTotalMoney = 0
        self.canSellVolume = 0
        self.dataRows = self.balanceDf[self.balanceDf['종목코드'] == self.code]
        if not self.dataRows.empty:
            print(str(self.dataRows))
            self.currentProfitRate = float(self.dataRows['수익율(%)'][0])
            self.buyTotalMoney = int(self.dataRows['매입금액'][0])
            self.canSellVolume = int(self.dataRows['매매가능수량'][0])
            print("평가잔고 정보 가쟈오기" + "\n" + str(self.currentProfitRate) + "\n" + str(self.buyTotalMoney) + "\n" + str(
                self.canSellVolume))

    def run(self):
        # 주식체결 (실시간)
        self.subscribe_market_time('1')
        self.subscribe_stock_conclusion('2')

    def subscribe_stock_conclusion(self, screen_no):
        self.SetRealReg(screen_no, self.code, "20", 0)
        #fid 20는 주식체결 관련 체결시간

    def subscribe_market_time(self, screen_no):
        self.SetRealReg(screen_no, "", "215", 0)
        #fid 215는 장시작시간

    # 실시간 타입을 위한 메소드
    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
        self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", 
                              screen_no, code_list, fid_list, real_type)

    def GetCommRealData(self, code, fid):
        data = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, fid) 
        return data

    def DisConnectRealData(self, screen_no):
        self.kiwoom.dynamicCall("DisConnectRealData(QString)", screen_no)
        
        
    # 실시간 이벤트 처리 핸들러
    def _handler_real_data(self, code, real_type, real_data):
        if real_type == "주식체결":
            # 현재가격
            currentPrice = self.GetCommRealData(code, 10)
            currentPrice = abs(int(currentPrice))          # +100, -100
            time = self.GetCommRealData(code, 20)
            print("currentPrice"+str(currentPrice))
            # 시장가
            # marketPrice = self.GetCommRealData(code, 16)
            # marketPrice= abs(int(marketPrice))          # +100, -100

            startTime = datetime.datetime.strptime(self.buyStartTime, '%H:%M')
            endTime = datetime.datetime.strptime(self.buyEndTime, '%H:%M')
            now = datetime.datetime.now()

            #매수로직
            #1. 현재시간이 시작과 종료시간 사이인지
            #2. 총보유금액이 총금액 조건 미만인지
            #3. 현재가격이 목표가(매수가)보다 크거나 같은지.
            #4. 목표가로 구매하는 주문 생성
            if (startTime.time()<now.time()) and (now.time()<endTime.time()):
                if (self.totalBuyAmount >= self.buyTotalMoney):
                   if currentPrice >= self.buyPrice:
                       print("create buy order")
                       #최대 구매할수 있는 금액에서 현재보유하고 있는량을 제외하고 남은 금액을 현재가로 나눈만큼 구매
                       buyVolume = int((self.totalBuyAmount - self.buyTotalMoney)/currentPrice)
                       buy_order = Order.Order("현재가매수", "0101", self.accountData.getAccountInfo(), 1, code, self.codeName,buyVolume,
                                                self.buyPrice, "00", "",self.profitRate,self.lossRate,self.currentProfitRate,now)
                       # 주문생성시만 어카운트 정보 업데이트
                       self.updateAccountDate()
                       self.notify_observers(buy_order)


            #매도로직
            # 1. 수익율이 최대수익율보다 크거나 같으면 거래량은 매매가능수량
            # 2. 수익율이 최대익절율보다 작고 부분익절율보다 크거나 같으면 거래량은 매매가능수량 * 부분익절량
            # 3. 수익율이 최대손절율보다 크거나 같고 부분손절율보다 작으면 거래량은 매매가능수량 * 부분손절량
            # 4. 수익율이 최대손절율보다 작거나 같으면 거래량은 매매가능수량

            sellVolume = 0
            trySell = False
            if self.currentProfitRate >= self.maxProfitRate:
                sellVolume = self.canSellVolume
                trySell = True
            elif (self.currentProfitRate < self.maxProfitRate) and (self.currentProfitRate >= self.profitRate):
                sellVolume = int(self.canSellVolume * self.profitSellVolume)
                trySell = True
            elif (self.currentProfitRate >= self.maxLossRate) and (self.currentProfitRate < self.lossRate):
                sellVolume = int(self.canSellVolume * self.lossSellVolume)
                trySell = True
            elif self.currentProfitRate <= self.maxLossRate:
                sellVolume = self.canSellVolume
                trySell = True

            print("create sell order")
            if trySell:
                sell_order = Order.Order("현재가매도","0102",self.accountData.getAccountInfo(),2,code,self.codeName,sellVolume,currentPrice,"00","",self.profitRate,self.lossRate,self.currentProfitRate,now)
                #주문생성시만 어카운트 정보 업데이트
                self.updateAccountDate()
                self.notify_observers(sell_order)
            #SendOrder(BSTR sRQName, // 사용자 구분명
            # BSTR sScreenNo, // 화면번호
            # BSTR sAccNo,  // 계좌번호 10자리
            # LONG nOrderType,  // 주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
            # BSTR sCode, // 종목코드 (6자리)
            # LONG nQty,  // 주문수량
            # LONG nPrice, // 주문가격
            # BSTR sHogaGb,   // 거래구분(혹은 호가구분)은 아래 참고
            # BSTR sOrgOrderNo  // 원주문번호. 신규주문에는 공백 입력, 정정/취소시 입력합니다.
            # )
                # self.hold = True
                # quantity = int(self.amount / 현재가)
                # self.SendOrder("매수", "8000", self.account, 1, "229200", quantity, 0, "03", "")
                # print(f"시장가 매수 진행 수량: {quantity}")

            # 로깅
            # print(f"시간: {체결시간} 목표가: {self.target} 현재가: {현재가}")