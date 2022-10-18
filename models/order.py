class Order():
    사용자구분명 = None
    화면번호 = None
    계좌번호 = None
    주문유형 = None
    종목코드 = None
    종목명 = None
    주문수량 = None
    주문가격 = None
    거래구분 = None
    원주문번호 = None
    목표익절율 = None
    목표손절율 = None
    현재수익율 = None
    시간 = None


    def __init__(self,사용자구분명,화면번호,계좌번호,주문유형,종목코드,종목명,주문수량,주문가격,거래구분,원주문번호,목표익절율,목표손절율,현재수익율,시간):
        self.사용자구분명 = 사용자구분명
        self.화면번호 = 화면번호
        self.계좌번호 = 계좌번호
        self.주문유형 = 주문유형
        self.종목코드 = 종목코드
        self.종목명 = 종목명
        self.주문수량 = 주문수량
        self.주문가격 = 주문가격
        self.거래구분 = 거래구분
        self.원주문번호 = 원주문번호
        self.목표익절율 = 목표익절율
        self.목표손절율 = 목표손절율
        self.현재수익율 = 현재수익율
        self.시간 = 시간
