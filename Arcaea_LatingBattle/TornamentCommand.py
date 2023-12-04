import asyncio
import pandas as pd

class Command():
    def __init__(self, Setting, client):
        self.Setting = Setting #設定の読み込み
        self.client = client
        self.CommandRoom = client.get_channel(self.Setting.CommandRoom)

    #ユーザーリストに自身のデータを追加
    async def Join_UserList(self, message):
        try:
            player = message.author.id
            player_name = self.client.get_user(player).display_name
            cmd, pt= message.content.split(" ")

            df_user = pd.read_csv(self.Setting.UserFile) #ユーザーリストを取得
            #既に登録されているか確認
            if df_user["Discord_ID"].isin([player]).any().any():
                return await message.channel.send("既に登録されているよ")

            joinuser = pd.DataFrame([[player_name, player, pt, 1000, False]], columns=df_user.columns) #新規ユーザーデータを作成
            df_user = pd.concat([df_user, joinuser])
            df_user = df_user.astype({"Discord_ID":"int64", "Rating":"int64"})
            df_user.to_csv(self.Setting.UserFile, index=False)

        except Exception:
            return await message.channel.send("コマンドが間違っているよ!もう一度やり直してみて!")
        

    #現在レートを取得
    async def NowRating(self, dm, userid):
        df_user = pd.read_csv(self.Setting.UserFile) #ユーザーファイル読み込み
        now_rate = int(df_user.query("Discord_ID == @userid").loc[:,"Rating"].values) #自身のレートを取得
        return await dm.send(f"あなたの現在レートは {now_rate} です!") #返信
    

    #現在のランキングを表示
    async def ShowRanking(self):
        #n秒おきにランキング表示処理を行う
        while True:
            #データの読み込み
            df_user = pd.read_csv(self.Setting.UserFile)
            df_user_low = df_user.query("Potential < @self.Setting.GroupDivision").sort_values("Rating", ascending=False)
            df_user_high = df_user.query("Potential >= @self.Setting.GroupDivision").sort_values("Rating", ascending=False)

            #レートで順位づけを行う
            df_user_low["Rank"] = df_user_low["Rating"].rank(ascending=False, method='min') #ランク付け
            df_user_low = df_user_low.set_index("Rank") #ランクをindexに指定
            df_user_high["Rank"] = df_user_high["Rating"].rank(ascending=False, method='min') #ランク付け
            df_user_high = df_user_high.set_index("Rank") #ランクをindexに指定

            #下位部門のランキング表示
            ranking_msg = "現在のランキング [12.39↓部門]"
            for rank, data in df_user_low.iterrows(): #一位から順に表示メッセージを作成
                ranking_msg = f"{ranking_msg}\n"\
                              f"{int(rank)}:{data['Name']} Rate:{data['Rating']}"

            await self.CommandRoom.send(ranking_msg) #送信

            #上位部門のランキング表示
            ranking_msg = "現在のランキング [12.40↑部門]"
            for rank, data in df_user_high.iterrows(): #一位から順に表示メッセージを作成
                ranking_msg = f"{ranking_msg}\n"\
                              f"{int(rank)}:{data['Name']} Rate:{data['Rating']}"

            await self.CommandRoom.send(ranking_msg) #送信
        
            #待機
            await asyncio.sleep(self.Setting.RankingTime)