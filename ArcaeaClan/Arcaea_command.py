import csv
import math
import random
import asyncio
import discord
import pandas as pd


#難易度ランダム選曲
def Random_Select_Level(level1="0", level2="12"):
    
    #＋難易度が指定された時は.7表記に変更する
    try:
        #引き数を数値型に変換
        level1 = float(level1)
    except ValueError:
        #引き数を数値型に変換
        if level1[-1] == "+":
            level1 = float(level1[:-1]) + 0.7
    
    try:        
        level2 = float(level2)
    except ValueError:
        if level2[-1] == "+":
            level2 = float(level2[:-1]) + 0.7
        
    #指定レベルが一つならその難易度のみから選曲
    if level2 == 12.0 and level1 != 0.0:
        level2 = float(level1)
    
    #楽曲情報をデータフレームに読み込む
    df_music = pd.read_csv("Arcaea_Music_Data.csv")
    
    #楽曲数を取得
    df_music_FTR = df_music[df_music["FTR_Level"] >= level1].copy()
    df_music_FTR = df_music_FTR[df_music_FTR["FTR_Level"] <= level2]

    df_music_BYD = df_music[df_music["BYD_Level"] >= level1].copy()
    df_music_BYD = df_music_BYD[df_music_BYD["BYD_Level"] <= level2]

    df_range_music = pd.concat([df_music_FTR, df_music_BYD])
    
    #乱数の範囲を取得
    music_num = len(df_range_music)

    #乱数を作成
    rand = random.randint(0,music_num-1)

    #乱数から選ばれた楽曲を抽出
    hit_music = df_range_music.iloc[rand]

    #結果を保存
    music = hit_music["Music_Title"]
    if pd.isnull(hit_music["BYD_Level"]) == True: #BYDのレベルデータがあるデータならBYDを結果として出力する
        level = hit_music["FTR_Level"]
        deffecult = "FTR" #難易度を表示
    else:
        level = hit_music["BYD_Level"]
        deffecult = "BYD" #難易度を表示

    #楽曲レベルを表示用に調整
    if level % 1 != 0.0:
        level_str = str(math.floor(level)) + "+"
    else:
        level_str = str(math.floor(level))
        
    return music, level_str, deffecult


#スコアバトルを行う関数
async def Arcaea_ScoreBattle(client, message, batlle_sys):
    try:
        #シングルス対決
        if batlle_sys == 0 or batlle_sys == 1:
            try:
                #対決を実行
                thread, score1, score2, users, music_ls = await Singles_RandomScoreBattle(client, message, batlle_sys)
            #終了を選ばれた時のみ対戦を終わらせてスレッドを閉じる
            except TypeError:
                return await message.reply(f"対戦が途中で終了されました。お疲れ様でした。")
                
            #対戦方式によってスコア計算を分岐
            if batlle_sys == 0: #通常スコア対決
                #得点を計算
                winner, loser, player1_score, player2_score = await Score_Battle(score1, score2, users[0], users[1])
            elif batlle_sys == 1: #EXスコア対決
                #得点を計算
                winner, loser, player1_score, player2_score, Drow_Flg = await EX_Score_Battle(score1, score2, users[0], users[1])
        
            #メンションをUserIDに変換
            winner_id = int(winner[2:-1])
            loser_id = int(loser[2:-1])
            user_name1 = client.get_user(int((users[0])[2:-1])).display_name
            user_name2 = client.get_user(int((users[1])[2:-1])).display_name

            #勝負形式を取得
            if batlle_sys == 1:
                vs_format = "EXScoreBattle"
            else:
                vs_format = "ScoreBattle"
            
            #勝敗をスレッドに表示
            if player1_score == player2_score:
                await thread.send(f"結果は両者{player1_score} で引き分けです!!お疲れ様でした")
                Drow_Flg = True
                #表示用のリザルトを作成
                result = f"[{vs_format}]\n"\
                         f"・1曲目 {music_ls[0]}\n{user_name1}：{score1[0]}\n{user_name2}：{score2[0]}\n"\
                         f"・2曲目 {music_ls[1]}\n{user_name1}：{score1[1]}\n{user_name2}：{score2[1]}\n"\
                         f"・Total\n{user_name1}：{player1_score}\n{user_name2}：{player2_score}\n\n"\
                         f"Drow：{client.get_user(winner_id).display_name, client.get_user(loser_id).display_name}!!"
            
            else:
                await thread.send(f"{users[0]}: {player1_score}\n{users[1]}: {player2_score}\n\n勝者は{winner}さんでした!!お疲れ様でした!!")
                Drow_Flg = False
                #表示用のリザルトを作成
                result = f"[{vs_format}]\n"\
                         f"・1曲目 {music_ls[0]}\n{user_name1}：{score1[0]}\n{user_name2}：{score2[0]}\n"\
                         f"・2曲目 {music_ls[1]}\n{user_name1}：{score1[1]}\n{user_name2}：{score2[1]}\n"\
                         f"・Total\n{user_name1}：{player1_score}\n{user_name2}：{player2_score}\n\n"\
                         f"Winner：{client.get_user(winner_id).display_name}!!"

            #csvファイルに保存
            df_log = pd.read_csv("BattleLog.csv")
            now_data = [[winner_id, loser_id, Drow_Flg]]
            df_now = pd.DataFrame(now_data, columns=["Winner", "Loser", "Drow_Flg"])
            df_log = pd.concat([df_log, df_now])
            df_log.to_csv("BattleLog.csv", index=False)
            
        #ダブルス対決
        elif batlle_sys == 2:
            try:
                #対戦を実行
                thread, team1, team2, users, music_ls =  await Doubles_RandomScoreBattle(client, message)
            #終了を選ばれた時のみ対戦を終わらせてスレッドを閉じる
            except TypeError:
                return await message.reply(f"対戦が途中で終了されました。お疲れ様でした。")
            
            #スコアを計算
            winner, loser, team1_score, team2_score = await Score_Battle(team1, team2, users[0], users[2])
            
            #メンションをUserIDに変換
            winner_id = int(winner[2:-1])
            loser_id = int(loser[2:-1])
            team1_user_name1 = f"{client.get_user(int((users[0])[2:-1])).display_name},{client.get_user(int((users[1])[2:-1])).display_name}"
            team2_user_name2 = f"{client.get_user(int((users[2])[2:-1])).display_name},{client.get_user(int((users[3])[2:-1])).display_name}"
            #勝者チームの2人を取得
            if winner == users[0]:
                winner1 = users[0]
                winner2 = users[1]
            else:
                winner1 = users[2]
                winner2 = users[3]

            #勝敗をスレッドに表示
            if team1_score == team2_score:
                await thread.send(f"結果は両チーム{team1_score} で引き分け!!お疲れ様!!!")
                #表示用のリザルトを作成
                result = f"[ScoreBattle(Team)]\n"\
                         f"・1曲目 {music_ls[0]}\n"\
                         f"{team1_user_name1}チーム：{int(team1[0]) + int(team1[1])}\n"\
                         f"{team2_user_name2}チーム：{int(team2[0]) + int(team2[1])}\n"\
                         f"・2曲目 {music_ls[1]}\n"\
                         f"{team1_user_name1}チーム：{int(team1[2]) + int(team1[3])}\n"\
                         f"{team2_user_name2}チーム：{int(team2[2]) + int(team2[3])}\n"\
                         f"・Total\n{team1_user_name1}：{team1_score}\n"\
                         f"{team2_user_name2}：{team2_score}\n"\
                          "\n"\
                         f"Drow：{team1_user_name1}チーム {team2_user_name2}チーム!"
            else:
                await thread.send(f"{users[0]}チーム: {team1_score}\n{users[2]}チーム: {team2_score}\n\n勝者は{winner1}, {winner2}チーム!!おめでとう!!お疲れ様!!")
                #表示用のリザルトを作成
                result = f"[ScoreBattle(Team)]]\n"\
                         f"・1曲目 {music_ls[0]}\n"\
                         f"{team1_user_name1}チーム：{int(team1[0]) + int(team1[1])}\n"\
                         f"{team2_user_name2}チーム：{int(team2[0]) + int(team2[1])}\n"\
                         f"・2曲目 {music_ls[1]}\n"\
                         f"{team1_user_name1}チーム：{int(team1[2]) + int(team1[3])}\n"\
                         f"{team2_user_name2}チーム：{int(team2[2]) + int(team2[3])}\n"\
                         f"・Total\n{team1_user_name1}：{team1_score}\n"\
                         f"{team2_user_name2}：{team2_score}\n"\
                          "\n"\
                         f"Winner：{client.get_user(int(winner1[2:-1])).display_name},{client.get_user(int(winner2[2:-1])).display_name}チーム!!"

        #対戦結果をチャンネルに表示
        await message.reply(result)
        
        #30秒後スレッドを閉じる
        await asyncio.sleep(1) #間を空ける
        await thread.send(f"このスレッドは30秒後、自働的に削除されます。")
        await asyncio.sleep(30) #スレッド削除まで待機
        await thread.delete() #スレッドを削除
        
    #トラブルがおこった際に表示
    except Exception as error:
        print(type(error))
        print(error.args)
        await message.channel.send("タイムアウト、もしくはコマンド不備により対戦が終了されました。")
        


#1vs1で戦う時のフォーマット
async def Singles_RandomScoreBattle(client, message, EX_flg):
    #渡されたコマンドを分割
    comannd = message.content.split(' ')
    users = [comannd[2], comannd[3]]
    users_id = [int((comannd[2])[2:-1]), int((comannd[3])[2:-1])]
    
    #勝負形式を取得
    if EX_flg == 1:
        vs_format = "EXScoreBattle"
    else:
        vs_format = "ScoreBattle"

    #同じ人が対戦することを防ぐ
    if len(comannd) == 4 and users[0] != users[1]:
        username_1 = client.get_user(users_id[0]).display_name
        username_2 = client.get_user(users_id[1]).display_name
        #対戦スレッドを作成
        thread = await message.channel.create_thread(name="{} vs {}：{}".format(username_1, username_2, vs_format),type=discord.ChannelType.public_thread)

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

            if EX_flg == True:
                an = f"スレッド：{thread.mention} \n {username_1}と{username_2}のEXスコア対戦を開始します"
                ms = f"{users[0]} {users[1]} \n 120秒以内に難易度を選択して下さい(全曲の場合は「all」と入力してください)"
            else:    
                an = f"スレッド：{thread.mention} \n {username_1}と{username_2}のスコア対戦を開始します"
                ms = f"{users[0]} {users[1]} \n 120秒以内に難易度を選択して下さい(全曲の場合は「all」と入力してください)"
            
            #メッセージを送信して難易度選択を待機
            await message.channel.send(an)
            await thread.send(ms)
        
            #メッセージを受け取ったスレッドに対してのみ返す
            while True:
                msg = await client.wait_for('message', check=checkLv, timeout=120)
        
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
                if EX_flg == True: 
                    startmsg = f"対戦曲は[{music}] {dif}:{level_str}です!!\n\n10分以内に楽曲を終了し、EXスコアを入力してください。\n例:1430 1392 13 7 (pure数,内部pure数,far数,lost数)\n(対戦を途中終了する場合はどちらかが「終了」と入力してください)"
                else:
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
                    
                def checkEX(m): #EXスコア用チェック関数
                    try:
                        ms = m.content.split(' ')
                        if len(ms) == 4:
                            for i in ms:
                                int(i)
                            return True
                    except Exception:
                        if m.content == "終了" or m.content == "引き直し": #終了か引き直しと入力した場合のみok
                            return True
                        return False
                    
                await thread.send(f"{users[0]}さんのスコアを入力してください。\n楽曲を再選択する場合は「引き直し」と入力してください")

                if EX_flg == True:
                    #メッセージを受け取ったスレッドに対してのみ返す
                    while True:
                        BattleRisult1 = await client.wait_for('message', check=checkEX, timeout=600)
                        if thread.id == BattleRisult1.channel.id:
                            break
                        else:
                            pass
                else:
                    #メッセージを受け取ったスレッドに対してのみ返す
                    while True:
                        BattleRisult1 = await client.wait_for('message', check=check, timeout=600)
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
                if EX_flg == True:
                    while True:
                        BattleRisult2 = await client.wait_for('message', check=checkEX, timeout=120)
                        if thread.id == BattleRisult2.channel.id:
                            break
                        else:
                            pass
                else:
                    while True:
                        BattleRisult2 = await client.wait_for('message', check=check, timeout=120)
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
            
    else:
        #例外処理に持っていく
        raise Exception("")


#ダブルススコアバトルを行う関数
async def Doubles_RandomScoreBattle(client, message):
    #渡されたコマンドを分割
    comannd = message.content.split(' ')
    users = [comannd[2], comannd[3], comannd[4], comannd[5]]
    users_id = [int(user[2:-1]) for user in users]

    if len(comannd) == 6 and len(users) == len(set(users)):
        username_1 = client.get_user(users_id[0]).display_name
        username_2 = client.get_user(users_id[2]).display_name
        #対戦スレッドを作成
        thread = await message.channel.create_thread(name="{}チーム vs {}チーム：ScoreBattle".format(username_1, username_2),type=discord.ChannelType.public_thread)

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
        
            an = f"スレッド：{thread.mention} \n {username_1}チームと{username_2}チームのスコア対戦を開始します"
            ms = f"{users[0]}, {users[1]}チームと{users[2]}, {users[3]}チーム \n 120秒以内に難易度を選択して下さい(全曲の場合は「all」と入力してください)"
            
            #メッセージを送信して難易度選択を待機
            await message.channel.send(an)
            await thread.send(ms)            

            #メッセージを受け取ったスレッドに対してのみ返す
            while True:
                msg = await client.wait_for('message', check=checkLv, timeout=120)
        
                if thread.id == msg.channel.id:
                    break
                else:
                    pass

            #渡されたコマンドを分割
            select_difficult = msg.content.split(' ')

            team1, team2, music_ls = [], [], []

            N_music = 2 #対戦曲数を指定(基本的に2)
            count = 0 #何曲目かをカウントする

            while True:
                #難易度を指定していない時
                if select_difficult[0] == "ALL" or select_difficult[0] == "all":
                    music, level_str, dif = Random_Select_Level()

                #難易度の上下限を指定している時
                elif len(select_difficult) == 2:
                    level_low = select_difficult[0]
                    level_high = select_difficult[1]
                    music, level_str, dif = Random_Select_Level(level_low, level_high)

                #難易度を指定している時
                elif len(select_difficult) == 1:
                    level = select_difficult[0]
                    music, level_str, dif = Random_Select_Level(level)

                #対戦開始前のメッセージを作成
                startmsg = f"対戦曲は[{music}] {dif}:{level_str}です!!\n\n10分以内に楽曲を終了してスコアを入力してね。\n例:9950231\n(対戦を途中終了する時は、チームの１人目が「終了」と入力してください)"
                await asyncio.sleep(1)
                await thread.send(startmsg)
                await asyncio.sleep(0.5)

                #スコア報告チェック関数
                def check(m):
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
            
                #team1のスコアを集計
                await thread.send(f"{users[0]}チーム１人目のスコアを入力してね。\n楽曲を再選択する場合は「引き直し」と入力してください")
                #メッセージを受け取ったスレッドに対してのみ返す
                while True:
                    BattleRisult1 = await client.wait_for('message', check=check, timeout=600)
                    if thread.id == BattleRisult1.channel.id:
                        break
                    else:
                        pass
                    
                await asyncio.sleep(1)
                #引き直しが選択されたら選曲まで戻る
                if BattleRisult1.content == "引き直し":
                    continue

                await thread.send(f"{users[0]}チーム２人目のスコアを入力してね。(5分以内)")
                #メッセージを受け取ったスレッドに対してのみ返す
                while True:
                    BattleRisult2 = await client.wait_for('message', check=check, timeout=300)
                    if thread.id == BattleRisult2.channel.id:
                        break
                    else:
                        pass
                    
                await asyncio.sleep(1)

                #team1のスコアをリストに追加
                team1.append(BattleRisult1.content)
                team1.append(BattleRisult2.content)

                #team2のスコアを集計
                await thread.send(f"{users[2]}チーム１人目のスコアを入力してね。(5分以内)")
                #メッセージを受け取ったスレッドに対してのみ返す
                while True:
                    BattleRisult3 = await client.wait_for('message', check=check, timeout=600)
                    if thread.id == BattleRisult3.channel.id:
                        break
                    else:
                        pass
                    
                await asyncio.sleep(1)

                await thread.send(f"{users[2]}チーム２人目のスコアを入力してね。(5分以内)")
                #メッセージを受け取ったスレッドに対してのみ返す
                while True:
                    BattleRisult4 = await client.wait_for('message', check=check, timeout=600)
                    if thread.id == BattleRisult4.channel.id:
                        break
                    else:
                        pass
                    
                await asyncio.sleep(1)

                #team2のスコアをリストに追加
                team2.append(BattleRisult3.content)
                team2.append(BattleRisult4.content)

                #どちらかが終了と入力したら終わる
                if BattleRisult1.content == "終了" or BattleRisult3.content == "終了":
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
                    await thread.send(f"対戦が終了ました。結果を集計します。")
                    await asyncio.sleep(3)
                    break

                await thread.send(f"{count}曲目お疲れ様でした！！ {count+1}曲目の選曲を行います。")
                await asyncio.sleep(3)
                
            return thread, team1, team2, users, music_ls
            
        #スレッド内でトラブルが起こったらスレッドを閉じる
        except Exception:
            await asyncio.sleep(1) #間を空ける
            await thread.send("タイムアウト、もしくはコマンド不備により対戦が終了されました。スレッドを削除します。")
            await asyncio.sleep(3) #スレッド削除まで待機
            await thread.delete()
            
    else:
        #例外処理に持っていく
        raise Exception("")
    
    
#スコア対決の計算
async def Score_Battle(user1, user2, name1, name2):

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
    
    
#EXスコア対決の計算
async def EX_Score_Battle(user1, user2, name1, name2):

    #対戦者名とスコアを取得
    user1_score = 0
    user2_score = 0
    total_P_pure1 = 0
    total_P_pure2 = 0
    for score1, score2 in zip(user1, user2):
        #EXスコアを計算(無印Pure:3点,Pure:2点,Far:1点,Lost:0点)
        #1Pプレイヤーのスコアを計算
        pure1, P_pure1, far1, lost1 = score1.split(' ')
        F_pure1 = int(pure1) - int(P_pure1)
        user1_score += int(P_pure1)*3 + int(F_pure1)*2 + int(far1)*1
        total_P_pure1 += int(P_pure1)
        
        #2Pプレイヤーのスコアを計算
        pure2, P_pure2, far2, lost2 = score2.split(' ')
        F_pure2 = int(pure2) - int(P_pure2)
        user2_score += int(P_pure2)*3 + int(F_pure2)*2 + int(far2)*1
        total_P_pure2 += int(P_pure1)

    if user1_score > user2_score:   #user1の勝利
        Drow_Flg = False
        return name1, name2, user1_score, user2_score, Drow_Flg
    elif user1_score < user2_score: #user2の勝利
        Drow_Flg = False
        return name2, name1, user1_score, user2_score, Drow_Flg
    else:                           #EXスコアが引き分けのときは内部精度勝負
        if total_P_pure1 > total_P_pure2:   #user1の勝利
            Drow_Flg = False
            return name1, name2, user1_score, user2_score, Drow_Flg
        elif total_P_pure1 < total_P_pure2: #user2の勝利
            Drow_Flg = False
            return name2, name1, user1_score, user2_score, Drow_Flg
        else:                               #それでも結果がつかなかった場合引き分け
            Drow_Flg = True
            return name1, name2, user1_score, user2_score, Drow_Flg

    
#戦績を確認
async def User_Status(client, message, file_path):
    #データを読み込んで加工しやすいように前処理
    BattleLog = pd.read_csv(file_path)
    BattleLog["Winner"] = BattleLog["Winner"].astype("Int64")
    BattleLog["Loser"] = BattleLog["Loser"].astype("Int64")
    wins = BattleLog[BattleLog["Winner"] == message.author.id]
    loses = BattleLog[BattleLog["Loser"] == message.author.id]
    userdata = pd.concat([wins, loses])

    #引き分け行に前処理を行う
    idx = 0
    for recode in userdata.itertuples():
        if recode.Drow_Flg == True:
            if recode.Winner == message.author.id:
                pass
            else:
                userdata.loc[idx, "Loser"] == userdata.loc[idx, "Winner"]
                userdata.loc[idx, "Winner"] == message.author.id

    #重複行を纏める
    margedata = userdata.drop_duplicates()
    #結果を保存するデータフレームを作成
    result = pd.DataFrame(columns=["User"])
    
    #対戦した相手をUserとしてデータフレームに登録していく
    for idx, recode in margedata.iterrows():
        if recode["Winner"] == message.author.id: #勝ってたとき
            if (result["User"] == recode["Loser"]).any():
                pass
            else:
                new_user = pd.DataFrame({"User":[recode["Loser"]]})
                result = pd.concat([result, new_user])
        elif recode.Loser == message.author.id: #負けてたとき
            if (result["User"] == recode["Winner"]).any():
                pass
            else:
                new_user = pd.DataFrame({"User":[recode["Winner"]]})
                result = pd.concat([result, new_user])


    #勝敗結果を記録するために列を追加、インデックスを追加
    result = result.assign(Win=0, Lose=0, Drow=0)
    result.index = range(len(result))

    #与えられたデータを上から流していく
    for _, recode in userdata.iterrows():
        if recode["Winner"] == message.author.id and recode["Drow_Flg"] == False: #入力者が勝者の場合
            idx = result.index[result["User"] == recode["Loser"]]
            result.loc[idx, "Win"] += 1 
        elif recode["Loser"] == message.author.id and recode["Drow_Flg"] == False: #入力者が敗者の場合
            idx = result.index[result["User"] == recode["Winner"]]
            result.loc[idx,"Lose"] += 1
        elif recode["Drow_Flg"] == True:
            if recode["Winner"] == message.author.id:
                idx = result.index[result["User"] == recode["Loser"]]
                result.loc[idx,"Drow"] += 1
            elif recode["Loser"] == message.author.id:
                idx = result.index[result["User"] == recode["Winner"]]
                result.loc[idx,"Drow"] += 1

    #名前を表示名に変更する
    for idx, recode in result.iterrows():
        result.loc[idx, "User"] = (await client.fetch_user(recode["User"])).display_name

    

    #集計が終了したデータを勝利→引き分け→敗北にソートして返す
    return result.sort_values(by=["Win", "Drow", "Lose"])


async def task_create():
    """今週の課題曲を指定"""
    music, level_str, dif = Random_Select_Level("9")
    
    msg = f"「{music}」{dif}:{level_str}" 
    #メッセージを作成
    embed = discord.Embed(title="今週の課題曲",description=msg)
    embed.add_field(name="今週の課題曲", value=msg, inline=False)
    
#現在使用していない機能
#ポテンシャル値の計算
def Potential_Score(music, score, difficult="FTR"):

    #楽曲情報をデータフレームに読み込む
    df_music = pd.read_csv("Arcaea_Music_Data.csv")

    #ptを算出したい曲のデータを取得
    pt_music = df_music[df_music["Music_Title"] == music]

    #登録されている略称(ニックネーム)でも可
    if pt_music["Music_Title"].empty == True:
        pt_music = df_music[df_music["Nickname"] == music]

    #曲の譜面定数情報を取得
    if difficult == "BYD" or difficult == "byd": #BYDの定数を取得
        pt_music_b = pt_music.dropna(subset=["BYD_Const"])
        const = float(pt_music_b["BYD_Const"].values)
        difficult = "BYD"                        #返信用に形式を統一

    else:                                        #FTRの定数を取得
        pt_music_f = pt_music.dropna(subset=["FTR_Const"])
        const = float(pt_music_f["FTR_Const"].values)

    #スコアの桁数を合わせる(994と入力したものを9,940,000に直す)
    while True:
        score_digit = len(str(score)) #現在の桁数を取得
        if score_digit == 7 or score_digit == 8:
            break
        score = score * 10

    #スコア区分を変数として作成
    PM = 10000000
    EX = 9800000
    AA = 9500000

    #楽曲のポテンシャル値を計算
    if score >= PM:
        potential = const + 2                       #譜面定数+2.0

    elif score >= EX:
        potential = const + 1 + (score - EX)/200000 #譜面定数+1.0+(スコア-9,800,000)/200,000

    else:
        potential = const + (score - AA)/300000     #譜面定数+(スコア-9,500,000)/300,000 (下限は0)

        #※ポテンシャル値は0以下にならない
        if potential <= 0:
            potential = 0

    return round(potential, 2), score, difficult #少数第３位を四捨五入して表示

#定数ランダム選曲
def Random_Select_Const(const1="0", const2="12.0"):
    
    #定数を決めていない時は全曲から選ぶ
    const1 = float(const1)
    const2 = float(const2)
    
    #楽曲情報をデータフレームに読み込む
    df_music = pd.read_csv("Arcaea_Music_Data.csv")
    
    #楽曲数を取得
    df_music = df_music[df_music["FTR_Const"] >= const1]
    df_music = df_music[df_music["FTR_Const"] <= const2]
    
    #乱数の範囲を取得
    music_num = len(df_music)

    rand = random.randint(0,music_num-1)

    #乱数から選ばれた楽曲を抽出
    hit_music = df_music.iloc[rand]

    #結果を保存
    music = hit_music["Music_Title"]
    level = hit_music["FTR_Level"]
    
    if level % 1 != 0.0:
        level_str = str(math.floor(level)) + "+"
    else:
        level_str = str(math.floor(level))

    return music, level_str