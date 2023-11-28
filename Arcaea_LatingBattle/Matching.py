import csv
import asyncio
from datetime import datetime, timedelta
import pandas as pd

class BattleMatching():
    def __init__(self, Setting):
        self.Setting = Setting

    #レート戦開始
    async def BattleStart(self, channel):
        channel.send("対戦開始~~~!!!")
        await self.PlayerMatching()

    #マッチ待機者を追加
    async def JoinList(self, user):
        #ユーザーリストから自身のデータを取得
        df_user = pd.read_csv(self.Setting.UserFile)

        number = 0
        #ファイルを開いて追加
        with open(self.file[number], 'a') as f:
            writer = csv.writer(f)
            writer.writerow(user)
            
    async def Match(self, user):

        #対戦者を待機リストに追加
        self.JoinList(user)
        
        

    #定期的に対戦マッチング関数を実行する
    async def PlayerMatching(self):
        start = datetime.now()
        stop = start + timedelta(hours=self.Setting.EventTime)
        while True:
            #2部門分のマッチング処理を行う
            for file in self.Setting.WatingFile:
                #対戦者待ちリストを取得
                data = pd.read_csv(file)

                print(data)

                break
        
        