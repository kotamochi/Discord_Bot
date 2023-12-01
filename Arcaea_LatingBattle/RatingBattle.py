import asyncio
import pandas as pd
import discord
import Music_Select

class BattleManager():
    def __init__(self, Setting, client):
        self.Setting = Setting #設定の読み込み
        self.client = client
        self.MatchRoom = client.get_channel(Setting.MatchRoom)
    
    
    #一連の対戦を管理
    async def RatingBattle(self, message):
        try:
            users_id, users, player_data = await self.Get_UsersData(message)
            #ステータスを対戦中に変更
            await self.StateChange(users_id, True)

            #対戦
            try:
                thread, score1, score2, users, music_ls = await self.Singles_ScoreBattle(users_id, users)
            #終了を選ばれた時のみ対戦を終わらせてスレッドを閉じる
            except TypeError:
                return await message.reply(f"対戦が途中で終了されました。お疲れ様でした。")

            #スコア計算
            winner, loser, player1_score, player2_score = await self.ScoreCalculation(score1, score2, users_id[0], users_id[1])

            #レート計算
            winner_rate, loser_rate = await self.RateCalculation(winner, loser, player_data)

            #結果を表示
            await self.ShowResult(thread, users, player1_score, player2_score, winner)

            #結果を反映し、ステータスを戻す
            await self.ResultReflection(winner, loser, winner_rate, loser_rate)
            
            #30秒後スレッドを閉じて終了
            await asyncio.sleep(1) #間を空ける
            await thread.send(f"このスレッドは30秒後、自働的に削除されます。")
            await asyncio.sleep(30) #スレッド削除まで待機
            await thread.delete() #スレッドを削除
        
        #トラブルがおこった際に表示
        except Exception:
            await message.channel.send("タイムアウト、もしくはコマンド不備により対戦が終了されました。")
            await self.StateChange(users_id, False)
        
        
    #ユーザーリストでの対戦者のステータスを変更
    async def StateChange(self, users_id, State):
        df_user = pd.read_csv(self.Setting.UserFile) #ファイル読み込み
        #データ更新
        df_user.loc[df_user[df_user["Discord_ID"] == users_id[0]].index, "State"] = State
        df_user.loc[df_user[df_user["Discord_ID"] == users_id[1]].index, "State"] = State
        df_user.to_csv(self.Setting.UserFile, index=False) #ファイル保存
    
    #結果をファイルに反映する
    async def ResultReflection(self, winner, loser, winner_rate, loser_rate):
        State = False
        df_user = pd.read_csv(self.Setting.UserFile) #ファイル読み込み
        #データ更新
        df_user.loc[df_user[df_user["Discord_ID"] == winner].index, "State"] = State
        df_user.loc[df_user[df_user["Discord_ID"] == winner].index, "Rating"] = winner_rate
        df_user.loc[df_user[df_user["Discord_ID"] == loser].index, "State"] = State
        df_user.loc[df_user[df_user["Discord_ID"] == loser].index, "Rating"] = loser_rate
        df_user.to_csv(self.Setting.UserFile, index=False) #ファイル保存
        
        
    #ユーザーデータを整理する
    async def Get_UsersData(self, message):
        #渡されたコマンドを分割して、ユーザーidをリストに取り出す
        comannd = message.content.split(' ')
        player_id = [int(comannd[2]), int(comannd[3])]
        
        #対戦者情報を読み込んで、情報を変数に入れていく
        df_user = pd.read_csv(self.Setting.UserFile) #ユーザーファイル読み込み
        player_data = df_user[(df_user["Discord_ID"] == player_id[0]) | (df_user["Discord_ID"] == player_id[1])] #対戦者情報
        player_mention = [f"<@{comannd[2]}>", f"<@{comannd[3]}>"]
        
        return player_id, player_mention, player_data


    #対戦を行う関数    
    async def Singles_ScoreBattle(self, users_id, users):
        #ユーザーの表示名を取得
        username_1 = self.client.get_user(users_id[0]).display_name
        username_2 = self.client.get_user(users_id[1]).display_name
        
        #対戦スレッドを作成
        thread = await self.MatchRoom.create_thread(name="{} vs {}".format(username_1, username_2),type=discord.ChannelType.public_thread)
        
        #スレッド内でのエラーをキャッチ
        try:
            #難易度選択時のメッセージチェック関数
            def checkLv(m):
                try:
                    ms = m.content.split() #受け取ったメッセージをlistに
                    for n in ms:
                        if n[-1] == "+":
                            float(n[:-1]) #数値であるか検証
                        elif n == "all":
                            pass
                        else:
                            float(n) #数値であるか判定
                    return True
                except Exception:
                    return False
            
            #メッセージを作成
            an = f"スレッド：{thread.mention} \n {username_1}と{username_2}の対戦を開始します"
            ms = f"{users[0]} {users[1]} \n 120秒以内に難易度を選択して下さい(全曲の場合は「all」と入力してください)"
            
            #メッセージを送信して難易度選択を待機
            await self.MatchRoom.send(an)
            await thread.send(ms)

            #メッセージを受け取ったスレッドに対してのみ返す
            while True:
                msg = await self.client.wait_for('message', check=checkLv, timeout=120)
        
                if thread.id == msg.channel.id:
                    break
                else:
                    pass

            #渡されたコマンドを分割
            select_difficult = msg.content.split(' ')

            score1, score2, music_ls = [], [], []

            N_music = 2 #対戦曲数を指定(基本的に2)
            count = 0 #何曲目かをカウントする

            while True:
                #難易度を指定していない時
                if select_difficult[0] == "ALL" or select_difficult[0] == "all":
                    music, level_str, dif = Music_Select.Random_Select_Level()
                
                #難易度上下限を指定してる時
                elif len(select_difficult) == 2:
                    level_low = select_difficult[0]
                    level_high = select_difficult[1]
                    music, level_str, dif = Music_Select.Random_Select_Level(level_low, level_high)

                #難易度を指定している時
                elif len(select_difficult) == 1:
                    level = select_difficult[0]
                    music, level_str, dif = Music_Select.Random_Select_Level(level)

                #対戦開始前のメッセージを作成
                startmsg = f"対戦曲は[{music}] {dif}:{level_str}です!!\n\n10分以内に楽曲を終了し、スコアを入力してください。\n例:9950231\n(対戦を途中終了する場合はどちらかが「終了」と入力してください)"
                await asyncio.sleep(1)
                await thread.send(startmsg)
                await asyncio.sleep(0.5)

                def check(m): #通常スコア用チェック関数
                    try:
                        ms = m.content.split(' ')
                        if len(ms) == 1:
                            for i in ms:
                                int(i)
                            return True
                    except Exception:
                        if m.content == "終了" or m.content == "引き直し": #終了か引き直しと入力した場合のみok
                            return True
                        return False
                    
                await thread.send(f"{users[0]}さんのスコアを入力してください。\n楽曲を再選択する場合は「引き直し」と入力してください")

                #メッセージを受け取ったスレッドに対してのみ返す
                while True:
                    BattleRisult1 = await self.client.wait_for('message', check=check, timeout=600)
                    if thread.id == BattleRisult1.channel.id:
                        break
                    else:
                        pass
                
                await asyncio.sleep(0.5)
                #引き直しが選択されたら選曲まで戻る
                if BattleRisult1.content == "引き直し":
                    continue

                await thread.send(f"{users[1]}さんのスコアを入力してください。")
            
                #メッセージを受け取ったスレッドに対してのみ返す
                while True:
                    BattleRisult2 = await self.client.wait_for('message', check=check, timeout=120)
                    if thread.id == BattleRisult2.channel.id:
                        break
                    else:
                        pass 
                
                await asyncio.sleep(1)

                score1.append(BattleRisult1.content)
                score2.append(BattleRisult2.content)

                #どちらかが終了と入力したら終わる
                if BattleRisult1.content == "終了" or BattleRisult2.content == "終了":
                    await thread.send(f"対戦が途中で終了されました。お疲れ様でした。")
                    await asyncio.sleep(3)
                    await thread.delete()
                    return
                
                #対戦曲数を数える
                count += 1

                #選択曲をレコード用に取得
                music_ls.append(f"{music} {dif} {level_str}")
                        
                #最終曲になったらループを抜ける
                if count == N_music:
                    await thread.send(f"対戦が終了しました。結果を集計します。")
                    await asyncio.sleep(3)
                    break

                await thread.send(f"{count}曲目お疲れ様でした！！ {count+1}曲目の選曲を行います。")
                await asyncio.sleep(3)

            return thread, score1, score2, users, music_ls
        
        #スレッド内でトラブルが起こったらスレッドを閉じる
        except Exception:
            await asyncio.sleep(1) #間を空ける
            await thread.send("タイムアウト、もしくはコマンド不備により対戦が終了されました。スレッドを削除します。")
            await asyncio.sleep(3) #スレッド削除まで待機
            await thread.delete()


    #スコア対決の計算
    async def ScoreCalculation(self, user1, user2, name1, name2):

        #対戦者名とスコアを取得
        user1_score = 0
        user2_score = 0
        for score1, score2 in zip(user1, user2):

            user1_score += int(score1)
            user2_score += int(score2)

        if user1_score > user2_score:    #user1の勝利
            return name1, name2, user1_score, user2_score
        elif user1_score == user2_score: #引き分け
            return name1, name2, user1_score, user2_score
        else:                            #user2の勝利
            return name2, name1, user1_score, user2_score


    #レート計算を行う
    async def RateCalculation(self, win_id, lose_id, player_data):
        #レート差を計算して、倍率調整
        winner_rate = int(player_data.query("Discord_ID == @win_id").loc[:,"Rating"].values)
        loser_rate = int(player_data.query("Discord_ID == @lose_id").loc[:,"Rating"].values)
        
        ratediff = loser_rate - winner_rate  #差を求める 900 - 1000
        ratediff = round(ratediff / 20) * 20 #20区切りで一番近い値にする
        ratemove = self.Setting.RateTrend_Dic.get(ratediff) #辞書から上下レート値を取得
        #勝敗に応じたレートを付与する
        winner_rate += ratemove
        loser_rate -= ratemove
        
        return winner_rate, loser_rate
    

    #結果を表示
    async def ShowResult(self, thread, users, player1_score, player2_score, winner):
        await thread.send(f"{users[0]}: {player1_score}\n{users[1]}: {player2_score}\n\n勝者は <@{winner}> さんでした!!お疲れ様でした!!")
        
    #現在レートを取得
    async def NowRating(self, dm, userid):
        df_user = pd.read_csv(self.Setting.UserFile) #ユーザーファイル読み込み
        now_rate = int(df_user.query("Discord_ID == @userid").loc[:,"Rating"].values) #自身のレートを取得
        return await dm.send(f"あなたの現在レートは {now_rate} です!!") #返信
        