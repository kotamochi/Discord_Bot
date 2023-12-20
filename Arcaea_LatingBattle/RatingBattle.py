import asyncio
import pandas as pd
import discord
import logging
import Music_Select

class BattleManager():
    def __init__(self, Setting, client):
        self.Setting = Setting #設定の読み込み
        self.client = client
        self.MatchRoom = client.get_channel(Setting.MatchRoom)
    
    
    #一連の対戦を管理
    async def rating_battle(self, message):
        try:
            users_id, users, player_data = await self.get_usersdata(message) #対戦者データを取得
            await self.state_change(users_id, True) #ステータスを対戦中に変更
            
            #DMにマッチ通知が届くまで待機
            await asyncio.sleep(3)

            #対戦
            try:
                thread, score1, score2, users, music_ls = await self.singles_scorebattle(users_id, users, player_data)
            #終了を選ばれた時のみ対戦を終わらせてスレッドを閉じる
            except TypeError:
                return await self.state_change(users_id, False) #対戦ステータスを待機中に変更

            #スコア計算
            winner, loser, player1_score, player2_score = await self.score_calculation(score1, score2, users_id[0], users_id[1])

            #レート計算
            winner_rate, loser_rate, ratemove= await self.rate_calculation(winner, loser, player_data)

            #結果を表示
            await self.show_result(thread, users, player1_score, player2_score, winner, loser, winner_rate, loser_rate, ratemove)

            #結果を反映し、ステータスを戻す
            await self.result_reflection(winner, loser, winner_rate, loser_rate)
            
            #30秒後スレッドを閉じて終了
            await asyncio.sleep(1) #間を空ける
            await thread.send(f"このスレッドは30秒後、自働的に削除されます。")
            await asyncio.sleep(30) #スレッド削除まで待機
            await thread.delete() #スレッドを削除
        
        #トラブルがおこった際に表示
        except Exception as e:
            self.Setting.logger.error(e)
            await message.channel.send("タイムアウト、もしくはコマンド不備により対戦が終了されました。")
            await self.state_change(users_id, False) #対戦ステータスを待機中に変更
        
        
    #ユーザーリストでの対戦者のステータスを変更
    async def state_change(self, users_id, State):
        df_user = pd.read_csv(self.Setting.UserFile) #ファイル読み込み
        #データ更新
        df_user.loc[df_user[df_user["Discord_ID"] == users_id[0]].index, "State"] = State
        df_user.loc[df_user[df_user["Discord_ID"] == users_id[1]].index, "State"] = State
        df_user.to_csv(self.Setting.UserFile, index=False) #ファイル保存
    
    
    #結果をファイルに反映する
    async def result_reflection(self, winner, loser, winner_rate, loser_rate):
        State = False
        df_user = pd.read_csv(self.Setting.UserFile) #ファイル読み込み
        #データ更新
        df_user.loc[df_user[df_user["Discord_ID"] == winner].index, "State"] = State
        df_user.loc[df_user[df_user["Discord_ID"] == winner].index, "Rating"] = winner_rate
        df_user.loc[df_user[df_user["Discord_ID"] == loser].index, "State"] = State
        df_user.loc[df_user[df_user["Discord_ID"] == loser].index, "Rating"] = loser_rate
        df_user.to_csv(self.Setting.UserFile, index=False) #ファイル保存
        
        
    #ユーザーデータを整理する
    async def get_usersdata(self, message):
        #渡されたコマンドを分割して、ユーザーidをリストに取り出す
        comannd = message.content.split(' ')
        player_id = [int(comannd[2]), int(comannd[3])]
        
        #対戦者情報を読み込んで、情報を変数に入れていく
        df_user = pd.read_csv(self.Setting.UserFile) #ユーザーファイル読み込み
        player_data = df_user[(df_user["Discord_ID"] == player_id[0]) | (df_user["Discord_ID"] == player_id[1])] #対戦者情報
        player_mention = [f"<@{comannd[2]}>", f"<@{comannd[3]}>"]
        
        return player_id, player_mention, player_data


    #対戦を行う関数    
    async def singles_scorebattle(self, users_id, users, player_data):
        #ユーザーの表示名を取得
        username_1 = self.client.get_user(users_id[0]).display_name
        username_2 = self.client.get_user(users_id[1]).display_name

        #レートを取得
        rate_1 = int(player_data.loc[player_data[player_data["Discord_ID"] == users_id[0]].index, "Rating"].values)
        rate_2 = int(player_data.loc[player_data[player_data["Discord_ID"] == users_id[1]].index, "Rating"].values)

        #ポテンシャルを取得
        pt_1 = float(player_data.loc[player_data[player_data["Discord_ID"] == users_id[0]].index, "Potential"].values)
        pt_2 = float(player_data.loc[player_data[player_data["Discord_ID"] == users_id[1]].index, "Potential"].values)

        #対戦スレッドを作成
        thread = await self.MatchRoom.create_thread(name="{} vs {}".format(username_1, username_2),type=discord.ChannelType.public_thread)
        
        #スレッド内でのエラーをキャッチ
        try:
            #メッセージを作成
            an = f"スレッド：{thread.mention} \n {username_1}と{username_2}の対戦を開始します"
            ms = f"{users[0]}(Pt:{pt_1},Rate:{rate_1}) vs {users[1]}(Pt:{pt_2},Rate:{rate_2}) \n 対戦者のpt基準で課題曲を選択します。"
            
            #メッセージを送信して難易度選択を待機
            await self.MatchRoom.send(an)
            await thread.send(ms)

            #選曲待機時間
            await asyncio.sleep(5)

            #曲、スコアを格納するリスト
            score1, score2, music_ls = [], [], []

            N_music = 2 #対戦曲数を指定(基本的に2)
            count = 0 #何曲目かをカウントする

            while True:
                #課題曲から選曲を行う
                music, level_str, dif, image = await Music_Select.Select_Assignment_Song(pt_1, pt_2)

                #対戦開始前のメッセージを作成
                startmsg1 = f"対戦曲は[{music}] {dif}:{level_str}です!!"
                startmsg2 = "10分以内に楽曲を終了し、スコアを入力してください。例:9950231\n(対戦を途中終了する場合はどちらかが「終了」と入力してください)"
                            
                await thread.send(startmsg1, file=discord.File(image)) #曲のジャケットを表示
                await thread.send(startmsg2)
                await asyncio.sleep(1)

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
                await asyncio.sleep(2)

            return thread, score1, score2, users, music_ls
        
        #スレッド内でトラブルが起こったらスレッドを閉じる
        except Exception as e:
            print(f"{e.__class__.__name__}: {e}")
            await asyncio.sleep(1) #間を空ける
            await thread.send("タイムアウト、もしくはコマンド不備により対戦が終了されました。スレッドを削除します。")
            await asyncio.sleep(3) #スレッド削除まで待機
            await thread.delete()


    #スコア対決の計算
    async def score_calculation(self, user1, user2, name1, name2):

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
    async def rate_calculation(self, win_id, lose_id, player_data):
        #レート差を計算して、倍率調整
        winner_rate = int(player_data.query("Discord_ID == @win_id").loc[:,"Rating"].iloc[-1])
        loser_rate = int(player_data.query("Discord_ID == @lose_id").loc[:,"Rating"].iloc[-1])
        
        ratediff = loser_rate - winner_rate  #差を求める 900 - 1000

        #レート範囲外のレート差の時、レート差が最大分離れているとして扱う
        if ratediff > self.Setting.RatingRange:
            ratediff = self.Setting.RatingRange
        elif ratediff < -self.Setting.RatingRange:
            ratediff = -self.Setting.RatingRange
        else:
            pass

        ratediff = round(ratediff / 20) * 20 #20区切りで一番近い値にする
        ratemove = self.Setting.RateTrend_Dic.get(ratediff) #辞書から上下レート値を取得
        #勝敗に応じたレートを付与する
        winner_rate += ratemove
        loser_rate -= ratemove
        
        return winner_rate, loser_rate, ratemove
    

    #結果を表示
    async def show_result(self, thread, users, player1_score, player2_score, winner, loser, winner_rate, loser_rate, ratemove):
        #表示名を取得
        winner_name = self.client.get_user(winner).display_name
        loser_name = self.client.get_user(loser).display_name
        #結果を送信
        await thread.send(f"{users[0]}: {player1_score:,}\n{users[1]}: {player2_score:,}\nWinner <@{winner}> (+{abs(player1_score - player2_score):,})\n\n"\
                          f"{winner_name}:Rate{winner_rate}(+{ratemove})\n"\
                          f"{loser_name}:Rate{loser_rate}(-{ratemove})\n"
                          )