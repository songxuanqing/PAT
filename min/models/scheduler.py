import schedule,time,requests,pandas,models.database as Database,openJson
class Scheduler:
	def __init__(A):A.msg,A.params=openJson.getJsonFiles();A.dataManager=Database.Database();schedule.every().day.at('08:50').do(A.job);schedule.every().day.at('15:20').do(A.job)
	def job(A):
		N='Open';L='createPiggleDaoMostVotedFile';K='mainWindow';D='piggleDaoMostVotedList';C='kiwoomRealTimeData';E=A.params[C][D]['code'];F=A.params[C][D]['name'];G=A.params[K][L]['expectedPrice'];H=A.params[K][L]['priceType'];I=A.params[K][L]['expectedDate'];O=A.params[C][D]['open'];P=A.params[C][D]['close'];J=[];J.append(N);J.append('Close');list={E:[],F:[],G:[],H:[],I:[]};Q=0
		for M in J:
			R='https://piggle-dao.shop/forecast/selectMostVotedAppInfoList?type='+M;S=requests.get(R);T=S.json()['stock_info_arr']
			for B in T:
				U=B['stockCode'];V=B['stockName'];W=B['price'];X=B['forecastDate']
				if M==N:type=O
				else:type=P
				list[E].append(U);list[F].append(V);list[G].append(W);list[H].append(type);list[I].append(X);Q+=1
		Y=pandas.DataFrame(list,columns=[E,F,G,H,I]);A.dataManager.updateCSVFile('pats_piggle_dao_most_voted.csv',Y)
	def run(A):
		while True:schedule.run_pending();time.sleep(1)