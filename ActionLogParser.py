from ActionLog import *


def parseActionLogs(actionFiles) -> list[ActionLogObject]:
    def lineToActionLogObject(line) -> ActionLogObject:
        actionList = re.split(r"\t+", line)
        if len(actionList) <= 5: # 5要素以下のラインは無視
            return None
        date = actionList[0]
        logType = actionList[2]
        name = actionList[5]
        info = actionList[6] if len(actionList) >= 7 else None
        if "[Pickup]" == logType:
            return PickUpLog(date, name, info)
        elif "[Discard]" == logType:
            return DiscardLog(date, name, info)
        elif "[DiscradExchange]" == logType:
            return DiscardExchangeLog(date, name, info)
        else: # どのアクションログにも当てはまらないものはNoneを返す
            return None 

    actionLogObjectList = []

    for actionFile in actionFiles:
        with open(actionFile, "r", encoding="utf-16") as f:
            lines = f.read().splitlines()
            tempList = list(filter(lambda x: x is not None, map(lineToActionLogObject, lines)))
            actionLogObjectList += tempList

    actionLogObjectList.sort(key=lambda x:x.date)
    return actionLogObjectList
    
