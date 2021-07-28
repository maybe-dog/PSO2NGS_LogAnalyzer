import glob
import os
import datetime
import re
import pprint
import json

LogFolderDir = r'D:\Shunsuke\Documents\SEGA\PHANTASYSTARONLINE2\log_ngs' + r'\*' 
CapsuleLogSaveFolderDir = r'.\capsuleLog' + '\\'

logFiles = glob.glob(LogFolderDir)
actionFiles = list(filter(lambda x: "ActionLog" in x, logFiles)) # ActionLogのみを抽出
latestActionFile = max(actionFiles, key=os.path.getmtime) # 最新のものを取得

class PUObject:
    def __init__(self, date, name, info):
        self.date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        self.name = name
        self.info = info

    def __str__(self) -> str:
        return "アイテム名:{}, 情報:{}, 日付:{}".format(self.date, self.info, self.date)

def lineToPUObject(line):
    puList = re.split(r"\t+", line)
    # print(puList)
    date = puList[0]
    name = puList[5]
    info = puList[6] if len(puList) >= 7 else None
    return PUObject(date, name, info)

# print(latestActionFile)

capsuleDic = dict()
meseta = 0

with open(latestActionFile, "r", encoding='utf-16') as f:
    lines = f.read().splitlines()
    pickUpLines = list(filter(lambda x: "Pickup" in x, lines))
    puObjectList = list(map(lineToPUObject, pickUpLines))
    
    for po in puObjectList:
        if "C/" in po.name: # カプセル入手ログ
            num = int(re.search(r"Num\((\d+)\)", po.info).group(1)) # 入手個数
            if po.name in capsuleDic:
                capsuleDic[po.name] = capsuleDic[po.name] + num
            else:
                capsuleDic[po.name] = num
        if "Meseta" in po.name: # メセタ入手ログ
            accquire = int(re.search(r"Meseta\((\d+)\)", po.name).group(1)) # 入手メセタ
            meseta += accquire 
    
pprint.pprint(capsuleDic)
print("拾ったメセタ:{}".format(meseta))

today = datetime.date.today()

with open(CapsuleLogSaveFolderDir + "capsuleLog{}.txt".format(today), "a") as f:
    f.write("=================={} outputed==================".format(datetime.datetime.now()))
    json.dump(capsuleDic, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.write("===============================================")





    
