import csv
import asyncio
import pandas as pd

class BattleMatching():
    def __init__(self):
        self.file = "Datas\MatchWaitlist.csv"

    #マッチ待機者を追加
    async def JoinList(self, user):
        #ファイルを開いて追加
        with open(self.file, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(user)
            
    async def Match(self, user):
        #対戦者を待機リストに追加
        self.JoinList(user)
        
        #現在の待ちリストを取得
        match_df = pd.read_csv(self.file)
        
        