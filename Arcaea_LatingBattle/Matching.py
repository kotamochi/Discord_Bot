import csv
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import schedule

class BattleMatching():
    def __init__(self, Setting, client, cmd):
        self.Setting = Setting #設定の読み込み
        self.Command = cmd
        self.MatchRoom = client.get_channel(self.Setting.MatchRoom)
        self.BotRoom = client.get_channel(self.Setting.BotRoom)

    #レート戦開始
    async def BattleStart(self):
        await self.MatchRoom.send("対戦開始~~~~~~~~~~~~~~~~~~~~~~~~~!!!")
        try:
            await self.BattleManagement() #対戦管理関数を起動
        except Exception as e:
            return await self.MatchRoom.send("大会進行に不具合が発生しました。対戦を中断し、運営からの案内をお待ちください")

        await self.MatchRoom.send("対戦終了~~~~~~~~~~~~~~~~~~~~~~~~~!!\nお疲れ様でした！！！")


    #対戦を管理する関数
    async def BattleManagement(self):
        #定期実行スケジュールを作成
        try:
            async with asyncio.timeout(self.Setting.EventTime):             #マッチ時間(対戦時間)を設定
                async with asyncio.TaskGroup() as tg:
                    matchtask = tg.create_task(self.MatchMaking())          #マッチメイキングの関数
                    ranktask = tg.create_task(self.Command.ShowRanking())   #ランキング表示の関数

        except TimeoutError: #対戦期間終了後に実行
            return 


    #マッチ待機者を追加
    async def JoinList(self, user):
        #ユーザーリストからIDを使用して自身のデータを取得
        df_user = pd.read_csv(self.Setting.UserFile)
        df_mydata = df_user[df_user["Discord_ID"] == user]
        
        #データが存在するか確認
        if df_mydata.empty:
            return True, "ユーザーリストに登録されていません。" #ユーザーデータが登録されていないのでエラーを返す
        
        rating = int(df_mydata["Rating"].values) #現在レートを取得
        
        #対戦ステータスを確認
        if df_mydata["State"].item():
            return True, "あなたは現在対戦中です。" #既に対戦中なのでエラーを返す
        
        #ptを参照して各部門のwatinglistに追加する
        if df_mydata["Potential"].values < self.Setting.GroupDivision: #下位部門
            f_num = 0 #idxを指定する
        else:                                                          #上位部門
            f_num = 1 #idxを指定する

        with open(self.Setting.WatingFile[f_num], 'a', newline='') as f: #ファイルを開いて追加
            writer = csv.writer(f)
            writer.writerow([user, rating])
        
        return False, "" #問題なく登録された事を返す
            

    #マッチングが行われたか確認する
    async def MatchCheck(self, user):
        #ユーザーリストからIDを使用して自身のデータを取得
        df_user = pd.read_csv(self.Setting.UserFile)
        df_mydata = df_user[df_user["Discord_ID"] == user]
        
        #ステータスを確認
        if df_mydata["State"].item(): #マッチが決まってるならTrue
            return True
        else:
            return False #決まっていなければFalse
    

    #マッチメイキングを行う関数
    async def MatchMaking(self):
        #n秒おきにマッチング処理を行う
        while True:
            #マッチレート範囲を変数に入れる
            ratingrange = self.Setting.RatingRange

            #2部門分のマッチング処理を行う
            for file in self.Setting.WatingFile:
                #対戦者待ちリストを取得
                df_wating = pd.read_csv(file)

                #データがあるかを確認
                if df_wating.empty or len(df_wating) < 2:
                    pass #データが２件未満なら読み飛ばす

                else:
                    #待機者の上から順にマッチングを行う
                    for _ in range(len(df_wating) // 2): #2人で1マッチなのでリストの1/2の数だけ回す
                        player1 = df_wating.head(1)                                             #待機者のデータ取得
                        player1_rate = int(player1["Rating"].values)                            #レート情報を変数に入れる
                        df_wating.drop(index=0, inplace=True)                                   #player1のデータを削除

                        #待機者リストの上からマッチレート範囲に該当する人のデータを取得
                        range_low, range_high = player1_rate - ratingrange, player1_rate + ratingrange
                        player2 = df_wating.query('@range_low <= Rating <= @range_high')

                        #マッチングが成立しなかった時
                        if player2.empty:
                            df_wating = pd.concat([df_wating, player1])                         #待機者リストの末尾にplayer1のデータを追加
                        
                        #マッチングが成立した時
                        else:
                            drop_idx = df_wating[df_wating["User"] == player2["User"]].index[0] #player2のindexを取得
                            df_wating.drop(index=drop_idx, inplace=True)                        #player2のデータを削除

                            #メッセージを作成
                            messeage = f"~MatchAnnounce~ playerID {int(player1['User'].values)} {int(player2['User'].values)}"

                            #botにマッチが成立したことを知らせる
                            await self.BotRoom.send(messeage)

                    #データをcsvに戻す
                    df_wating.to_csv(file, index=False)
            
            #待機
            await asyncio.sleep(self.Setting.MatchTime)