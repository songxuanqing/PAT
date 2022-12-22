_I='volume'
_H='close'
_G='low'
_F='high'
_E='open'
_D='index'
_C='date'
_B=None
_A='종목코드'
import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from datetime import datetime
import pandas
from PyQt5.QtCore import *
from time import sleep
class KiwoomData:
	kiwoom=_B
	def __init__(self,kiwoom):super().__init__();self.kiwoom=kiwoom;self.calculator_event_loop=QEventLoop();self.screen_calculation_stock='9000';self.kiwoom.OnReceiveTrData.connect(self.tr_slot)
	def request_candle_data(self,code=_B,date=_B,nPrevNext=0,type=_B,interval=_B):
		F='끝일자';E='틱범위';D='기준일자';C='CommRqData(QString, QString, int, QString)';B='수정주가구분';A='SetInputValue(QString, QString)';sleep(3)
		if nPrevNext==0:self.calculator_list={_D:[],_C:[],_E:[],_F:[],_G:[],_H:[],_I:[]}
		else:self.calculator_list=self.calculator_list
		self.code=code;self.time=date;self.type=type;self.interval=interval
		if type=='틱':self.kiwoom.dynamicCall(A,_A,code);self.kiwoom.dynamicCall(A,E,interval);self.kiwoom.dynamicCall(A,B,1);self.kiwoom.dynamicCall(C,'주식틱차트조회요청','opt10079',nPrevNext,self.screen_calculation_stock)
		elif type=='분':self.kiwoom.dynamicCall(A,_A,code);self.kiwoom.dynamicCall(A,E,interval);self.kiwoom.dynamicCall(A,B,1);self.kiwoom.dynamicCall(C,'주식분봉차트조회요청','opt10080',nPrevNext,self.screen_calculation_stock)
		elif type=='일':self.kiwoom.dynamicCall(A,_A,code);self.kiwoom.dynamicCall(A,D,date);self.kiwoom.dynamicCall(A,B,1);self.kiwoom.dynamicCall(C,'주식일봉차트조회요청','opt10081',nPrevNext,self.screen_calculation_stock)
		elif type=='주':self.kiwoom.dynamicCall(A,_A,code);self.kiwoom.dynamicCall(A,D,date);self.kiwoom.dynamicCall(A,B,1);self.kiwoom.dynamicCall(A,F,'');self.kiwoom.dynamicCall(C,'주식주봉차트조회요청','opt10082',nPrevNext,self.screen_calculation_stock)
		elif type=='달':self.kiwoom.dynamicCall(A,_A,code);self.kiwoom.dynamicCall(A,D,date);self.kiwoom.dynamicCall(A,B,1);self.kiwoom.dynamicCall(A,F,'');self.kiwoom.dynamicCall(C,'주식월봉차트조회요청','opt10083',nPrevNext,self.screen_calculation_stock)
		if not self.calculator_event_loop.isRunning():self.calculator_event_loop.exec_();return self.df
	def tr_slot(self,sScrNo,sRQName,sTrCode,sRecordName,sPrevNext):
		E='%Y%m%d';D='            ';C='일자';B='-';A='GetCommData(QString, QString, int, QString)'
		if'봉차트조회요청'in sRQName:
			stock_code=self.kiwoom.dynamicCall(A,sTrCode,sRQName,0,_A);stock_code=stock_code.strip();cnt=self.kiwoom.dynamicCall('GetRepeatCnt(QString, QString)',sTrCode,sRQName)
			for i in range(cnt):
				if self.type=='분':date=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,'체결시간');date=date.replace('      ','');date_to_time=datetime.strptime(date,'%Y%m%d%H%M%S')
				elif self.type=='일':date=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,C);date=date.replace(D,'');date_to_time=datetime.strptime(date,E)
				elif self.type=='주':date=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,C);date=date.replace(D,'');date_to_time=datetime.strptime(date,E)
				elif self.type=='달':date=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,C);date=date.replace(D,'');date_to_time=datetime.strptime(date,E)
				open=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,'시가');open=open.replace(B,'');high=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,'고가');high=high.replace(B,'');low=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,'저가');low=low.replace(B,'');close=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,'현재가');close=close.replace(B,'');volume=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,'거래량');self.calculator_list[_D].append(i);self.calculator_list[_C].append(date_to_time);self.calculator_list[_E].append(int(open));self.calculator_list[_F].append(int(high));self.calculator_list[_G].append(int(low));self.calculator_list[_H].append(int(close));self.calculator_list[_I].append(int(volume))
			print(str(self.calculator_list))
			if sPrevNext=='2':print('if'+sPrevNext);self.request_candle_data(code=self.code,date=self.time,nPrevNext=2,type=self.type,interval=self.interval)
			else:self.calculator_event_loop.exit();self.df=pandas.DataFrame(self.calculator_list,columns=[_D,_C,_E,_F,_G,_H,_I]);self.df.set_index(self.df[_C],inplace=True)