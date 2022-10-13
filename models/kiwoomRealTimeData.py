import interface.observerOrderQueue as observer

class KiwoomRealTimeData(observer.Subject):
    kiwoom = None
    def __init__(self,kiwoom):
        print("real time data")
        super().__init__()
        self.kiwoom = kiwoom
        self._observer_list = []
        # 실시간 데이터 슬롯 등록
        self.kiwoom.OnReceiveRealData.connect(self._handler_real_data)

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
        for observer in self._observer_list:
            observer.update(order)

    def run(self):
        # 주식체결 (실시간)
        self.subscribe_market_time('1')
        self.subscribe_stock_conclusion('2')

    def subscribe_stock_conclusion(self, screen_no):
        self.SetRealReg(screen_no, "229200", "20", 0)

    def subscribe_market_time(self, screen_no):
        self.SetRealReg(screen_no, "", "215", 0)

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
            # 현재가
            현재가 = self.GetCommRealData(code, 10)
            현재가 = abs(int(현재가))          # +100, -100
            체결시간 = self.GetCommRealData(code, 20)
            print("_handler_real_data"+str(현재가))
            # 목표가 계산
            # TR 요청을 통한 전일 range가 계산되었고 아직 당일 목표가가 계산되지 않았다면
            시가 = self.GetCommRealData(code, 16)
            시가 = abs(int(시가))          # +100, -100
            self.target = int(시가)+0.001

            # 매수시도
            # 당일 매수하지 않았고
            # TR 요청과 Real을 통한 목표가가 설정되었고
            # TR 요청을 통해 잔고조회가 되었고
            # 현재가가 목표가가 이상이면
            # if 현재가 >= self.target:
            self.notify_observers(f"시간: {체결시간} 목표가: {self.target} 현재가: {현재가}")
                # self.hold = True
                # quantity = int(self.amount / 현재가)
                # self.SendOrder("매수", "8000", self.account, 1, "229200", quantity, 0, "03", "")
                # print(f"시장가 매수 진행 수량: {quantity}")

            # 로깅
            # print(f"시간: {체결시간} 목표가: {self.target} 현재가: {현재가}")