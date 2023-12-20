import asyncio
import pandas as pd

class Command():
    def __init__(self, Setting, client):
        self.Setting = Setting #設定の読み込み
        self.client = client
        self.CommandRoom = client.get_channel(self.Setting.CommandRoom)
        self.BotRoom = client.get_channel(self.Setting.BotRoom)
        self.EventRoom = client.get_channel(self.Setting.EventRoom)


    async def get_observars(self, ctx):
        '''運営メンバーのIDを取得'''
        #運営ロールをつけている人を取得
        role_member = ctx.guild.get_role(self.Setting.ObserverRole).members
        observers_id = [member.id for member in role_member]

        return observers_id
            

    async def join_userlist(self, ctx, pt):
        '''ユーザー登録を行う'''
        try:
            userid = ctx.user.id
            disp_name = ctx.user.display_name#self.client.get_user(userid).display_name

            df_user = pd.read_csv(self.Setting.UserFile) #ユーザーリストを取得
            #既に登録されているか確認
            if df_user["Discord_ID"].isin([userid]).any().any():
                return await ctx.response.send_message("既に登録されているよ")

            joinuser = pd.DataFrame([[disp_name, userid, pt, 1000, False]], columns=df_user.columns) #新規ユーザーデータを作成
            df_user = pd.concat([df_user, joinuser])
            df_user = df_user.astype({"Discord_ID":"int64", "Rating":"int64"})
            df_user.to_csv(self.Setting.UserFile, index=False)
            
            return await ctx.response.send_message("登録完了!!")

        except Exception:
            return await ctx.response.send_message("コマンドが間違っているよ!もう一度やり直してみて!")
        

    #現在レートをDMに送信
    async def now_rating(self, ctx):
        #エラーをキャッチ
        try:
            #情報を変数に
            user_id = ctx.user.id
            
            df_user = pd.read_csv(self.Setting.UserFile) #ユーザーファイル読み込み
            now_rate = int(df_user.query("Discord_ID == @user_id").loc[:,"Rating"].values) #自身のレートを取得
            return await ctx.response.send_message(f"あなたの現在レートは {now_rate} です!") #返信
        
        except TypeError: #データがないとき
            return await ctx.response.send_message(f"ユーザーデータが登録されていません。") #返信
        except Exception as e: #それ以外の例外
            self.Setting.logger.error(e) #エラーをログに追記
        
    
    #現在のランキングを表示
    async def show_ranking(self):
        #エラーをキャッチ
        try:
            time = 0 #経過時間
            #n秒おきにランキング表示処理を行う
            while True:
                #経過時間を表示
                await self.EventRoom.send(f"---開始{int(time/60)}分経過----------") #送信
                
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

                await self.EventRoom.send(ranking_msg) #送信
                await self.EventRoom.send("---------------------------") #送信

                #上位部門のランキング表示
                ranking_msg = "現在のランキング [12.40↑部門]"
                for rank, data in df_user_high.iterrows(): #一位から順に表示メッセージを作成
                    ranking_msg = f"{ranking_msg}\n"\
                                  f"{int(rank)}:{data['Name']} Rate:{data['Rating']}"

                await self.EventRoom.send(ranking_msg) #送信
                
                await asyncio.sleep(self.Setting.RankingTime) #待機
                time += self.Setting.RankingTime              #経過時間をカウント
        
        #問題が発生した時
        except Exception as e:
            self.Setting.logger.error(e) #エラーをログに追記
            
            
    #参加者全員に現在のレートを送信
    async def my_result_dm(self):
        #エラーをキャッチ
        try:
            df_user = pd.read_csv(self.Setting.UserFile) #ユーザーデータ取得
            for _, player_data in df_user.iterrows():
                dm = await self.client.fetch_user(player_data["Discord_ID"]) #ユーザーのDiscord情報を取得
                await dm.send(f"最終レートは{player_data['Rating']}でした!!") #DMにレートを送信

        #問題が発生した時
        except Exception as e:
            self.Setting.logger.error(e) #エラーをログに追記
            await self.BotRoom.send(f"<@{self.Setting.MasterID}>, エラーが発生したよ")


    #最終結果を表示
    async def show_result(self):
        #エラーをキャッチ
        try:
            #データの読み込み
            df_user = pd.read_csv(self.Setting.UserFile)
            df_user_low = df_user.query("Potential < @self.Setting.GroupDivision").sort_values("Rating", ascending=False)
            df_user_high = df_user.query("Potential >= @self.Setting.GroupDivision").sort_values("Rating", ascending=False)
            
            #レートで順位づけを行う
            df_user_low["Rank"] = df_user_low["Rating"].rank(ascending=False, method='min').astype("int64") #ランク付け
            df_user_low = df_user_low.set_index("Rank") #ランクをindexに指定
            df_user_high["Rank"] = df_user_high["Rating"].rank(ascending=False, method='min').astype("int64") #ランク付け
            df_user_high = df_user_high.set_index("Rank") #ランクをindexに指定
            
            #下位部門のランキング表示
            ranking_msg_low = "最終ランキング [12.39↓部門]"
            for rank, data in df_user_low.iterrows(): #一位から順に表示メッセージを作成
                ranking_msg_low = f"{ranking_msg_low}\n"\
                              f"{int(rank)}:{data['Name']} Rate:{data['Rating']}"
            
            #優勝者を表示
            winner_low = df_user_low[df_user_low.index.values == 1]
            winner_msg_low = "[12.40↓部門]優勝者は..."
            winner_name_low = ""
            for _, data in winner_low.iterrows():
                winner_name_low = f"{winner_name_low}{data['Name']} "
            
            #送信メッセージを作成
            winner_msg_low = "\n" + winner_msg_low + winner_name_low + "!!!🎉🎉🎉"
                
            #結果を送信
            await self.EventRoom.send(ranking_msg_low) #ランキング
            await self.EventRoom.send(winner_msg_low) #優勝者
            
            #上位部門のランキング表示
            ranking_msg_high = "最終ランキング [12.40↑部門]"
            for rank, data in df_user_high.iterrows(): #一位から順に表示メッセージを作成
                ranking_msg_high = f"{ranking_msg_high}\n"\
                              f"{int(rank)}:{data['Name']} Rate:{data['Rating']}"
                              
            #優勝者を表示
            winner_high = df_user_high[df_user_high.index == 1]
            winner_msg_high = "[12.40↑部門]優勝者は..."
            winner_name_high = ""
            for _, data in winner_high.iterrows():
                winner_name_high = f"{winner_name_high}{data['Name']} "
            
            #送信メッセージを作成
            winner_msg_high = "\n" + winner_msg_high + winner_name_high + "!!!🎉🎉🎉"
            
            await self.EventRoom.send(ranking_msg_high) #送信
            await self.EventRoom.send(winner_msg_high) #優勝者
        
        #問題が発生した時
        except Exception as e:
            self.Setting.logger.error(e) #エラーをログに追記
            await self.BotRoom.send(f"<@{self.Setting.MasterID}>, エラーが発生したよ")
