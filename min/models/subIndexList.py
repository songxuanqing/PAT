import openJson
class SubIndexList:
	arr=[]
	def __init__(A):A.msg,A.params=openJson.getJsonFiles();A.setList()
	def setList(A):C='subIndex';B='mainWindow';D=A.params[B][C]['mavg5'];E=A.params[B][C]['mavg10'];F=A.params[B][C]['mavg20'];G=A.params[B][C]['mavg60'];H=A.params[B][C]['rsi'];I=A.params[B][C]['sc'];J=A.params[B][C]['macd'];K=A.params[B][C]['ilmock'];L=A.params[B][C]['bb'];A.arr.append(D);A.arr.append(E);A.arr.append(F);A.arr.append(G);A.arr.append(H);A.arr.append(I);A.arr.append(J);A.arr.append(K);A.arr.append(L)
	def getList(A):return A.arr
	def add(A,item):A.arr.append(item)