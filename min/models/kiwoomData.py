_J='typeMonth'
_I='typeWeek'
_H='typeDay'
_G='typeMin'
_F='requestAccount'
_E='CommRqData(QString, QString, int, QString)'
_D=None
_C='SetInputValue(QString, QString)'
_B='request_candle_data'
_A='kiwoomData'
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import pandas
from datetime import datetime
import os,sys,openJson
print(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import interface.observer as observer
class KiwoomData(observer.Subject):
	kiwoom=_D
	def __init__(self,kiwoom):super().__init__();self.msg,self.params=openJson.getJsonFiles();self.kiwoom=kiwoom;self._observer_list=[];self.calculator_event_loop=QEventLoop();self.account_event_loop=QEventLoop();self.screen_calculation_stock='2000';self.screen_my_account='1000';self.account_stock_dict={};self.kiwoom.OnReceiveTrData.connect(self.tr_slot);self.is_completed_request=False;self.account_number=self.get_account_info()
	def register_observer(self,observer):
		if observer in self._observer_list:return'Already exist observer!'
		self._observer_list.append(observer);return'Success register!'
	def remove_observer(self,observer):
		if observer in self._observer_list:self._observer_list.remove(observer);return'Success remove!'
		return'observer does not exist.'
	def notify_observers(self,df):
		for observer in self._observer_list:observer.update(self.is_completed_request,df)
	def getChartData(self):return self.calculator_list
	def get_account_evaluation_balance(self,nPrevNext=0):
		A='get_account_evaluation_balance';accountNumVal=self.params[_A][A]['accountNum'];passwordVal=self.params[_A][A]['password'];inputPasswordVal=self.params[_A][A]['inputPassword'];searchTypeVal=self.params[_A][A]['searchType'];requestAccountVal=self.params[_A][_B][_F];self.kiwoom.dynamicCall(_C,accountNumVal,self.account_number);self.kiwoom.dynamicCall(_C,passwordVal,' ');self.kiwoom.dynamicCall(_C,inputPasswordVal,'00');self.kiwoom.dynamicCall(_C,searchTypeVal,'1');returnCode=self.kiwoom.dynamicCall(_E,requestAccountVal,'opw00018',nPrevNext,self.screen_my_account)
		if not self.account_event_loop.isRunning():self.account_event_loop.exec_()
		else:print('')
		return self.accountBalance
	def get_account_info(self):account_list=self.kiwoom.dynamicCall('GetLoginInfo(QString)','ACCLIST');account_number=account_list.split(';')[0];return account_number
	def request_candle_data(self,code=_D,date=_D,nPrevNext=0,type=_D,interval=_D):
		typeMinVal=self.params[_A][_B][_G];typeDayVal=self.params[_A][_B][_H];typeWeekVal=self.params[_A][_B][_I];typeMonthVal=self.params[_A][_B][_J];codeVal=self.params[_A][_B]['code'];tickVal=self.params[_A][_B]['tick'];stdDateVal=self.params[_A][_B]['stdDate'];editedPriceVal=self.params[_A][_B]['editedPrice'];endDateVal=self.params[_A][_B]['endDate'];requestMinVal=self.params[_A][_B]['requestMin'];requestDayVal=self.params[_A][_B]['requestDay'];requestWeekVal=self.params[_A][_B]['requestWeek'];requestMonthVal=self.params[_A][_B]['requestMonth'];self.code=code;self.time=date;self.type=type;self.interval=interval
		if type==typeMinVal:self.kiwoom.dynamicCall(_C,codeVal,code);self.kiwoom.dynamicCall(_C,tickVal,interval);self.kiwoom.dynamicCall(_C,editedPriceVal,1);self.kiwoom.dynamicCall(_E,requestMinVal,'opt10080',nPrevNext,self.screen_calculation_stock)
		elif type==typeDayVal:self.kiwoom.dynamicCall(_C,codeVal,code);self.kiwoom.dynamicCall(_C,stdDateVal,date);self.kiwoom.dynamicCall(_C,editedPriceVal,1);self.kiwoom.dynamicCall(_E,requestDayVal,'opt10081',nPrevNext,self.screen_calculation_stock)
		elif type==typeWeekVal:self.kiwoom.dynamicCall(_C,codeVal,code);self.kiwoom.dynamicCall(_C,stdDateVal,date);self.kiwoom.dynamicCall(_C,editedPriceVal,1);self.kiwoom.dynamicCall(_C,endDateVal,'');self.kiwoom.dynamicCall(_E,requestWeekVal,'opt10082',nPrevNext,self.screen_calculation_stock)
		elif type==typeMonthVal:self.kiwoom.dynamicCall(_C,codeVal,code);self.kiwoom.dynamicCall(_C,stdDateVal,date);self.kiwoom.dynamicCall(_C,editedPriceVal,1);self.kiwoom.dynamicCall(_C,endDateVal,'');self.kiwoom.dynamicCall(_E,requestMonthVal,'opt10083',nPrevNext,self.screen_calculation_stock)
		if not self.calculator_event_loop.isRunning():self.calculator_event_loop.exec_()
		return self.df
	def req_account_data(self):self.total_buy_money=0;self.total_evaluation_money=0;self.total_evaluation_profit_and_loss_money=0;self.total_yield=0;self.account_stock_dict={}
	def tr_slot(self,sScrNo,sRQName,sTrCode,sRecordName,sPrevNext):
		M='GetRepeatCnt(QString, QString)';L='currentPrice';K='%Y%m%d';J='            ';I='close';H='index';G='-';F='volume';E='low';D='high';C='open';B='date';A='GetCommData(QString, QString, int, QString)';requestCandleVal=self.params[_A][_B]['requestCandle'];requestAccountVal=self.params[_A][_B][_F];codeVal=self.params[_A][_B]['code'];typeMinVal=self.params[_A][_B][_G];typeDayVal=self.params[_A][_B][_H];typeWeekVal=self.params[_A][_B][_I];typeMonthVal=self.params[_A][_B][_J];chejanTimeVal=self.params[_A][_B]['chejanTime'];dateVal=self.params[_A][_B][B];openVal=self.params[_A][_B][C];highVal=self.params[_A][_B][D];lowVal=self.params[_A][_B][E];volumeVal=self.params[_A][_B][F];currentPriceVal=self.params[_A][_B][L]
		if requestCandleVal in sRQName:
			stock_code=self.kiwoom.dynamicCall(A,sTrCode,sRQName,0,codeVal);stock_code=stock_code.strip();cnt=self.kiwoom.dynamicCall(M,sTrCode,sRQName);calculator_list={H:[],B:[],C:[],D:[],E:[],I:[],F:[]}
			for i in range(cnt):
				if self.type==typeMinVal:date=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,chejanTimeVal);date=date.replace('      ','');date_to_time=datetime.strptime(date,'%Y%m%d%H%M%S')
				elif self.type==typeDayVal:date=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,dateVal);date=date.replace(J,'');date_to_time=datetime.strptime(date,K)
				elif self.type==typeWeekVal:date=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,dateVal);date=date.replace(J,'');date_to_time=datetime.strptime(date,K)
				elif self.type==typeMonthVal:date=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,dateVal);date=date.replace(J,'');date_to_time=datetime.strptime(date,K)
				open=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,openVal);open=open.replace(G,'');high=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,highVal);high=high.replace(G,'');low=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,lowVal);low=low.replace(G,'');close=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,currentPriceVal);close=close.replace(G,'');volume=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,volumeVal);calculator_list[H].append(i);calculator_list[B].append(date_to_time);calculator_list[C].append(int(open));calculator_list[D].append(int(high));calculator_list[E].append(int(low));calculator_list[I].append(int(close));calculator_list[F].append(int(volume))
			self.calculator_event_loop.exit();self.df=pandas.DataFrame(calculator_list,columns=[H,B,C,D,E,I,F]);self.df.set_index(self.df[B],inplace=True)
		elif sRQName==requestAccountVal:
			noVal=self.params[_A][_B]['No'];accountCodeVal=self.params[_A][_B]['accountCode'];evalAmountVal=self.params[_A][_B]['evalAmount'];profitRateVal=self.params[_A][_B]['profitRate'];buyPriceVal=self.params[_A][_B]['buyPrice'];buyAmountVal=self.params[_A][_B]['buyAmount'];holdQtyVal=self.params[_A][_B]['holdQty'];canSellQtyVal=self.params[_A][_B]['canSellQty'];currentPriceVal=self.params[_A][_B][L];totalBuyAmountVal=self.params[_A][_B]['totalBuyAmount'];totalEvalAmountVal=self.params[_A][_B]['totalEvalAmount'];totalEvalProfitAmountVal=self.params[_A][_B]['totalEvalProfitAmount'];totalProfitRateVal=self.params[_A][_B]['totalProfitRate'];codeNumVal=self.params[_A][_B]['codeNum'];codeNameVal=self.params[_A][_B]['codeName'];evalProfitVal=self.params[_A][_B]['evalProfit'];self.balance_list={noVal:[],accountCodeVal:[],codeNameVal:[],evalAmountVal:[],profitRateVal:[],buyPriceVal:[],buyAmountVal:[],holdQtyVal:[],canSellQtyVal:[],currentPriceVal:[]};total_buy_money=self.kiwoom.dynamicCall(A,sTrCode,sRQName,0,totalBuyAmountVal);self.total_buy_money=int(total_buy_money);total_evaluation_money=self.kiwoom.dynamicCall(A,sTrCode,sRQName,0,totalEvalAmountVal);self.total_evaluation_money=int(total_evaluation_money);total_evaluation_profit_and_loss_money=self.kiwoom.dynamicCall(A,sTrCode,sRQName,0,totalEvalProfitAmountVal);self.total_evaluation_profit_and_loss_money=int(total_evaluation_profit_and_loss_money);total_yield=self.kiwoom.dynamicCall(A,sTrCode,sRQName,0,totalProfitRateVal);self.total_yield=float(total_yield);cnt=self.kiwoom.dynamicCall(M,sTrCode,sRQName)
			for i in range(cnt):
				stock_code=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,codeNumVal);stock_code=stock_code.strip()[1:];stock_name=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,codeNameVal);stock_name=stock_name.strip();stock_evaluation_profit_and_loss=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,evalProfitVal);stock_evaluation_profit_and_loss=int(stock_evaluation_profit_and_loss);stock_yield=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,profitRateVal);stock_yield=float(stock_yield);stock_buy_money=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,buyPriceVal);stock_buy_money=int(stock_buy_money);stock_buy_total_money=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,buyAmountVal);stock_buy_total_money=int(stock_buy_total_money);stock_quantity=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,holdQtyVal);stock_quantity=int(stock_quantity);stock_trade_quantity=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,canSellQtyVal);stock_trade_quantity=int(stock_trade_quantity);stock_present_price=self.kiwoom.dynamicCall(A,sTrCode,sRQName,i,currentPriceVal);stock_present_price=int(stock_present_price)
				if not stock_code in self.account_stock_dict:self.account_stock_dict[stock_code]={}
				self.balance_list[noVal].append(i);self.balance_list[accountCodeVal].append(stock_code);self.balance_list[codeNameVal].append(stock_name);self.balance_list[evalAmountVal].append(str(stock_evaluation_profit_and_loss));self.balance_list[profitRateVal].append(str(stock_yield));self.balance_list[buyPriceVal].append(str(stock_buy_money));self.balance_list[buyAmountVal].append(str(stock_buy_total_money));self.balance_list[holdQtyVal].append(str(stock_quantity));self.balance_list[canSellQtyVal].append(str(stock_trade_quantity));self.balance_list[currentPriceVal].append(str(stock_present_price))
			if sPrevNext=='2':self.get_account_evaluation_balance(2)
			else:self.cancel_screen_number(self.screen_my_account);self.account_event_loop.exit();df=pandas.DataFrame(self.balance_list,columns=[noVal,accountCodeVal,codeNameVal,evalAmountVal,profitRateVal,buyPriceVal,buyAmountVal,holdQtyVal,canSellQtyVal,currentPriceVal]);df.set_index(noVal,inplace=True);self.accountBalance=df
	def cancel_screen_number(self,sScrNo):self.kiwoom.dynamicCall('DisconnectRealData(QString)',sScrNo)