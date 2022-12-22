
class Order():
    def __init__(self, sRQName,sScreenNo,sAccNo, nOrderType,sCode,sCodeName,nQty,nPrice,sHogaGb,
                 sOrgOrderNo ,targetProfitRate,targetLossRate,currentProfitRate,time):
        self.sRQName = sRQName
        self.sScreenNo = sScreenNo
        self.sAccNo = sAccNo
        self.nOrderType = nOrderType
        self.sCode = sCode
        self.sCodeName = sCodeName
        self.nQty = nQty
        self.nPrice = nPrice
        self.sHogaGb = sHogaGb
        self.sOrgOrderNo = sOrgOrderNo
        self.targetProfitRate = targetProfitRate
        self.targetLossRate = targetLossRate
        self.currentProfitRate = currentProfitRate
        self.time = time
