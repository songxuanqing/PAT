_AK='http://localhost:9000/'
_AJ='timeFormat'
_AI='piggleDao'
_AH='canSellVolume'
_AG='codeName'
_AF='first'
_AE='totalBuyAmount'
_AD='totalBuyAmountPerTime'
_AC='currentPrice'
_AB='oneStock'
_AA='%Y-%m-%d'
_A9='lossQtyPercent'
_A8='profitQtyPercent'
_A7='endTime'
_A6='startTime'
_A5='DisConnectRealData(QString)'
_A4='observer does not exist.'
_A3='Success remove!'
_A2='Success register!'
_A1='Already exist observer!'
_A0='pats_piggle_dao_most_voted.csv'
_z='low'
_y='high'
_x='minBuy'
_w='dayBuy'
_v='condiCode'
_u='AI'
_t='{:.3f}'
_s='currentPriceBuy'
_r='0102'
_q='totalPrice'
_p='open'
_o='%Y%m%d'
_n='type'
_m='aiTradingVals'
_l='0101'
_k='currentPriceSell'
_j='close'
_i='maxLossRate'
_h='maxProfitRate'
_g='price'
_f='min'
_e='day'
_d='name'
_c='piggleDaoMostVotedList'
_b='date'
_a='lossRate'
_Z='profitRate'
_Y='condiName'
_X='conditionList'
_W='updateLog'
_V='00'
_U='order'
_T='id'
_S='displayKiwoomConditionTable'
_R='AIConditionList'
_Q='kiwoomConditionList'
_P='accumulatedAmount'
_O='isSellOrdered'
_N='isBuyOrdered'
_M='displayConditionTable'
_L='currentProfitRate'
_K=None
_J=0.0
_I='buyVolume'
_H='sellChejan'
_G='buyPrice'
_F='buyChejan'
_E=False
_D='code'
_C=True
_B='mainWindow'
_A='kiwoomRealTimeData'
import interface.observerOrderQueue as observer,datetime,time as Time,models.accountData as AccountData,models.order as Order,models.orderQueue as OrderQueue,interface.observerOrder as observerOrder,interface.observerAccount as observerAccount,interface.observerChejan as observerChejan,interface.observerMainPrice as observerMainPrice,pandas,os,sys,json
from PyQt5.QtCore import *
from PyQt5 import QtNetwork
import requests,asyncio,models.database as Database,openJson
class KiwoomRealTimeData(observer.Observer,observerAccount.Observer,observerOrder.Subject,observerChejan.Subject,observerMainPrice.Subject):
	kiwoom=_K
	def __init__(self,kiwoom,kiwoomData,conditionList,kiwoomConditionList,AIConditionList,settingPiggleDaoMostVoted):
		super().__init__();self.msg,self.params=openJson.getJsonFiles();self.dataManager=Database.Database();self.kiwoom=kiwoom;self.selectedStock=0;self.networkAccessManager=QtNetwork.QNetworkAccessManager();self.networkAccessManager.finished.connect(self.handleNetworkResponse);self.id=0;aiTradingVals={};self.predictRequestDf=pandas.DataFrame({_T:[self.id],_m:[aiTradingVals]});self.orderQueue=OrderQueue.OrderQueue(kiwoom);self.register_subject(self.orderQueue);self.accountData=kiwoomData;self.balanceInfo=self.accountData.get_account_evaluation_balance();self.screen_main='3000';self.screen_condition='5000';self.screen_kiwoom_condition='6000';self.screen_code_kiwoom_condition='7000';self.screen_AI_condition='8000';self.scrren_piggle_dao_most_voted='9000';self.register_subject_account(self.accountData);self._observer_list_chejan=[];self._observer_list_mainPrice=[];self.chejan_event_loop=QEventLoop();self.conditionList=conditionList;codeVal=self.params[_A][_X][_D];self.conditionStatusList={codeVal:[],_N:[],_O:[],_F:[],_H:[],_P:[],_G:[],_I:[],_L:[]};self.conditionStatusDf=self.prepareConditionStatusDf(self.conditionList,self.screen_condition,1);self.kiwoomConditionList=kiwoomConditionList;condiCode=self.params[_A][_Q][_v];condiName=self.params[_A][_Q][_Y];codeVal=self.params[_A][_Q][_D];self.kiwoomConditionStatusList={condiCode:[],codeVal:[],_N:[],_O:[],_F:[],_H:[],_P:[],_G:[],_I:[],_L:[]};self.kiwoomConditionStatusDf=pandas.DataFrame(self.kiwoomConditionStatusList,columns=[codeVal,_N,_O,_F,_H,_P,_G,_I,_L])
		for (idx,row) in self.kiwoomConditionList.iterrows():code=row[codeVal];name=row[condiName];self.SendCondition(self.screen_kiwoom_condition,name,code,1)
		self.AIConditionList=AIConditionList;codeVal=self.params[_A][_R][_D];buyType=self.params[_A][_R][_n];dayBuy=self.params[_A][_R][_w];minBuy=self.params[_A][_R][_x];day=self.params[_A][_R][_e];min=self.params[_A][_R][_f];self.AIConditionStatusList={codeVal:[],_N:[],_O:[],_F:[],_H:[],_P:[],_G:[],_I:[],_L:[]};self.AIConditionStatusDf=self.prepareConditionStatusDf(self.AIConditionList,self.screen_AI_condition,2);self.AIPastDataList={}
		for (idx,row) in self.AIConditionList.iterrows():
			totalPastData=_K;code=row[codeVal]
			if row[buyType]==dayBuy:now=datetime.datetime.now();time=now.strftime(_o);totalPastData=self.accountData.request_candle_data(code=code,date=time,nPrevNext=0,type=day,interval=1)
			elif row[buyType]==minBuy:now=datetime.datetime.now();time=now.strftime(_o);totalPastData=self.accountData.request_candle_data(code=code,date=time,nPrevNext=0,type=min,interval=1)
			totalPastData=totalPastData.drop('index',axis=1);totalPastData=totalPastData.drop(_b,axis=1);totalPastData=totalPastData.drop(_p,axis=1);totalPastData=totalPastData.drop(_y,axis=1);totalPastData=totalPastData.drop(_z,axis=1);totalPastData=totalPastData.drop('volume',axis=1);self.AIPastDataList[code]=totalPastData
		self.piggleDaoMostVotedDf=self.dataManager.readCSVFile(_A0);codeVal=self.params[_A][_c][_D];self.piggleDaoMostVotedStatusList={codeVal:[],_N:[],_O:[],_F:[],_H:[],_P:[],_G:[],_I:[],_L:[]};self.piggleDaoMostVotedStatusDf=self.prepareConditionStatusDf(self.piggleDaoMostVotedDf,self.scrren_piggle_dao_most_voted,3);self.settingPiggleDaoMostVoted=settingPiggleDaoMostVoted;self._observer_list=[];self._subject_list=[];self.kiwoom.OnReceiveRealData.connect(self._handler_real_data);self.kiwoom.OnReceiveRealCondition.connect(self._handler_real_condition);self.kiwoom.OnReceiveChejanData.connect(self._receive_chejan_data)
	def SetRemoveReg(self,screen_no,code_list):self.kiwoom.dynamicCall('SetRealRemove(QString,QString)',screen_no,code_list)
	def SendConditionStop(self,screen,cond_name,cond_index):ret=self.kiwoom.dynamicCall('SendConditionStop(QString, QString, int)',screen,cond_name,cond_index)
	def register_observer_mainPrice(self,observer):
		if observer in self._observer_list_mainPrice:return _A1
		self._observer_list_mainPrice.append(observer);return _A2
	def remove_observer_mainPrice(self,observer):
		if observer in self._observer_list_mainPrice:self._observer_list_mainPrice.remove(observer);return _A3
		return _A4
	def notify_observers_mainPrice(self,df):
		for observer in self._observer_list_mainPrice:observer.update_mainPrice(df)
	def register_subject(self,subject):self.subject=subject;self.subject.register_observer(self)
	def update(self,source,type,order):
		B='\n';A='updateOrderLog'
		if source==_A:self.orderQueue.order(type,order)
		elif source=='orderQueue':tab=self.params[_A][A]['tab'];name=self.params[_A][A][_d];orderType=self.params[_A][A]['orderType'];price=self.params[_A][A][_g];qty=self.params[_A][A]['qty'];currentProfitRate=self.params[_A][A][_L];targetProfitRate=self.params[_A][A]['targetProfitRate'];targetLossRate=self.params[_A][A]['targetLossRate'];msg=tab+str(type)+B+name+str(order.sCodeName)+B+orderType+str(order.nOrderType)+B+price+str(order.nPrice)+B+qty+str(order.nQty)+B+currentProfitRate+str(order.currentProfitRate)+B+targetProfitRate+str(order.targetProfitRate)+B+targetLossRate+str(order.targetLossRate);self.notify_observers_order(msg)
	def register_observer_chejan(self,observer):
		if observer in self._observer_list_chejan:return _A1
		self._observer_list_chejan.append(observer);return _A2
	def remove_observer_chejan(self,observer):
		if observer in self._observer_list_chejan:self._observer_list_chejan.remove(observer);return _A3
		return _A4
	def notify_observers_chejan(self,df):
		for observer in self._observer_list_chejan:observer.update_chejan(df)
	def register_observer_order(self,observer):
		if observer in self._observer_list:return _A1
		self._observer_list.append(observer);return _A2
	def remove_observer_order(self,observer):
		if observer in self._observer_list:self._observer_list.remove(observer);return _A3
		return _A4
	def notify_observers_order(self,order):
		for observer in self._observer_list:observer.update_order(order)
	def get_chejan_data(self,fid):ret=self.kiwoom.dynamicCall('GetChejanData(int)',fid);return ret
	def addConditionDf(self,conditionDf):
		if self.conditionList.empty:self.conditionList=conditionDf
		else:self.conditionList=pandas.concat([self.conditionList,conditionDf],ignore_index=_C)
		self.conditionStatusDf=self.prepareConditionStatusDf(conditionDf,self.screen_condition,1)
	def editConditionDf(self,conditionDf):self.conditionList=conditionDf
	def deleteConditionDf(self,codeList):
		codeVal=self.params[_A][_X][_D]
		for i in codeList:
			for (idx,row) in self.conditionList.iterrows():
				if row[codeVal]==i:self.conditionList=self.conditionList.drop(self.conditionList.index[idx])
			for (idx,row) in self.conditionStatusDf.iterrows():
				if row[codeVal]==i:self.conditionStatusDf=self.conditionStatusDf.drop(self.conditionStatusDf.index[idx])
		self.SetRemoveReg(self.screen_condition,codeList)
	def addKiwoomConditionDf(self,conditionDf):
		codeVal=self.params[_A][_Q][_D];condiName=self.params[_A][_Q][_Y]
		if self.kiwoomConditionList.empty:self.kiwoomConditionList=conditionDf
		else:self.kiwoomConditionList=pandas.concat([self.kiwoomConditionList,conditionDf],ignore_index=_C)
		for (idx,row) in conditionDf.iterrows():code=row[codeVal];name=row[condiName];self.SendCondition(self.screen_kiwoom_condition,name,code,1)
	def editKiwoomConditionDf(self,conditionDf):self.kiwoomConditionList=conditionDf
	def deleteKiwoomConditionDf(self,codeList):
		codeVal=self.params[_A][_Q][_D];condiName=self.params[_A][_Q][_Y]
		for i in codeList:
			for (idx,row) in self.kiwoomConditionList.iterrows():
				if row[codeVal]==i:self.kiwoomConditionList=self.kiwoomConditionList.drop(self.kiwoomConditionList.index[idx]);self.SendConditionStop(self.screen_kiwoom_condition,row[condiName],row[codeVal])
			for (idx,row) in self.kiwoomConditionStatusDf.iterrows():
				if row[codeVal]==i:self.kiwoomConditionStatusDf=self.kiwoomConditionStatusDf.drop(self.kiwoomConditionStatusDf.index[idx]);self.SetRemoveReg(self.screen_code_kiwoom_condition,row[codeVal])
	def addAIConditionDf(self,conditionDf):
		codeVal=self.params[_A][_R][_D];buyType=self.params[_A][_R][_n];dayBuy=self.params[_A][_R][_w];minBuy=self.params[_A][_R][_x];day=self.params[_A][_R][_e];min=self.params[_A][_R][_f]
		if self.AIConditionList.empty:self.AIConditionList=conditionDf
		else:self.AIConditionList=pandas.concat([self.AIConditionList,conditionDf],ignore_index=_C)
		self.AIConditionStatusDf=self.prepareConditionStatusDf(conditionDf,self.screen_AI_condition,2)
		for (idx,row) in conditionDf.iterrows():
			totalPastData=_K;code=row[codeVal]
			if row[buyType]==dayBuy:now=datetime.datetime.now();time=now.strftime(_o);totalPastData=self.accountData.request_candle_data(code=code,date=time,nPrevNext=0,type=day,interval=1)
			elif row[buyType]==minBuy:now=datetime.datetime.now();time=now.strftime(_o);totalPastData=self.accountData.request_candle_data(code=code,date=time,nPrevNext=0,type=min,interval=1)
			totalPastData=totalPastData.drop('index',axis=1);totalPastData=totalPastData.drop(_b,axis=1);totalPastData=totalPastData.drop(_p,axis=1);totalPastData=totalPastData.drop(_y,axis=1);totalPastData=totalPastData.drop(_z,axis=1);totalPastData=totalPastData.drop('volume',axis=1);self.AIPastDataList[code]=totalPastData
	def editAIConditionDf(self,conditionDf):self.AIConditionList=conditionDf
	def deleteAIConditionDf(self,codeList):
		codeVal=self.params[_A][_R][_D]
		for i in codeList:
			for (idx,row) in self.AIConditionList.iterrows():
				if row[codeVal]==i:self.AIConditionList=self.AIConditionList.drop(self.AIConditionList.index[idx])
			for (idx,row) in self.AIConditionStatusDf.iterrows():
				if row[codeVal]==i:self.AIConditionStatusDf=self.AIConditionStatusDf.drop(self.AIConditionStatusDf.index[idx])
		self.SetRemoveReg(self.screen_AI_condition,codeList)
	def updateSettingPiggleDaoMostVoted(self,df):self.settingPiggleDaoMostVoted=df
	def SendCondition(self,screen,cond_name,cond_index,search):ret=self.kiwoom.dynamicCall('SendCondition(QString, QString, int, int)',screen,cond_name,cond_index,search)
	def subscribe_stock_conclusion(self,screen_no,code):self.SetRealReg(screen_no,code,'20',1)
	def SetRealReg(self,screen_no,code_list,fid_list,real_type):self.kiwoom.dynamicCall('SetRealReg(QString, QString, QString, QString)',screen_no,code_list,fid_list,real_type)
	def GetCommRealData(self,code,fid):data=self.kiwoom.dynamicCall('GetCommRealData(QString, int)',code,fid);return data
	def stopAllCondition(self):self.kiwoom.dynamicCall(_A5,self.screen_condition)
	def stopSelectedCondition(self,codeList):self.SetRemoveReg(self.screen_condition,codeList)
	def startSelectedCondition(self,codeList):
		for i in codeList:self.subscribe_stock_conclusion(self.screen_condition,i)
	def stopAllKiwoomCondition(self):
		codeVal=self.params[_A][_Q][_D];condiName=self.params[_A][_Q][_Y]
		for (idx,row) in self.kiwoomConditionList.iterrows():self.SendConditionStop(self.screen_kiwoom_condition,row[condiName],row[codeVal])
		for (idx,row) in self.kiwoomConditionStatusDf.iterrows():self.SetRemoveReg(self.screen_code_kiwoom_condition,row[codeVal])
	def stopSelectedKiwoomCondition(self,codeList):
		codeVal=self.params[_A][_Q][_D];condiName=self.params[_A][_Q][_Y]
		for i in codeList:
			for (idx,row) in self.kiwoomConditionList.iterrows():
				if row[codeVal]==i:self.SendConditionStop(self.screen_kiwoom_condition,row[condiName],row[codeVal])
			for (idx,row) in self.kiwoomConditionStatusDf.iterrows():
				if row[codeVal]==i:self.SetRemoveReg(self.screen_code_kiwoom_condition,row[codeVal])
	def startSelectedKiwoomCondition(self,codeList):
		codeVal=self.params[_A][_Q][_D];condiName=self.params[_A][_Q][_Y]
		for i in codeList:
			for (idx,row) in self.kiwoomConditionList.iterrows():
				if row[codeVal]==i:self.SendCondition(self.screen_kiwoom_condition,row[condiName],row[codeVal],1)
	def stopAllAICondition(self):self.kiwoom.dynamicCall(_A5,self.screen_AI_condition)
	def stopSelectedAICondition(self,codeList):self.SetRemoveReg(self.screen_AI_condition,codeList)
	def startSelectedAICondition(self,codeList):
		for i in codeList:self.subscribe_stock_conclusion(self.screen_AI_condition,i)
	def getRealPriceData(self,code):self.selectedStock=code;self.kiwoom.dynamicCall(_A5,self.screen_main);self.subscribe_stock_conclusion(self.screen_main,code)
	def _receive_chejan_data(self,gubun,item_cnt,fid_list):
		C='2';B='1';A='displayChejanTable';code=self.get_chejan_data(9001)[1:];status=self.get_chejan_data(913);chejanPrice=self.get_chejan_data(910);chejanVolume=self.get_chejan_data(911);buySell=self.get_chejan_data(907);chejaned=self.params[_A]['chejan']['chejaned'];codeVal=self.params[_A][_X][_D]
		if status==chejaned:
			for (idx,row) in self.conditionStatusDf.iterrows():
				if row[codeVal]==code:
					if buySell==B:self.conditionStatusDf.at[(idx,_F)]=_E;self.conditionStatusDf.at[(idx,_H)]=_C;self.conditionStatusDf.at[(idx,_G)]=0;self.conditionStatusDf.at[(idx,_I)]=0
					elif buySell==C:self.conditionStatusDf.at[(idx,_F)]=_C;self.conditionStatusDf.at[(idx,_H)]=_E;self.conditionStatusDf.at[(idx,_G)]=chejanPrice;self.conditionStatusDf.at[(idx,_I)]=chejanVolume
			if not self.kiwoomConditionStatusDf.empty:
				for (idx,row) in self.kiwoomConditionStatusDf.iterrows():
					if row[codeVal]==code:
						if buySell==B:self.kiwoomConditionStatusDf.at[(idx,_F)]=_E;self.kiwoomConditionStatusDf.at[(idx,_H)]=_C;self.kiwoomConditionStatusDf.at[(idx,_G)]=0;self.kiwoomConditionStatusDf.at[(idx,_I)]=0
						elif buySell==C:self.kiwoomConditionStatusDf.at[(idx,_F)]=_C;self.kiwoomConditionStatusDf.at[(idx,_H)]=_E;self.kiwoomConditionStatusDf.at[(idx,_G)]=chejanPrice;self.kiwoomConditionStatusDf.at[(idx,_I)]=chejanVolume
			for (idx,row) in self.AIConditionStatusDf.iterrows():
				if row[codeVal]==code:
					if buySell==B:self.AIConditionStatusDf.at[(idx,_F)]=_E;self.AIConditionStatusDf.at[(idx,_H)]=_C;self.AIConditionStatusDf.at[(idx,_G)]=0;self.AIConditionStatusDf.at[(idx,_I)]=0
					elif buySell==C:self.AIConditionStatusDf.at[(idx,_F)]=_C;self.AIConditionStatusDf.at[(idx,_H)]=_E;self.AIConditionStatusDf.at[(idx,_G)]=chejanPrice;self.AIConditionStatusDf.at[(idx,_I)]=chejanVolume
			for (idx,row) in self.piggleDaoMostVotedStatusDf.iterrows():
				if row[codeVal]==code:
					if buySell==B:self.piggleDaoMostVotedStatusDf.at[(idx,_F)]=_E;self.piggleDaoMostVotedStatusDf.at[(idx,_H)]=_C;self.piggleDaoMostVotedStatusDf.at[(idx,_G)]=0;self.piggleDaoMostVotedStatusDf.at[(idx,_I)]=0
					elif buySell==C:self.piggleDaoMostVotedStatusDf.at[(idx,_F)]=_C;self.piggleDaoMostVotedStatusDf.at[(idx,_H)]=_E;self.piggleDaoMostVotedStatusDf.at[(idx,_G)]=chejanPrice;self.piggleDaoMostVotedStatusDf.at[(idx,_I)]=chejanVolume
			codeVal=self.params[_A][_X][_D];nameVal=self.params[_A][_X][_d];buy=self.params[_A][_X]['buy'];sell=self.params[_A][_X]['sell'];profitRateVal=self.params[_B][_M][_Z];maxProfitRateVal=self.params[_B][_M][_h];lossRateVal=self.params[_B][_M][_a];maxLossRateVal=self.params[_B][_M][_i];codeChejan=self.params[_B][A][_D];nameChejan=self.params[_B][A][_d];typeChejan=self.params[_B][A][_n];priceChejan=self.params[_B][A][_g];qtyChejan=self.params[_B][A]['qty'];currentProfitRateChejan=self.params[_B][A][_L];profitRateChejan=self.params[_B][A][_Z];maxProfitRateChejan=self.params[_B][A][_h];lossRateChejan=self.params[_B][A][_a];maxLossRateChejan=self.params[_B][A][_i]
			for (idx,row) in self.conditionList.iterrows():
				if row[codeVal]==code:
					name=row[name]
					if buySell==B:type=sell
					elif buySell==C:type=buy
					price=str(chejanPrice);volume=str(chejanVolume);profitRate=str(row[profitRateVal]);maxProfitRate=str(row[maxProfitRateVal]);lossRate=str(row[lossRateVal]);maxLossRate=str(row[maxLossRateVal]);currentProfitRate='0'
					for (idx,row) in self.conditionStatusDf.iterrows():
						if row[codeVal]==code:currentProfitRate=str(row[_L])
						df=pandas.DataFrame([[code,name,type,price,volume,currentProfitRate,profitRate,maxProfitRate,lossRate,maxLossRate]],columns=[codeChejan,nameChejan,typeChejan,priceChejan,qtyChejan,currentProfitRateChejan,profitRateChejan,maxProfitRateChejan,lossRateChejan,maxLossRateChejan]);self.notify_observers_chejan(df);break
			for (idx,row) in self.AIConditionList.iterrows():
				if row[codeVal]==code:
					name=row[nameVal]
					if buySell==B:type=sell
					elif buySell==C:type=buy
					price=str(chejanPrice);volume=str(chejanVolume);profitRate=str(_J);maxProfitRate=str(_J);lossRate=str(_J);maxLossRate=str(_J);currentProfitRate='0'
					for (idx,row) in self.AIConditionStatusDf.iterrows():
						if row[codeVal]==code:currentProfitRate=str(row[_L])
						df=pandas.DataFrame([[code,name,type,price,volume,currentProfitRate,profitRate,maxProfitRate,lossRate,maxLossRate]],columns=[codeChejan,nameChejan,typeChejan,priceChejan,qtyChejan,currentProfitRateChejan,profitRateChejan,maxProfitRateChejan,lossRateChejan,maxLossRateChejan]);self.notify_observers_chejan(df);break
			for (idx,row) in self.piggleDaoMostVotedDf.iterrows():
				if row[codeVal]==code:
					name=row[nameVal]
					if buySell==B:type=sell
					elif buySell==C:type=buy
					price=str(chejanPrice);volume=str(chejanVolume);profitRate=str(_J);maxProfitRate=str(_J);lossRate=str(_J);maxLossRate=str(_J);currentProfitRate='0'
					for (idx,row) in self.piggleDaoMostVotedStatusDf.iterrows():
						if row[codeVal]==code:currentProfitRate=str(row[_L])
						df=pandas.DataFrame([[code,name,type,price,volume,currentProfitRate,profitRate,maxProfitRate,lossRate,maxLossRate]],columns=[codeChejan,nameChejan,typeChejan,priceChejan,qtyChejan,currentProfitRateChejan,profitRateChejan,maxProfitRateChejan,lossRateChejan,maxLossRateChejan]);self.notify_observers_chejan(df);break
	def _handler_real_condition(self,code,type,cond_name,cond_index):
		if type=='I':
			condiCode=self.params[_A][_Q][_v];condiName=self.params[_A][_Q][_Y];codeVal=self.params[_A][_Q][_D];self.kiwoomConditionStatusList[condiCode].append(cond_index);self.kiwoomConditionStatusList[codeVal].append(code);self.kiwoomConditionStatusList[_N].append(_E);self.kiwoomConditionStatusList[_O].append(_C);self.kiwoomConditionStatusList[_F].append(_E);self.kiwoomConditionStatusList[_H].append(_E);self.kiwoomConditionStatusList[_P].append(0);self.kiwoomConditionStatusList[_G].append(0);self.kiwoomConditionStatusList[_I].append(0);self.kiwoomConditionStatusList[_L].append('0');df=pandas.DataFrame(self.kiwoomConditionStatusList,columns=[condiCode,codeVal,_N,_O,_F,_H,_P,_G,_I,_L]);self.kiwoomConditionStatusDf=df;data=self.kiwoomConditionList[self.kiwoomConditionList[codeVal]==code];idVal=self.params[_B][_S][_T];codeVal=self.params[_B][_S][_D];nameVal=self.params[_B][_S][_d];totalPriceVal=self.params[_B][_S][_q];priceVal=self.params[_B][_S][_g];startTimeVal=self.params[_B][_S][_A6];endTimeVal=self.params[_B][_S][_A7];profitRateVal=self.params[_B][_S][_Z];profitQtyPercentVal=self.params[_B][_S][_A8];maxProfitRateVal=self.params[_B][_S][_h];lossRateVal=self.params[_B][_S][_a];lossQtyPercentVal=self.params[_B][_S][_A9];maxLossRateVal=self.params[_B][_S][_i]
			for (idx,condition) in data.iterrows():totalBuyAmount=int(condition[priceVal]);buyStartTime=str(condition[startTimeVal]);buyEndTime=str(condition[endTimeVal]);profitRate=float(condition[profitRateVal]);profitSellVolume=int(condition[profitQtyPercentVal])*0.01;maxProfitRate=float(condition[maxProfitRateVal]);lossRate=float(condition[lossRateVal]);lossSellVolume=int(condition[lossQtyPercentVal])*0.01;maxLossRate=float(condition[maxLossRateVal]);id=0;arr=[id,str(code),'',0,totalBuyAmount,buyStartTime,buyEndTime,profitRate,profitSellVolume,maxProfitRate,lossRate,lossSellVolume,maxLossRate];df=pandas.DataFrame([arr],columns=[idVal,codeVal,nameVal,totalPriceVal,priceVal,startTimeVal,endTimeVal,profitRateVal,profitQtyPercentVal,maxProfitRateVal,lossRateVal,lossQtyPercentVal,maxLossRateVal]);pandas.concat([self.self.conditionList,df]);self.subscribe_stock_conclusion(self.screen_code_kiwoom_condition,code)
	def _handler_real_data(self,code,real_type,real_data):
		A='displayRealPriceTable'
		if code==self.selectedStock:currentPrice=self.GetCommRealData(code,10);compareToYesterday=self.GetCommRealData(code,11);goDownRate=self.GetCommRealData(code,12);accumulatedVolume=self.GetCommRealData(code,13);startPrice=self.GetCommRealData(code,16);highPrice=self.GetCommRealData(code,17);lowPrice=self.GetCommRealData(code,18);arr=[currentPrice,compareToYesterday,goDownRate,accumulatedVolume,startPrice,highPrice,lowPrice];priceVal=self.params[_B][A][_g];compareToYesterdayVal=self.params[_B][A]['compareToYesterday'];rocVal=self.params[_B][A]['roc'];accumulatedVolumeVal=self.params[_B][A]['accumulatedVolume'];startVal=self.params[_B][A]['start'];highVal=self.params[_B][A][_y];lowVal=self.params[_B][A][_z];df=pandas.DataFrame([arr],columns=[priceVal,compareToYesterdayVal,rocVal,accumulatedVolumeVal,startVal,highVal,lowVal]);self.notify_observers_mainPrice(df)
		currentPrice=self.GetCommRealData(code,10)
		if currentPrice!='':currentPrice=abs(int(currentPrice));time=self.GetCommRealData(code,20);self.trading(code,currentPrice)
	def trading(self,code,currentPrice):
		C='%Y-%m-%d %H:%M:%S';B='%H:%M';A='displayAIConditionTable';codeVal=self.params[_B][A][_D];AIConditionDf=self.AIConditionList[self.AIConditionList[codeVal]==code]
		if not AIConditionDf.empty:
			codeVal=self.params[_B][A][_D];nameVal=self.params[_B][A][_d];buyAmountPerTimeVal=self.params[_B][A]['buyAmountPerTime'];totalPriceVal=self.params[_B][A][_q];startTimeVal=self.params[_B][A][_A6];endTimeVal=self.params[_B][A][_A7];profitRateVal=self.params[_B][A][_Z];profitQtyPercentVal=self.params[_B][A][_A8];maxProfitRateVal=self.params[_B][A][_h];lossRateVal=self.params[_B][A][_a];lossQtyPercentVal=self.params[_B][A][_A9];maxLossRateVal=self.params[_B][A][_i];buyType=self.params[_A][_R][_n];dayBuy=self.params[_A][_R][_w];minBuy=self.params[_A][_R][_x];day=self.params[_A][_R][_e];min=self.params[_A][_R][_f]
			for (idx,condition) in AIConditionDf.iterrows():
				code=str(condition[codeVal]);codeName=condition[nameVal];dayOrMin=condition[buyType];totalBuyAmountPerTime=int(condition[buyAmountPerTimeVal]);totalBuyAmount=int(condition[totalPriceVal]);buyStartTime=str(condition[startTimeVal]);buyEndTime=str(condition[endTimeVal]);profitRate=float(condition[profitRateVal]);profitSellVolume=int(condition[profitQtyPercentVal])*0.01;maxProfitRate=float(condition[maxProfitRateVal]);lossRate=float(condition[lossRateVal]);lossSellVolume=int(condition[lossQtyPercentVal])*0.01;maxLossRate=float(condition[maxLossRateVal]);startTime=datetime.datetime.strptime(buyStartTime,B);endTime=datetime.datetime.strptime(buyEndTime,B);now=datetime.datetime.now();isBuyOrdered=_E;isSellOrdered=_C;status=self.AIConditionStatusDf[self.AIConditionStatusDf[codeVal]==code]
				if not status.empty:
					for (idx,row) in status.iterrows():isBuyOrdered=row[_N];isSellOrdered=row[_O];buyChejan=row[_F];sellChejan=row[_H];accumulatedAmount=row[_P]
				if not isBuyOrdered:
					if startTime.time()<now.time()and now.time()<endTime.time():
						if dayOrMin==dayBuy:
							timeFormat=_AA;url=_e;currentProfitRate=_J
							if len(self.AIPastDataList[code])>=499:i_num=499
							else:i_num=len(self.AIPastDataList[code])-101
							print(i_num);self.AIFirstBuy(isBuyOrdered,isSellOrdered,buyChejan,code,codeName,currentPrice,timeFormat,totalBuyAmountPerTime,totalBuyAmount,accumulatedAmount,currentProfitRate,profitRate,lossRate,i_num,url)
						elif dayOrMin==minBuy:
							timeFormat=C;url=_f;currentProfitRate=_J
							if len(self.AIPastDataList[code])>=799:i_num=799
							else:i_num=len(self.AIPastDataList[code])-101
							self.AIFirstBuy(isBuyOrdered,isSellOrdered,buyChejan,code,codeName,currentPrice,timeFormat,totalBuyAmountPerTime,totalBuyAmount,accumulatedAmount,currentProfitRate,profitRate,lossRate,i_num,url)
				if not isSellOrdered and buyChejan:
					if startTime.time()<now.time()and now.time()<endTime.time():
						currentProfitRate=_J;canSellVolume=0
						for (idx,row) in self.AIConditionStatusDf.iterrows():
							if row[codeVal]==code:prevPrice=int(row[_G]);currentProfitRate=float((currentPrice-prevPrice)/currentPrice*100);canSellVolume=row[_I]
						if dayOrMin==dayBuy:
							timeFormat=_AA;url=_e
							if len(self.AIPastDataList[code])>=499:i_num=499
							else:i_num=len(self.AIPastDataList[code])-101
							dueTime=datetime.datetime.strptime('1998-01-01 15:20:00',C)
							if now.time()>=dueTime.time():self.AISecondBuySell(isBuyOrdered,isSellOrdered,buyChejan,code,codeName,currentPrice,timeFormat,totalBuyAmountPerTime,totalBuyAmount,accumulatedAmount,currentProfitRate,profitRate,lossRate,maxProfitRate,maxLossRate,profitSellVolume,lossSellVolume,canSellVolume,i_num,url)
						elif dayOrMin==minBuy:
							timeFormat=C;url=_f
							if len(self.AIPastDataList[code])>=799:i_num=799
							else:i_num=len(self.AIPastDataList[code])-101
							self.AISecondBuySell(isBuyOrdered,isSellOrdered,buyChejan,code,codeName,currentPrice,timeFormat,totalBuyAmountPerTime,totalBuyAmount,accumulatedAmount,currentProfitRate,profitRate,lossRate,maxProfitRate,maxLossRate,profitSellVolume,lossSellVolume,canSellVolume,i_num,url)
		conditionDf=self.conditionList[self.conditionList[codeVal]==code]
		if not conditionDf.empty:
			nameVal=self.params[_B][_M][_d];priceVal=self.params[_B][_M][_g];totalPriceVal=self.params[_B][_M][_q];startTimeVal=self.params[_B][_M][_A6];endTimeVal=self.params[_B][_M][_A7];profitRateVal=self.params[_B][_M][_Z];profitQtyPercentVal=self.params[_B][_M][_A8];maxProfitRateVal=self.params[_B][_M][_h];lossRateVal=self.params[_B][_M][_a];lossQtyPercentVal=self.params[_B][_M][_A9];maxLossRateVal=self.params[_B][_M][_i]
			for (idx,condition) in conditionDf.iterrows():
				code=str(condition[codeVal]);codeName=condition[nameVal];buyPrice=condition[priceVal];totalBuyAmount=int(condition[totalPriceVal]);buyStartTime=str(condition[startTimeVal]);buyEndTime=str(condition[endTimeVal]);profitRate=float(condition[profitRateVal]);profitSellVolume=int(condition[profitQtyPercentVal])*0.01;maxProfitRate=float(condition[maxProfitRateVal]);lossRate=float(condition[lossRateVal]);lossSellVolume=int(condition[lossQtyPercentVal])*0.01;maxLossRate=float(condition[maxLossRateVal]);startTime=datetime.datetime.strptime(buyStartTime,B);endTime=datetime.datetime.strptime(buyEndTime,B);now=datetime.datetime.now();isBuyOrdered=_E;isSellOrdered=_C
				if buyPrice==0:
					condiCode=self.params[_A][_Q][_v];condiName=self.params[_A][_Q][_Y];status=self.kiwoomConditionStatusDf[self.kiwoomConditionStatusDf[codeVal]==code]
					if not status.empty:
						for (idx,row) in status.iterrows():isBuyOrdered=row[_N];isSellOrdered=row[_O];buyChejan=row[_F];sellChejan=row[_H];condi_code=row[condiCode];accumulatedAmount=row[_P]
				else:
					status=self.conditionStatusDf[self.conditionStatusDf[codeVal]==code]
					if not status.empty:
						for (idx,row) in status.iterrows():isBuyOrdered=row[_N];isSellOrdered=row[_O];buyChejan=row[_F];sellChejan=row[_H];condi_code=_K;accumulatedAmount=0
				if not isBuyOrdered:
					if startTime.time()<now.time()and now.time()<endTime.time():self.conditionBuy(code,codeName,currentPrice,buyPrice,accumulatedAmount,condi_code,totalBuyAmount,_J,profitRate,lossRate)
				if not isSellOrdered and buyChejan:
					currentProfitRate=_J;canSellVolume=0
					if buyPrice==0:
						for (idx,row) in self.kiwoomConditionStatusDf.iterrows():
							if row[codeVal]==code:prevPrice=row[_G];currentProfitRate=float((currentPrice-prevPrice)/currentPrice*100);canSellVolume=row[_I]
					else:
						for (idx,row) in self.conditionStatusDf.iterrows():
							if row[codeVal]==code:prevPrice=row[_G];currentProfitRate=float((currentPrice-int(prevPrice))/currentPrice*100);canSellVolume=row[_I]
					self.conditionSell(code,codeName,currentPrice,buyPrice,accumulatedAmount,currentProfitRate,profitRate,lossRate,maxProfitRate,maxLossRate,profitSellVolume,lossSellVolume,canSellVolume)
		now=datetime.datetime.now();openTimeStart=datetime.datetime.strptime('08:50',B);openTimeEnd=datetime.datetime.strptime('08:59',B);closeTimeStart=datetime.datetime.strptime('15:20',B);closeTimeEnd=datetime.datetime.strptime('15:29',B);openVal=self.params[_A][_c][_p];closeVal=self.params[_A][_c][_j]
		if openTimeStart.time()<now.time()and openTimeEnd.time()>now.time():self.tradingForPiggleDaoMostVoted(openVal,code,currentPrice)
		elif closeTimeStart.time()<now.time()and closeTimeEnd.time()>now.time():self.tradingForPiggleDaoMostVoted(closeVal,code,currentPrice)
	def prepareConditionStatusDf(self,conditionDf,screen_num,type):
		codeVal=self.params[_A][_X][_D]
		if type==1:statusList=self.conditionStatusList
		elif type==2:statusList=self.AIConditionStatusList
		elif type==3:statusList=self.piggleDaoMostVotedStatusList
		for (idx,row) in conditionDf.iterrows():code=row[codeVal];statusList[codeVal].append(code);self.subscribe_stock_conclusion(screen_num,code);statusList[_N].append(_E);statusList[_O].append(_C);statusList[_F].append(_E);statusList[_H].append(_E);statusList[_G].append(0);statusList[_I].append(0);statusList[_L].append('0');statusList[_P].append(0)
		df=pandas.DataFrame(statusList,columns=[codeVal,_N,_O,_F,_H,_P,_G,_I,_L])
		if type==1:self.conditionStatusList=statusList
		elif type==2:self.AIConditionStatusList=statusList
		elif type==3:self.piggleDaoMostVotedStatusList=statusList
		return df
	def tradingForPiggleDaoMostVoted(self,type,code,currentPrice):
		B='createSettingPiggleDaoMostVotedFile';A='createPiggleDaoMostVotedFile';isAppliedVal=self.params[_B][B]['isApplied'];amountVal=self.params[_B][B]['amount'];openVal=self.params[_A][_c][_p];closeVal=self.params[_A][_c][_j];codeVal=self.params[_A][_c][_D];expectedPriceVal=self.params[_B][A]['expectedPrice'];priceTypeVal=self.params[_B][A]['priceType'];expectedDateVal=self.params[_B][A]['expectedDate'];nameVal=self.params[_B][A][_d];isApplied=_K;buyVolume=_K
		for (idx,row) in self.settingPiggleDaoMostVoted.iterrows():isApplied=row[isAppliedVal];buyVolume=row[amountVal];break
		if isApplied:
			now=datetime.datetime.now()
			if type==openVal:comparisonTime=now.day;comparisonType=closeVal
			elif type==closeVal:comparisonTime=now.day+1;comparisonType=openVal
			conditionDf=self.piggleDaoMostVotedDf[self.piggleDaoMostVotedDf[codeVal]==code]
			if not conditionDf.empty:
				isBuyOrdered=_E;isSellOrdered=_C;status=self.piggleDaoMostVotedStatusDf[self.piggleDaoMostVotedStatusDf[codeVal]==code]
				if not status.empty:
					for (idx,row) in status.iterrows():isBuyOrdered=row[_N];isSellOrdered=row[_O];buyChejan=row[_F];sellChejan=row[_H];condi_code=_K;accumulatedAmount=_K
					conditionDf=conditionDf[conditionDf[priceTypeVal]==comparisonType]
					if not conditionDf.empty:
						for (idx,condition) in conditionDf.iterrows():
							forecastDate=condition[expectedDateVal];price=condition[expectedPriceVal];codeName=condition[nameVal]
							if not isBuyOrdered:
								forecast_date=datetime.datetime.strptime(forecastDate,_AA)
								if now.year==forecast_date.year and now.month==forecast_date.month and comparisonTime==forecast_date.day:
									if price>currentPrice:self.piggleDaoMostVotedBuy(code,codeName,currentPrice,currentPrice,buyVolume,_J,_J);self.piggleDaoMostVotedDf=self.dataManager.readCSVFile(_A0);piggleDaoMostVotedStatusDf=self.prepareConditionStatusDf(self.piggleDaoMostVotedDf,self.scrren_piggle_dao_most_voted,3)
							if not isSellOrdered and buyChejan:
								currentProfitRate=_J;canSellVolume=0
								for (idx,row) in self.piggleDaoMostVotedStatusDf.iterrows():
									if row[codeVal]==code:prevPrice=row[_G];currentProfitRate=float((currentPrice-int(prevPrice))/currentPrice*100);canSellVolume=row[_I]
								self.piggleDaoMostVotedSell(code,codeName,currentPrice,canSellVolume,currentProfitRate,_J,_J);self.piggleDaoMostVotedDf=self.dataManager.readCSVFile(_A0);piggleDaoMostVotedStatusDf=self.prepareConditionStatusDf(self.piggleDaoMostVotedDf,self.scrren_piggle_dao_most_voted,3)
	def piggleDaoMostVotedSell(self,code,codeName,currentPrice,sellVolume,currentProfitRate,profitRate,lossRate):currentPriceSellVal=self.params[_A][_U][_k];now=datetime.datetime.now();sell_order=Order.Order(currentPriceSellVal,_r,self.accountData.get_account_info(),2,code,codeName,sellVolume,currentPrice,_V,'',profitRate,lossRate,str(currentProfitRate),now);updateTypeVal=self.msg[_W][_AI];self.update(_A,updateTypeVal,sell_order);self.updatePiggleDaoMostVotedDf(code,currentPrice,_K,_E,_C,_E,_K,currentProfitRate)
	def piggleDaoMostVotedBuy(self,code,codeName,currentPrice,buyPrice,buyVolume,profitRate,lossRate):
		now=datetime.datetime.now()
		if currentPrice>=buyPrice:
			if buyVolume>=1:currentPriceBuyVal=self.params[_A][_U][_s];buy_order=Order.Order(currentPriceBuyVal,_l,self.accountData.get_account_info(),1,code,codeName,buyVolume,currentPrice,_V,'',profitRate,lossRate,_J,now);updateTypeVal=self.msg[_W][_AI];self.update(_A,updateTypeVal,buy_order);self.updatePiggleDaoMostVotedDf(code,currentPrice,buyVolume,_C,_E,_C,_K,_J)
	def updatePiggleDaoMostVotedDf(self,code,currentPrice,buyVolume,isBuyOrdered,isSellOrdered,sellChejan,buyChejan,currentProfitRate):
		codeVal=self.params[_A][_c][_D]
		for (idx,row) in self.piggleDaoMostVotedStatusDf.iterrows():
			if row[codeVal]==code:
				self.piggleDaoMostVotedStatusDf.at[(idx,_N)]=isBuyOrdered;self.piggleDaoMostVotedStatusDf.at[(idx,_O)]=isSellOrdered;self.piggleDaoMostVotedStatusDf.at[(idx,_L)]=_t.format(currentProfitRate)
				if not isBuyOrdered:self.piggleDaoMostVotedStatusDf.at[(idx,_H)]=sellChejan;self.piggleDaoMostVotedStatusDf.at[(idx,_G)]=currentPrice;self.piggleDaoMostVotedStatusDf.at[(idx,_I)]=buyVolume
				else:self.piggleDaoMostVotedStatusDf.at[(idx,_F)]=buyChejan
	def checkSell(self,currentProfitRate,profitRate,lossRate,maxProfitRate,maxLossRate,profitSellVolume,lossSellVolume,canSellVolume):
		sellVolume=0;trySell=_E
		if currentProfitRate>=maxProfitRate:sellVolume=canSellVolume;trySell=_C
		elif currentProfitRate<maxProfitRate and currentProfitRate>=profitRate:sellVolume=int(canSellVolume*profitSellVolume);trySell=_C
		elif currentProfitRate>=maxLossRate and currentProfitRate<lossRate:sellVolume=int(canSellVolume*lossSellVolume);trySell=_C
		elif currentProfitRate<=maxLossRate:sellVolume=canSellVolume;trySell=_C
		return trySell,sellVolume
	def conditionSell(self,code,codeName,currentPrice,buyPrice,accumulatedAmount,currentProfitRate,profitRate,lossRate,maxProfitRate,maxLossRate,profitSellVolume,lossSellVolume,canSellVolume):
		now=datetime.datetime.now();trySell,sellVolume=self.checkSell(currentProfitRate,profitRate,lossRate,maxProfitRate,maxLossRate,profitSellVolume,lossSellVolume,canSellVolume)
		if trySell:
			currentPriceSellVal=self.params[_A][_U][_k];sell_order=Order.Order(currentPriceSellVal,_r,self.accountData.get_account_info(),2,code,codeName,sellVolume,currentPrice,_V,'',profitRate,lossRate,str(currentProfitRate),now);updateTypeVal=self.msg[_W][_AB];self.update(_A,updateTypeVal,sell_order)
			if buyPrice==0:self.updateKiwoomConditionDf(code,currentPrice,_K,sellVolume,_C,_E,_C,_K,currentProfitRate,accumulatedAmount)
			else:self.updateConditionDf(code,currentPrice,_K,_E,_C,_E,_K,currentProfitRate)
	def conditionBuy(self,code,codeName,currentPrice,buyPrice,accumulatedAmount,condi_code,totalBuyAmount,currentProfitRate,profitRate,lossRate):
		now=datetime.datetime.now()
		if buyPrice==0:
			condiCodeVal=self.params[_B][_S][_D];codeVal=self.params[_B][_M][_D];totalPriceVal=self.params[_B][_S][_q];status=self.kiwoomConditionStatusDf[self.kiwoomConditionStatusDf[codeVal]==code]
			if not status.empty:
				df=self.kiwoomConditionList[self.kiwoomConditionList[condiCodeVal]==condi_code]
				if not df.empty:
					totalConditionBuyAmount=df[totalPriceVal]
					if totalConditionBuyAmount>accumulatedAmount:
						buyVolume=int(totalBuyAmount/currentPrice)
						if buyVolume>1:currentPriceBuyVal=self.params[_A][_U][_s];buy_order=Order.Order(currentPriceBuyVal,_l,self.accountData.getAccountInfo(),1,code,codeName,buyVolume,currentPrice,_V,'',profitRate,lossRate,currentProfitRate,now);updateTypeVal=self.msg[_W][_AB];self.update(_A,updateTypeVal,buy_order);self.updateKiwoomConditionDf(code,currentPrice,buyVolume,_K,_C,_E,_C,_K,_J,accumulatedAmount)
		elif currentPrice>=buyPrice:
			buyVolume=int(totalBuyAmount/currentPrice)
			if buyVolume>1:currentPriceSellVal=self.params[_A][_U][_k];buy_order=Order.Order(currentPriceSellVal,_l,self.accountData.get_account_info(),1,code,codeName,buyVolume,currentPrice,_V,'',profitRate,lossRate,_J,now);updateTypeVal=self.msg[_W][_AB];self.update(_A,updateTypeVal,buy_order);self.updateConditionDf(code,currentPrice,buyVolume,_C,_E,_C,_K,_J)
	def updateConditionDf(self,code,currentPrice,buyVolume,isBuyOrdered,isSellOrdered,sellChejan,buyChejan,currentProfitRate):
		codeVal=self.params[_B][_M][_D]
		for (idx,row) in self.conditionStatusDf.iterrows():
			if row[codeVal]==code:
				self.conditionStatusDf.at[(idx,_N)]=isBuyOrdered;self.conditionStatusDf.at[(idx,_O)]=isSellOrdered;self.conditionStatusDf.at[(idx,_L)]=_t.format(currentProfitRate)
				if not isBuyOrdered:self.conditionStatusDf.at[(idx,_H)]=sellChejan;self.conditionStatusDf.at[(idx,_G)]=currentPrice;self.conditionStatusDf.at[(idx,_I)]=buyVolume
				else:self.conditionStatusDf.at[(idx,_F)]=buyChejan
	def updateKiwoomConditionDf(self,code,currentPrice,buyVolume,sellVolume,isBuyOrdered,isSellOrdered,sellChejan,buyChejan,currentProfitRate,accumulatedAmount):
		codeVal=self.params[_B][_M][_D]
		for (idx,row) in self.kiwoomConditionStatusDf.iterrows():
			if row[codeVal]==code:
				self.kiwoomConditionStatusDf.at[(idx,_N)]=isBuyOrdered;self.kiwoomConditionStatusDf.at[(idx,_O)]=isSellOrdered;self.kiwoomConditionStatusDf.at[(idx,_L)]=_t.format(currentProfitRate)
				if not isBuyOrdered:self.kiwoomConditionStatusDf.at[(idx,_H)]=sellChejan;self.kiwoomConditionStatusDf.at[(idx,_G)]=currentPrice;self.kiwoomConditionStatusDf.at[(idx,_I)]=buyVolume;self.kiwoomConditionStatusDf.at[(idx,_P)]=accumulatedAmount+currentPrice*buyVolume
				else:self.kiwoomConditionStatusDf.at[(idx,_F)]=buyChejan;self.kiwoomConditionStatusDf.at[(idx,_P)]=accumulatedAmount-currentPrice*sellVolume
	def AIFirstBuy(self,isBuyOrdered,isSellOrdered,buyChejan,code,codeName,currentPrice,timeFormat,totalBuyAmountPerTime,totalBuyAmount,accumulatedAmount,currentProfitRate,profitRate,lossRate,i_num,url):first,xhat=self.prepareInputData(code,currentPrice,timeFormat,i_num);self.id=self.id+1;aiTradingVals={_AC:currentPrice,_AD:totalBuyAmountPerTime,_AE:totalBuyAmount,_AF:first,_D:code,_AG:codeName,_Z:profitRate,_a:lossRate,_L:currentProfitRate,_P:accumulatedAmount,_N:isBuyOrdered,_O:isSellOrdered,_F:buyChejan,_AH:0,_AJ:timeFormat,'i_num':i_num,'url':url};payload={'input':xhat,_T:self.id};qJsonDocument=QJsonDocument(payload);input=qJsonDocument.toJson();newPredictRequestDf=pandas.DataFrame({_T:[self.id],_m:[aiTradingVals]});self.predictRequestDf=pandas.concat([self.predictRequestDf,newPredictRequestDf]);self.predictRequestDf.set_index(self.predictRequestDf[_T],inplace=_C);api=_AK+url;self.networkAccessManager.post(QtNetwork.QNetworkRequest(QUrl(api)),input)
	def AISecondBuySell(self,isBuyOrdered,isSellOrdered,buyChejan,code,codeName,currentPrice,timeFormat,totalBuyAmountPerTime,totalBuyAmount,accumulatedAmount,currentProfitRate,profitRate,lossRate,maxProfitRate,maxLossRate,profitSellVolume,lossSellVolume,canSellVolume,i_num,url):
		now=datetime.datetime.now();trySell,sellVolume=self.checkSell(currentProfitRate,profitRate,lossRate,maxProfitRate,maxLossRate,profitSellVolume,lossSellVolume,canSellVolume)
		if trySell:currentPriceSellVal=self.params[_A][_U][_k];sell_order=Order.Order(currentPriceSellVal,_r,self.accountData.get_account_info(),2,code,codeName,sellVolume,currentPrice,_V,'',profitRate,lossRate,str(currentProfitRate),now);updateTypeVal=self.msg[_W][_u];self.update(_A,updateTypeVal,sell_order);self.updateAIConditionDf(code,currentPrice,0,_E,_C,_K,_E,currentProfitRate,accumulatedAmount)
		else:first,xhat=self.prepareInputData(code,currentPrice,timeFormat,i_num);self.id=self.id+1;aiTradingVals={_AC:currentPrice,_AD:totalBuyAmountPerTime,_AE:totalBuyAmount,_AF:first,_D:code,_AG:codeName,_Z:profitRate,_a:lossRate,_L:currentProfitRate,_P:accumulatedAmount,_N:isBuyOrdered,_O:isSellOrdered,_F:buyChejan,_AH:canSellVolume,_AJ:timeFormat,'i_num':i_num,'url':url};payload={'input':xhat,_T:self.id};qJsonDocument=QJsonDocument(payload);input=qJsonDocument.toJson();newPredictRequestDf=pandas.DataFrame({_T:[self.id],_m:[aiTradingVals]});self.predictRequestDf=pandas.concat([self.predictRequestDf,newPredictRequestDf]);self.predictRequestDf.set_index(self.predictRequestDf[_T],inplace=_C);api=_AK+url;self.networkAccessManager.post(QtNetwork.QNetworkRequest(QUrl(api)),input)
	def updateAIConditionDf(self,code,currentPrice,buyVolume,isBuyOrdered,isSellOrdered,sellChejan,buyChejan,currentProfitRate,accumulatedAmount):
		codeVal=self.params[_B][_M][_D]
		for (idx,row) in self.AIConditionStatusDf.iterrows():
			if row[codeVal]==code:
				self.AIConditionStatusDf.at[(idx,_N)]=isBuyOrdered;self.AIConditionStatusDf.at[(idx,_O)]=isSellOrdered;self.AIConditionStatusDf.at[(idx,_L)]=_t.format(currentProfitRate);self.AIConditionStatusDf.at[(idx,_P)]=accumulatedAmount+currentPrice*buyVolume
				if not isBuyOrdered:self.AIConditionStatusDf.at[(idx,_H)]=sellChejan;self.AIConditionStatusDf.at[(idx,_G)]=currentPrice;self.AIConditionStatusDf.at[(idx,_I)]=buyVolume
				else:self.AIConditionStatusDf.at[(idx,_F)]=buyChejan
	def prepareInputData(self,code,currentPrice,timeFormat,i_num):
		now=datetime.datetime.now();newDate=now.strftime(timeFormat);pastData=self.AIPastDataList[code];arr={_b:[],_j:[]};arr[_b].append(newDate);arr[_j].append(currentPrice);df=pandas.DataFrame(arr,columns=[_b,_j]);df.set_index(df[_b],inplace=_C);df=df.drop(_b,axis=1);print(len(pastData));pastData=pandas.concat([pastData,df]);print(len(pastData));pastData=pastData.iloc[:-1];print(len(pastData));print(i_num);window_size=100;k=0;i=i_num;first=pastData.iloc[(i,k)];xhat=[]
		for j in range(window_size):
			if first!=0:datume1=(pastData.iloc[(i+j,k)]-first)/first
			else:datume1=0
			xhat.append(datume1)
		return first,xhat
	def handleNetworkResponse(self,reply):
		er=reply.error()
		if er==QtNetwork.QNetworkReply.NetworkError.NoError:
			str1=reply.readAll();parse_doucment=QJsonDocument.fromJson(str1);obj=parse_doucment.object();id=obj[_T];output=obj['output'];yhat=output.toDouble();print('yhat'+str(yhat));s=self.predictRequestDf[_m];v=s[id.toInt()];self.predictRequestDf=self.predictRequestDf.drop(id.toInt());now=datetime.datetime.now();currentPrice=v[_AC];totalBuyAmount=v[_AE];totalBuyAmountPerTime=v[_AD];first=v[_AF];code=v[_D];codeName=v[_AG];profitRate=v[_Z];lossRate=v[_a];currentProfitRate=v[_L];accumulatedAmount=v[_P];isBuyOrdered=v[_N];isSellOrdered=v[_O];buyChejan=v[_F];canSellVolume=v[_AH];expected_value=yhat*first+first;codeVal=self.params[_B][_M][_D];status=self.AIConditionStatusDf[self.AIConditionStatusDf[codeVal]==code]
			if not status.empty:
				for (idx,row) in status.iterrows():accumulatedAmount=row[_P]
			if not isBuyOrdered:
				if expected_value>currentPrice:
					if totalBuyAmount>accumulatedAmount:
						buyVolume=int(totalBuyAmountPerTime/currentPrice)
						if buyVolume>1:currentPriceBuyVal=self.params[_A][_U][_s];buy_order=Order.Order(currentPriceBuyVal,_l,self.accountData.get_account_info(),1,code,codeName,buyVolume,currentPrice,_V,'',profitRate,lossRate,currentProfitRate,now);updateTypeVal=self.msg[_W][_u];self.update(_A,updateTypeVal,buy_order);self.updateAIConditionDf(code,currentPrice,buyVolume,_C,_E,_C,_K,currentProfitRate,accumulatedAmount)
			if not isSellOrdered and buyChejan:
				prevPrice=0;codeVal=self.params[_B][_M][_D]
				for (idx,row) in self.AIConditionStatusDf.iterrows():
					if row[codeVal]==code:prevPrice=int(row[_G])
				if expected_value>prevPrice and expected_value>currentPrice:
					if totalBuyAmount>accumulatedAmount:
						buyVolume=int(totalBuyAmountPerTime/currentPrice)
						if buyVolume>1:currentPriceBuyVal=self.params[_A][_U][_s];buy_order=Order.Order(currentPriceBuyVal,_l,self.accountData.get_account_info(),1,code,codeName,buyVolume,currentPrice,_V,'',profitRate,lossRate,str(currentProfitRate),now);updateTypeVal=self.msg[_W][_u];self.update(_A,updateTypeVal,buy_order);self.updateAIConditionDf(code,currentPrice,buyVolume,_C,_E,_C,_K,currentProfitRate,accumulatedAmount)
				elif expected_value<currentPrice:currentPriceSellVal=self.params[_A][_U][_k];sell_order=Order.Order(currentPriceSellVal,_r,self.accountData.get_account_info(),2,code,codeName,canSellVolume,currentPrice,_V,'',profitRate,lossRate,str(currentProfitRate),now);updateTypeVal=self.msg[_W][_u];self.update(_A,updateTypeVal,sell_order);self.updateAIConditionDf(code,currentPrice,0,_E,_C,_K,_E,currentProfitRate,accumulatedAmount)
				else:print('')
		else:print('Error occured: ',er);print(reply.errorString())