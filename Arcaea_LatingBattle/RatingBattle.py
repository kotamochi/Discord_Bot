import asyncio
import pandas as pd
import discord

class BattleManager():
    def __init__(self, Setting, client):
        self.Setting = Setting #設定の読み込み
        self.client = client
        self.MatchRoom = client.get_channel(Setting.MatchRoom)
    
    #レート戦を行う関数    
    async def RatingBattle(self, message):
        #渡されたコマンドを分割して、ユーザーidをリストに取り出す
        comannd = message.content.split(' ')
        users_id = [comannd[2], comannd[3]]
        users = [f"<@{comannd[2]}>", f"<@{comannd[3]}>"]
        
        #ステータスを対戦中に変更
        await self.StateChange(users_id, True)
        
        #ユーザーの表示名を取得
        username_1 = self.client.get_user(users_id[0]).display_name
        username_2 = self.client.get_user(users_id[1]).display_name
        #対戦スレッドを作成
        thread = await message.channel.create_thread(name="{} vs {}".format(username_1, username_2),type=discord.ChannelType.public_thread)
        
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
                    music, level_str, dif = Random_Select_Level()
                
                #難易度上下限を指定してる時
                elif len(select_difficult) == 2:
                    level_low = select_difficult[0]
                    level_high = select_difficult[1]
                    music, level_str, dif = Random_Select_Level(level_low, level_high)

                #難易度を指定している時
                elif len(select_difficult) == 1:
                    level = select_difficult[0]
                    music, level_str, dif = Random_Select_Level(level)

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

        
    #ユーザーリストでの対戦者のステータスを変更
    async def StateChange(self, users_id, State):
        df_user = pd.read_csv(self.Setting.UserFile) #ファイル読み込み
        df_user.loc[df_user[df_user["User"] == users_id[0]].index, "State"] = State
        df_user.loc[df_user[df_user["User"] == users_id[1]].index, "State"] = State
        df_user.to_csv(self.Setting.UserFile) #ファイル保存
        
        