import json

msg_path = "const/message.json"
param_path = "const/params.json"

def getJsonFiles():
    with open(msg_path, 'r',encoding='UTF8') as file:
        msg_json = json.load(file)
    with open(param_path, 'r',encoding='UTF8') as file:
        param_json = json.load(file)
    return msg_json, param_json
