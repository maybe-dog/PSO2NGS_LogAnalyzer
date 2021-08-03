from ActionLog import ActionLogObject, PickUpLog
from ActionLogParser import parseActionLogs
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import configparser
import datetime
import re
import glob
from tkinter.constants import ANCHOR, LEFT, W, Y

# Settings
username = os.environ['USERNAME']
DefaultLogFolderDir = "C:\\{}\\Documents\\SEGA\\PHANTASYSTARONLINE2\\log_ngs".format(username)

inifile = configparser.ConfigParser()
inifile.read("settings.ini")
iniLogFolderDir = inifile.get("Default", "LogFolderDir")

userLogFolderDir = DefaultLogFolderDir if iniLogFolderDir == "Default" else iniLogFolderDir

dateFormat = "%Y-%m-%d %H:%M"

ALL = 0
CAPSULE = 1


""" ボタン押したときにする必要あり
logFiles = glob.glob(userLogFolderDir)
actionFiles = list(filter(lambda x: "ActionLog" in x, logFiles)) # ActionLogのみを抽出
sortedActionFiles = sorted(actionFiles, key=os.path.getmtime) # 更新日時順にソート
"""

# Global Variables
ActionLogObjectList = [] # 読み込んだ全ての取得物のリスト
startTime = None
endTime = None

# Definitions
def loadActionFiles(num) -> list[ActionLogObject]:
    if num < 1:
        messagebox.showwarning("Error", "1以上の整数を入力してください")
        raise Exception("loadActionFiles, 1未満の数字が入力されました")
    global ActionLogObjectList
    logFiles = glob.glob(userLogFolderDir + r"\*")
    actionFiles = list(filter(lambda x: "ActionLog" in x, logFiles)) # ActionLogのみを抽出
    sortedActionFiles = sorted(actionFiles, key=os.path.getmtime) # 更新日時順にソート
    loadNum = min(num, len(sortedActionFiles)) # 読み込む数
    
    return parseActionLogs(sortedActionFiles)

def updateLogTree(treeView: ttk.Treeview, state):
    treeView.delete(*treeView.get_children()) # 要素を全部消す
    filteredActionLogObjectList = list(filter( # 指定した範囲時間でフィルタリング
        lambda alo:startTime <= alo.date and alo.date <= endTime, ActionLogObjectList))
    if state == ALL: # 全て表示
        pass
    elif state == CAPSULE:
        filteredActionLogObjectList = list(filter(lambda alo: isinstance(alo, PickUpLog), filteredActionLogObjectList)) # PickUpLogのみでフィルタリング
        filteredActionLogObjectList = list(filter(lambda alo: alo.type == PickUpLog.CAPSULE, filteredActionLogObjectList)) # カプセルのログのみでフィルタリング
    for alo in filteredActionLogObjectList:
            values = (alo.name, alo.info, alo.date.strftime(dateFormat))
            treeView.insert(parent="", index="end", values=values)
    return

def updateStatTree(treeView: ttk.Treeview, state):
    treeView.delete(*treeView.get_children()) # 要素を全部消す
    filteredActionLogObjectList = list(filter(
        lambda alo:startTime <= alo.date and alo.date <= endTime, ActionLogObjectList))
    if state == ALL:
        pass # TODO
    elif state == CAPSULE:
        capsuleDic = dict()
        for alo in filteredActionLogObjectList:
            if alo.type == PickUpLog.CAPSULE:
                num = alo.getNum() # 入手個数
                if alo.name in capsuleDic:
                    capsuleDic[alo.name] = capsuleDic[alo.name] + num
                else:
                    capsuleDic[alo.name] = num
        sortedCapsuleList = sorted(list(capsuleDic.items()), key=lambda item: item[0])
        for name, quantity in sortedCapsuleList:
            treeView.insert(parent="", index="end", values=(name, quantity))
        return

def updateCallBack(logTreeView, statTreeView, state):
    updateLogTree(logTreeView, state)
    updateStatTree(statTreeView, state)

def startUp(logTreeView, statTreeView, state):
    global ActionLogObjectList
    try:
        ActionLogObjectList = loadActionFiles(10)
        updateCallBack(logTreeView, statTreeView, state)
    except Exception as e:
        print(e)

def main():
    # Window
    root = tk.Tk()
    root.title('PSO2NGS LOG Analyzer')

    # 設定項目
    parFrame1 = tk.Frame(root)

    # 読み込み数
    readFrame = tk.LabelFrame(parFrame1, text="読み込み数", relief="ridge")
    readNumBar = tk.IntVar(value=10)
    readEntry1 = tk.Entry(readFrame, textvariable=readNumBar, width=4)
    
    def readButtonCallBack(num):
        global ActionLogObjectList
        try:
            ActionLogObjectList = loadActionFiles(num)
            updateLogTree(logTreeView, radioVar.get())
            updateStatTree(statTreeView, radioVar.get())
        except Exception as e:
            print(e)

    readButton1 = tk.Button(
        readFrame,
        text="読み込み",
        command=lambda: readButtonCallBack(readNumBar.get())
    )
    
    # 範囲日時
    global startTime, endTime
    rangeFrame = tk.LabelFrame(parFrame1, text="範囲日時", relief="ridge")
    startFrame = tk.Frame(rangeFrame)
    endFrame = tk.Frame(rangeFrame)
    startLabel = tk.Label(startFrame, text="開始時間")
    endLabel = tk.Label(endFrame, text="終了時間")
    endTime = datetime.datetime.now().replace(second=0, microsecond=0) # 秒数以下切り捨て
    startTime = endTime + datetime.timedelta(days=-1)
    startTimeBar = tk.StringVar(value=startTime.strftime(dateFormat))
    endTimeBar = tk.StringVar(value=endTime.strftime(dateFormat))
    startTimeEntry = tk.Entry(startFrame, textvariable=startTimeBar)
    endTimeEntry = tk.Entry(endFrame, textvariable=endTimeBar)

    def startTimeManualSet(event):
        global startTime
        try:
            inputString = startTimeEntry.get()
            inputDate = datetime.datetime.strptime(inputString, dateFormat) # raises ValueError
            startTime = inputDate
            startTimeBar.set(startTime.strftime(dateFormat))
            updateCallBack(logTreeView, statTreeView, radioVar.get())
        except Exception as e:
            messagebox.showwarning("Error", "不正なフォーマットです")
            startTimeBar.set(startTime.strftime(dateFormat)) # エントリーを元に戻す
            print(e)
        
    def endTimeManualSet(event):
        global endTime
        try:
            inputString = endTimeEntry.get()
            inputDate = datetime.datetime.strptime(inputString, dateFormat) # raises ValueError
            endTime = inputDate
            endTimeBar.set(endTime.strftime(dateFormat))
            updateCallBack(logTreeView, statTreeView, radioVar.get())
        except Exception as e:
            messagebox.showwarning("Error", "不正なフォーマットです")
            endTimeBar.set(endTime.strftime(dateFormat)) # エントリーを元に戻す
            print(e)

    startTimeEntry.bind("<Return>", startTimeManualSet)
    endTimeEntry.bind("<Return>", endTimeManualSet)

    def startTimeAdd(hours=0, minutes=0):
        global startTime
        startTime += datetime.timedelta(hours=hours, minutes=minutes)
        startTimeBar.set(startTime.strftime(dateFormat))

    def endTimeAdd(hours=0, minutes=0):
        global endTime
        endTime += datetime.timedelta(hours=hours, minutes=minutes)
        endTimeBar.set(endTime.strftime(dateFormat))

    def timeAddCallBack(func, hours=0, minutes=0):
        func(hours=hours, minutes=minutes)
        updateCallBack(logTreeView, statTreeView, radioVar.get())

    startTimeBack24hButton = tk.Button(
        startFrame,
        text="-24h",
        width=4,
        command=lambda: timeAddCallBack(startTimeAdd, hours=-24)
    )
    startTimeBack1hButton = tk.Button(
        startFrame,
        text="-1h",
        width=4,
        command=lambda: timeAddCallBack(startTimeAdd, hours=-1)
    )
    startTimeBack10mButton = tk.Button(
        startFrame,
        text="-10m",
        width=4,
        command=lambda: timeAddCallBack(startTimeAdd, minutes=-10)
    )
    startTimeBack1mButton = tk.Button(
        startFrame,
        text="-1m",
        width=4,
        command=lambda: timeAddCallBack(startTimeAdd, minutes=-1)
    )
    startTimeForward24hButton = tk.Button(
        startFrame,
        text="+24h",
        width=4,
        command=lambda: timeAddCallBack(startTimeAdd, hours=24)
    )
    startTimeForward1hButton = tk.Button(
        startFrame,
        text="+1h",
        width=4,
        command=lambda: timeAddCallBack(startTimeAdd, hours=1)
    )
    startTimeForward10mButton = tk.Button(
        startFrame,
        text="+10m",
        width=4,
        command=lambda: timeAddCallBack(startTimeAdd, minutes=10)
    )
    startTimeForward1mButton = tk.Button(
        startFrame,
        text="+1m",
        width=4,
        command=lambda: timeAddCallBack(startTimeAdd, minutes=1)
    )
    endTimeBack24hButton = tk.Button(
        endFrame,
        text="-24h",
        width=4,
        command=lambda: timeAddCallBack(endTimeAdd, hours=-24)
    )
    endTimeBack1hButton = tk.Button(
        endFrame,
        text="-1h",
        width=4,
        command=lambda: timeAddCallBack(endTimeAdd, hours=-1)
    )
    endTimeBack10mButton = tk.Button(
        endFrame,
        text="-10m",
        width=4,
        command=lambda: timeAddCallBack(endTimeAdd, minutes=-10)
    )
    endTimeBack1mButton = tk.Button(
        endFrame,
        text="-1m",
        width=4,
        command=lambda: timeAddCallBack(endTimeAdd, minutes=-1)
    )
    endTimeForward24hButton = tk.Button(
        endFrame,
        text="+24h",
        width=4,
        command=lambda: timeAddCallBack(endTimeAdd, hours=24)
    )
    endTimeForward1hButton = tk.Button(
        endFrame,
        text="+1h",
        width=4,
        command=lambda: timeAddCallBack(endTimeAdd, hours=1)
    )
    endTimeForward10mButton = tk.Button(
        endFrame,
        text="+10m",
        width=4,
        command=lambda: timeAddCallBack(endTimeAdd, minutes=10)
    )
    endTimeForward1mButton = tk.Button(
        endFrame,
        text="+1m",
        width=4,
        command=lambda: timeAddCallBack(endTimeAdd, minutes=1)
    )


    # 選択項目
    radioFrame = tk.LabelFrame(parFrame1, text="選択項目", relief="ridge")

    radioVar = tk.IntVar(value=0)
    radioAll = tk.Radiobutton(radioFrame, value=ALL, variable=radioVar, text="全て", 
    command=lambda: updateCallBack(logTreeView, statTreeView, radioVar.get()))
    radioCupsle = tk.Radiobutton(radioFrame, value=CAPSULE, variable=radioVar, text="カプセルのみ",
    command=lambda: updateCallBack(logTreeView, statTreeView, radioVar.get()))

    parFrame2 = tk.Frame(root)

    # ログ表示
    logFrame = tk.LabelFrame(parFrame2, text="ログ表示", relief="ridge")
    logTreeView = ttk.Treeview(logFrame)
    logTreeView["columns"] = ("name", "info", "date")
    logTreeView.column("#0", width=0, stretch="no")
    logTreeView.heading("#0", text="Label")
    logTreeView.heading("name", text="name")
    logTreeView.heading("info", text="info")
    logTreeView.heading("date", text="date")

    logTreeViewScroll = tk.Scrollbar(logFrame, orient=tk.VERTICAL, command=logTreeView.yview)
    logTreeView["yscrollcommand"] = logTreeViewScroll.set


    # 統計表示
    statFrame = tk.LabelFrame(parFrame2, text="統計表示", relief="ridge")
    statTreeView = ttk.Treeview(statFrame)
    statTreeView["columns"] = ("name", "quantity")
    statTreeView.column("#0", width=0, stretch="no")
    statTreeView.column("quantity", width=50)
    statTreeView.heading("#0", text="Label")
    statTreeView.heading("name", text="name")
    statTreeView.heading("quantity", text="quantity")

    statTreeViewScroll = tk.Scrollbar(statFrame, orient=tk.VERTICAL, command=statTreeView.yview)
    statTreeView["yscrollcommand"] = statTreeViewScroll.set
 
    #layout
    parFrame1.pack()

    readFrame.pack(side=LEFT)
    readEntry1.pack(side=LEFT)
    readButton1.pack(side=LEFT)

    rangeFrame.pack(side=LEFT)
    startFrame.pack()
    endFrame.pack()
    startLabel.pack(side=LEFT)
    endLabel.pack(side=LEFT)
    startTimeBack24hButton.pack(side=LEFT)
    startTimeBack1hButton.pack(side=LEFT)
    startTimeBack10mButton.pack(side=LEFT)
    startTimeBack1mButton.pack(side=LEFT)
    startTimeEntry.pack(side=LEFT)
    startTimeForward1mButton.pack(side=LEFT)
    startTimeForward10mButton.pack(side=LEFT)
    startTimeForward1hButton.pack(side=LEFT)
    startTimeForward24hButton.pack(side=LEFT)
    endTimeBack24hButton.pack(side=LEFT)
    endTimeBack1hButton.pack(side=LEFT)
    endTimeBack10mButton.pack(side=LEFT)
    endTimeBack1mButton.pack(side=LEFT)
    endTimeEntry.pack(side=LEFT)
    endTimeForward1mButton.pack(side=LEFT)
    endTimeForward10mButton.pack(side=LEFT)
    endTimeForward1hButton.pack(side=LEFT)
    endTimeForward24hButton.pack(side=LEFT)

    radioFrame.pack(side=LEFT)
    radioAll.pack(anchor=W)
    radioCupsle.pack(anchor=W)

    parFrame2.pack(expand=True, fill=tk.Y)

    logFrame.pack(side=LEFT, expand=True, fill=tk.Y)
    logTreeView.pack(side=LEFT, expand=True, fill=tk.Y)
    logTreeViewScroll.pack(side=LEFT, fill="y")

    statFrame.pack(side=LEFT, expand=True, fill=tk.Y)
    statTreeView.pack(side=LEFT, expand=True, fill=tk.Y)
    statTreeViewScroll.pack(side=LEFT, fill="y")

    root.after_idle(lambda: startUp(logTreeView, statTreeView, radioVar.get()))
    root.mainloop()

if __name__ == "__main__":
    main()






