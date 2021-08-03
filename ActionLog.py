from abc import ABCMeta, abstractmethod
import datetime
import re

# Settings
LogDateFormat = "%Y-%m-%dT%H:%M:%S"



class ActionLogObject(metaclass=ABCMeta):
    def __str__(self) -> str:
        return "アイテム名:{}, 情報:{}, 日付:{}".format(self.date, self.info, self.date)


class PickUpLog(ActionLogObject):
    ITEM = 0
    CUPSLE = 1
    MESETA = 2

    def __init__(self, date, name, info):
        self.date = datetime.datetime.strptime(date, LogDateFormat)
        if "C/" in name: # カプセル入手ログ
            self.type = self.CUPSLE
            self.name = name
            self.info = info
        elif "Meseta" in name: # メセタ入手ログ
            self.type = self.MESETA
            self.name = name
            self.info = info
        else: # アイテム入手ログ
            self.type = self.ITEM
            self.name = name
            self.info = info

    def getCurrentMeseta(self) -> int:
        if self.type == self.MESETA:
            return int(re.search(r"CurrentMeseta\((\d+)\)", self.info).group(1)) # 現在のメセタ
        else:
            raise TypeError("getCurrentMeseta() is supported for only Meseta Log.")

    def getNum(self) -> int:
        if self.type == self.MESETA:
            return int(re.search(r"Meseta\((\d+)\)", self.name).group(1))
        else:
            if re.match(r"Num\((\d+)\)", self.info):
                return int(re.search(r"Num\((\d+)\)", self.info).group(1))
            else:
                return 1

    def __str__(self) -> str:
        return "[拾得]" + super().__str__()

class DiscardLog(ActionLogObject):
    def __init__(self, date, name, info):
        self.date = datetime.datetime.strptime(date, LogDateFormat)
        self.name = name
        self.info = info

    def __str__(self) -> str:
        return "[売却]" + super().__str__()
    
class DiscardExchangeLog(ActionLogObject):
    def __init__(self, date, name, info):
        self.date = datetime.datetime.strptime(date, LogDateFormat)
        self.name = name
        accquire = int(re.search(r"Meseta\((\d+)\)", name).group(1)) # 入手メセタ
        current = int(re.search(r"CurrentMeseta\((\d+)\)", info).group(1)) # 現在のメセタ
        self.info = [accquire, current]

    def getNum(self):
        return self.info[0]

    def getCurrentMeseta(self):
        return self.info[1]

    def __str__(self) -> str:
        return "[売却で取得]" + super().__str__()