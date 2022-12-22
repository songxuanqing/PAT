import openJson
class CandleList:
	kiwoom=None;arr=[]
	def __init__(A):A.msg,A.params=openJson.getJsonFiles();A.setList()
	def setList(A):B='candleList';C=A.params[B]['min1'];D=A.params[B]['min3'];E=A.params[B]['min5'];F=A.params[B]['min10'];G=A.params[B]['min30'];H=A.params[B]['min60'];I=A.params[B]['day1'];J=A.params[B]['week1'];K=A.params[B]['month1'];A.arr.append(C);A.arr.append(D);A.arr.append(E);A.arr.append(F);A.arr.append(G);A.arr.append(H);A.arr.append(I);A.arr.append(J);A.arr.append(K)
	def getList(A):return A.arr
	def add(A,item):A.arr.append(item)