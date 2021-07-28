# PSO2NGS_LogAnalyzer

PSO2NGSで生成されたログファイルを解析するGUIソフトウェアです。

範囲日時を指定してその間に取得したアイテムのログ、統計を簡単に調べることができます。

![loganagit](https://user-images.githubusercontent.com/45330305/127304279-4213108f-abd4-4fcc-8e9c-3b68a4fd6786.PNG)

# 使い方

Pythonインタプリタ上で動作するものと、Windows10 64bit上で動作するexe版があります。

1. settings.iniのLogFolderDirを編集し、NGSのログがあるフォルダへ変更する。Windows標準のドキュメントのフォルダをCドライブから変更していない場合は変更する必要なし。

2. Python版あるいはexe版を起動。
    1. Python版はコマンドプロンプトにて
       ```
       python LogAnalyzerGUI.py
       ```
    2. GUI版はLogAnalyzerGUI.exeをダブルクリックで実行できます。


# 環境
  * Python版
    * python 3.9.0
  * exe版
    * Windows10 64bit

# 文責
* Haruyuk1
* sa990130@gmail.com
  
