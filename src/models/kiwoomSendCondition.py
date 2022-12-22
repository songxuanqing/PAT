# import datetime
# import models.accountData as AccountData
# import models.order as Order
# import interface.observerOrderQueue as observer
# import interface.observerAccount as observerAccount
#
#
# class KiwoomSendCondition(observer.Subject, observerAccount.Observer):
#     def __init__(self,kiwoom,kiwoomData,conditionList):
#         self.kiwoom = kiwoom
#         self.conditionList = conditionList
#
#         self.ItypeList = []
#         self.buyRequest = []
#         self.sellRequest = []
#         self._observer_list = []
#         self._subject_list = []
#
#         self.kiwoom.OnReceiveRealCondition.connect(self._handler_real_condition)
#         self.kiwoom.OnReceiveRealData.connect(self._handler_real_data)
#
#
#         self.index = condition['코드']
#         self.name = condition['조건명']
#
#         self.totalBuyAmount = int(condition['총금액'])
#         self.buyStartTime = str(condition['시작시간'])
#         self.buyEndTime = str(condition['종료시간'])
#         self.profitRate = float(condition['부분익절율'])
#         self.profitSellVolume = int(condition['부분익절수량']) * 0.01
#         self.maxProfitRate = float(condition['최대익절율'])
#         self.lossRate = float(condition['부분손절율'])
#         self.lossSellVolume = int(condition['부분손절수량']) * 0.01
#         self.maxLossRate = float(condition['최대손절율'])
#
#         self.accountData = kiwoomData
#         self.register_subject_account(self.accountData)
#         # 평가잔고 정보 가져오기
#         # self.updateAccountData()
#
#         self.SendCondition("300", self.name, self.index, 1)
#
#
#
#     def register_observer(self, observer):
#         if observer in self._observer_list:
#             return "Already exist observer!"
#         self._observer_list.append(observer)
#         return "Success register!"
#
#     def remove_observer(self, observer):
#         if observer in self._observer_list:
#             self._observer_list.remove(observer)
#             return "Success remove!"
#         return "observer does not exist."
#
#     def notify_observers(self,order):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
#         print("kiwoomSendConditionData notify observer")
#         source = "kiwoomSendCondition"
#         for observer in self._observer_list:
#             observer.update(source,order)
#
#     def update_account(self, df):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
#         self.balanceDf = df
#         # self.updateAccountData(df)
#         print("condition" + str(df))
#
#     def register_subject_account(self, subject):
#         self.subject = subject
#         self.subject.register_observer_account(self)
#
#     def updateAccountData(self,df):
#         print("kiwoomSendCondition")
#         # self.accountData.get_account_evaluation_balance()
#         self.balanceDf = df
#         # self.currentProfitRate = 0
#         # self.buyTotalMoney = 0
#         # self.canSellVolume = 0
#         # self.dataRows = self.balanceDf[self.balanceDf['코드'] == self.code]
#         # if not self.dataRows.empty:
#         #     print(str(self.dataRows))
#         #     self.currentProfitRate = float(self.dataRows['수익율(%)'])
#         #     self.buyTotalMoney = int(self.dataRows['매입금액'])
#         #     self.canSellVolume = int(self.dataRows['매매가능수량'])
#         #     print("평가잔고 정보 가쟈오기" + "\n" + str(self.currentProfitRate) + "\n" + str(self.buyTotalMoney) + "\n" + str(
#         #         self.canSellVolume))
#
#     def _handler_real_condition(self, code, type, cond_name, cond_index):
#         if cond_name == self.name:
#             print("조건 반환"+cond_name, code, type)
#             # test 014470 I
#             if type == 'I':
#                 self.ItypeList.append(code)
#                 self.SetRealReg("300", self.code, "20", 1)
#
#     def SetRealReg(self, screen_no, code_list, fid_list, real_type):
#         self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)",
#                               screen_no, code_list, fid_list, real_type)
#
#     def SetRemoveReg(self, screen_no, code_list):
#         self.kiwoom.dynamicCall("SetRealRemove(QString,QString)",screen_no,code_list)
#
#     def GetCommRealData(self, code, fid):
#         data = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, fid)
#         return data
#
#     def SendCondition(self, screen, cond_name, cond_index, search):
#         print("조건 보냄")
#         ret = self.kiwoom.dynamicCall("SendCondition(QString, QString, int, int)", screen, cond_name, cond_index, search)
#         print(str(ret))
#
#     def SendConditionStop(self, screen, cond_name, cond_index):
#         ret = self.kiwoom.dynamicCall("SendConditionStop(QString, QString, int)", screen, cond_name, cond_index)
#
#     # def updateAccountData(self,code):
#     #     # self.accountData.get_account_evaluation_balance()
#     #     self.balanceDf = self.accountData.getBalanceInfo()
#     #     self.currentProfitRate = 0
#     #     self.buyTotalMoney = 0
#     #     self.canSellVolume = 0
#     #     self.dataRows = self.balanceDf[self.balanceDf['코드'] == code]
#     #     if not self.dataRows.empty:
#     #         print(str(self.dataRows))
#     #         self.currentProfitRate = float(self.dataRows['수익율(%)'])
#     #         self.buyTotalMoney = int(self.dataRows['매입금액'])
#     #         self.canSellVolume = int(self.dataRows['매매가능수량'])
#     #         print("평가잔고 정보 가쟈오기" + "\n" + str(self.currentProfitRate) + "\n" + str(self.buyTotalMoney) + "\n" + str(
#     #             self.canSellVolume))
#
#     def _handler_real_data(self, code, real_type, real_data):
#         if code in self.ItypeList:
#             # 현재가격
#             currentPrice = self.GetCommRealData(code, 10)
#             currentPrice = abs(int(currentPrice))          # +100, -100
#             time = self.GetCommRealData(code, 20)
#             print("currentPrice"+str(currentPrice)+"code"+self.code)
#             # 시장가
#             # marketPrice = self.GetCommRealData(code, 16)
#             # marketPrice= abs(int(marketPrice))          # +100, -100
#
#             startTime = datetime.datetime.strptime(self.buyStartTime, '%H:%M')
#             endTime = datetime.datetime.strptime(self.buyEndTime, '%H:%M')
#             now = datetime.datetime.now()
#
#             balanceDf = self.balanceDf
#             currentProfitRate = 0
#             buyTotalMoney = 0
#             canSellVolume = 0
#             dataRows = balanceDf[balanceDf['코드'] == code]
#             if not dataRows.empty:
#                 print(str(dataRows))
#                 currentProfitRate = float(dataRows['수익율(%)'])
#                 buyTotalMoney = int(dataRows['매입금액'])
#                 canSellVolume = int(dataRows['매매가능수량'])
#                 print("평가잔고 정보 가쟈오기" + "\n" + str(currentProfitRate) + "\n" + str(buyTotalMoney) + "\n" + str(
#                     canSellVolume))
#
#             # if not self.isBuyOrdered:
#             # 매수로직
#             # 1. 현재시간이 시작과 종료시간 사이인지
#             # 2. 총보유금액이 총금액 조건 미만인지
#             # 3. 현재가격이 목표가(매수가)보다 크거나 같은지.
#             # 4. 목표가로 구매하는 주문 생성
#             if (startTime.time() < now.time()) and (now.time() < endTime.time()):
#                 if (self.totalBuyAmount >= buyTotalMoney):
#                     # 최대 구매할수 있는 금액에서 현재보유하고 있는량을 제외하고 남은 금액을 현재가로 나눈만큼 구매
#                     buyVolume = int((self.totalBuyAmount - buyTotalMoney) / currentPrice)
#                     if buyVolume > 1:
#                         print("create buy order")
#                         print(str(self.totalBuyAmount))
#                         print(str(buyTotalMoney))
#                         print(str(currentPrice))
#                         print(str(int((self.totalBuyAmount - buyTotalMoney) / currentPrice)))
#                         buy_order = Order.Order("현재가매수", "0101", self.accountData.getAccountInfo(), 1, code,
#                                                 self.codeName, buyVolume,
#                                                 currentPrice, "00", "", self.profitRate, self.lossRate,
#                                                 currentProfitRate, now)
#                         # 주문생성시만 어카운트 정보 업데이트
#                         self.notify_observers(buy_order)
#                         self.buyRequest.append(code)
#                         # self.updateAccountData()
#                         # self.isBuyOrdered = True
#                         # self.isSellOrdered = False
#
#             # if not self.isSellOrdered or (self.canSellVolume > 0):
#             print("able to sell")
#             # 매도로직
#             # 1. 수익율이 최대수익율보다 크거나 같으면 거래량은 매매가능수량
#             # 2. 수익율이 최대익절율보다 작고 부분익절율보다 크거나 같으면 거래량은 매매가능수량 * 부분익절량
#             # 3. 수익율이 최대손절율보다 크거나 같고 부분손절율보다 작으면 거래량은 매매가능수량 * 부분손절량
#             # 4. 수익율이 최대손절율보다 작거나 같으면 거래량은 매매가능수량
#             sellVolume = 0
#             trySell = False
#             if currentProfitRate >= self.maxProfitRate:
#                 sellVolume = canSellVolume
#                 trySell = True
#             elif (currentProfitRate < self.maxProfitRate) and (currentProfitRate >= self.profitRate):
#                 sellVolume = int(canSellVolume * self.profitSellVolume)
#                 trySell = True
#             elif (currentProfitRate >= self.maxLossRate) and (currentProfitRate < self.lossRate):
#                 sellVolume = int(canSellVolume * self.lossSellVolume)
#                 trySell = True
#             elif currentProfitRate <= self.maxLossRate:
#                 sellVolume = canSellVolume
#                 trySell = True
#
#             if trySell:
#                 print("create sell order")
#                 print(str(currentPrice))
#                 print(str(sellVolume))
#                 sell_order = Order.Order("현재가매도", "0102", self.accountData.getAccountInfo(), 2, code,
#                                          self.codeName, sellVolume, currentPrice, "00", "", self.profitRate,
#                                          self.lossRate, currentProfitRate, now)
#                 # 주문생성시만 어카운트 정보 업데이트
#                 self.notify_observers(sell_order)
#                 # self.updateAccountData()
#                 self.sellRequest.append(code)
#                 self.SetRemoveReg("300", code)
#
#                 # SendOrder(BSTR sRQName, // 사용자 구분명
#                 # BSTR sScreenNo, // 화면번호
#                 # BSTR sAccNo,  // 계좌번호 10자리
#                 # LONG nOrderType,  // 주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
#                 # BSTR sCode, // 종목코드 (6자리)
#                 # LONG nQty,  // 주문수량
#                 # LONG nPrice, // 주문가격
#                 # BSTR sHogaGb,   // 거래구분(혹은 호가구분)은 아래 참고
#                 # BSTR sOrgOrderNo  // 원주문번호. 신규주문에는 공백 입력, 정정/취소시 입력합니다.
#                 # )