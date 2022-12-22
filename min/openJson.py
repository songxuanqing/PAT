import json
msg_path='const/message.json'
param_path='const/params.json'
def getJsonFiles():
	B='UTF8'
	with open(msg_path,'r',encoding=B)as A:C=json.load(A)
	with open(param_path,'r',encoding=B)as A:D=json.load(A)
	return C,D