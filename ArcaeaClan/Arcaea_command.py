import csv
import math
import random
import asyncio
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
        
    #レベル指定がない時は全曲から選ぶ
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

#1v1ランダムスコアバトルを行う関数
async def Arcaea_RandomScoreBattle(client, message):

    #シングルス対決を実行
    try:
        player1, player2, users = await Singles_RandomScoreBattle(client, message)
    except TypeError:
        return
    
    #得点を計算
    winner, loser, player1_score, player2_score = await Score_Battle(player1, player2, users[0], users[1])

    #勝敗を表示
    if player1_score == player2_score:
        await message.channel.send(f"結果は両者{player1_score} で引き分けです!!お疲れ様でした")
        Drow_Flg = True
    else:
        await message.channel.send(f"{users[0]}: {player1_score}\n{users[1]}: {player2_score}\n\n勝者は{winner}さんでした!!お疲れ様でした!!")
        Drow_Flg = False

    #csvファイルに保存
    df_log = pd.read_csv("BattleLog.csv")
    now_data = [[winner, loser, Drow_Flg]]
    df_now = pd.DataFrame(now_data, columns=["Winner", "Loser", "Drow_Flg"])
    df_log = pd.concat([df_log, df_now])
    df_log.to_csv("BattleLog.csv", index=False)

#ダブルススコアバトルを行う関数
async def Arcaea_DoublesScoreBattle(client, message):
    #渡されたコマンドを分割
    comannd = message.content.split(' ')
    users = [comannd[2], comannd[3], comannd[4], comannd[5]]

    if len(users) == 4:

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
                    
        await message.channel.send(f"{users[0]}, {users[1]}チームと{users[2]}, {users[3]}チームの対戦を開始するよ!!\n120秒以内に難易度を選択してね!!(全曲の場合は「all」と入力してください)")

        msg = await client.wait_for('message', check=checkLv, timeout=120)

        #渡されたコマンドを分割
        select_difficult = msg.content.split(' ')

        team1, team2 = [], []

        N_music = 2 #対戦曲数を指定(基本的に2)
        count = 0 #何曲目かをカウントする

        while True:
            #譜面定数上下限を設定してる時
            #譜面定数を設定していない時
            if select_difficult[0] == "ALL" or select_difficult[0] == "all":
                music, level_str, dif = Random_Select_Level()

            elif len(select_difficult) == 2:
                level_low = select_difficult[0]
                level_high = select_difficult[1]
                music, level_str, dif = Random_Select_Level(level_low, level_high)

            #譜面定数の下限を設定している時
            elif len(select_difficult) == 1:
                level = select_difficult[0]
                music, level_str, dif = Random_Select_Level(level)

            #対戦開始前のメッセージを作成
            startmsg = f"対戦曲は[{music}] {dif}:{level_str}です!!\n\n10分以内に楽曲を終了してスコアを入力してね。\n例:9950231\n(対戦を途中終了する時は、チームの１人目が「終了」と入力してください)"
            await asyncio.sleep(1)
            await message.channel.send(startmsg)
            await asyncio.sleep(1)

            #スコア報告チェック関数
            def check(m):
                try:
                    int(m.content)
                    return True
                except Exception:
                    if m.content == "終了" or m.content == "引き直し": #終了か引き直しと入力した場合のみok
                        return True
                    return False
            
            #team1のスコアを集計
            await message.channel.send(f"{users[0]}チーム１人目のスコアを入力してね。\n楽曲を再選択する場合は「引き直し」と入力してください")
            BattleRisult1 = await client.wait_for('message', check=check, timeout=600)
            await asyncio.sleep(0.5)
            
            #引き直しが選択されたら選曲まで戻る
            if BattleRisult1.content == "引き直し":
                continue

            await message.channel.send(f"{users[0]}チーム２人目のスコアを入力してね。(5分以内)")
            BattleRisult2 = await client.wait_for('message', check=check, timeout=300)
            await asyncio.sleep(1)

            team1.append(BattleRisult1.content)
            team1.append(BattleRisult2.content)

            #team2のスコアを集計
            await message.channel.send(f"{users[2]}チーム１人目のスコアを入力してね。(5分以内)")
            BattleRisult3 = await client.wait_for('message', check=check, timeout=300)
            await asyncio.sleep(0.5)

            await message.channel.send(f"{users[2]}チーム２人目のスコアを入力してね。(5分以内)")
            BattleRisult4 = await client.wait_for('message', check=check, timeout=300)
            await asyncio.sleep(1)

            team2.append(BattleRisult3.content)
            team2.append(BattleRisult4.content)

            #どちらかが終了と入力したら終わる
            if BattleRisult1.content == "終了" or BattleRisult3.content == "終了":
                await message.channel.send(f"対戦が途中で終了されたよ。お疲れ様!!")
            
                await asyncio.sleep(2)
            
            #対戦曲数を数える
            count += 1
                        
            #最終曲になったらループを抜ける
            if count == N_music:
                await message.channel.send(f"対戦が終了したよ。結果を集計するね。")
                await asyncio.sleep(3)
                break

            await message.channel.send(f"{count}曲目お疲れ様！！ {count+1}曲目の選曲を始めるよ。")
            await asyncio.sleep(2)

        winner, loser, team1_score, team2_score = await Score_Battle(team1, team2, users[0], users[2])

        #表示用に勝者を取得
        if winner == users[0]:
            winner1 = users[0]
            winner2 = users[1]
        else:
            winner1 = users[2]
            winner2 = users[3]

        #結果を出力
        if team1_score == team2_score:
            await message.channel.send(f"結果は両チーム{team1_score} で引き分け!!お疲れ様!!!")
        else:
            await message.channel.send(f"{users[0]}チーム: {team1_score}\n{users[2]}チーム: {team2_score}\n\n勝者は{winner1}, {winner2}チーム!!おめでとう!!お疲れ様!!")


#EXスコア対決
async def Arcaea_EXScoreBattle(client, message):
    player1, player2, users = await Singles_RandomScoreBattle(client, message, EX_flg=True)
    
    #得点を計算
    try:
        winner, loser, player1_score, player2_score, Drow_Flg = await EX_Score_Battle(player1, player2, users[0], users[1])
    except TypeError:
        return
    #勝敗を表示
    if Drow_Flg == True:
        await message.channel.send(f"結果は両者{player1_score} で引き分けです!!お疲れ様でした")
    else:
        await message.channel.send(f"{users[0]}: {player1_score}\n{users[1]}: {player2_score}\n\n勝者は{winner}さんでした!!お疲れ様でした!!")
    

#1vs1で戦う時のフォーマット
async def Singles_RandomScoreBattle(client, message, EX_flg=False):
    #渡されたコマンドを分割
    comannd = message.content.split(' ')
    users = [comannd[2], comannd[3]]

    if len(users) == 2 and users[0] != users[1]:

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
            reply = f"{users[0]}と{users[1]}のEXスコア対戦を開始します\n120秒以内に難易度を選択して下さい(全曲の場合は「all」と入力してください)"
        else:    
            reply = f"{users[0]}と{users[1]}のスコア対戦を開始します\n120秒以内に難易度を選択して下さい(全曲の場合は「all」と入力してください)"
            
        #メッセージを送信して難易度選択を待機
        await message.reply(reply)
        msg = await client.wait_for('message', check=checkLv, timeout=120)

        #渡されたコマンドを分割
        select_difficult = msg.content.split(' ')

        player1, player2 = [], []

        N_music = 2 #対戦曲数を指定(基本的に2)
        count = 0 #何曲目かをカウントする

        while True:
            #譜面定数上下限を設定してる時
            #譜面定数を設定していない時
            if select_difficult[0] == "ALL" or select_difficult[0] == "all":
                music, level_str, dif = Random_Select_Level()

            elif len(select_difficult) == 2:
                level_low = select_difficult[0]
                level_high = select_difficult[1]
                music, level_str, dif = Random_Select_Level(level_low, level_high)

            #譜面定数の下限を設定している時
            elif len(select_difficult) == 1:
                level = select_difficult[0]
                music, level_str, dif = Random_Select_Level(level)

            #対戦開始前のメッセージを作成
            if EX_flg == True: 
                startmsg = f"対戦曲は[{music}] {dif}:{level_str}です!!\n\n10分以内に楽曲を終了し、EXスコアを入力してください。\n例:1430 1392 13 7 (pure数,内部pure数,far数,lost数)\n(対戦を途中終了する場合はどちらかが「終了」と入力してください)"
            else:
                startmsg = f"対戦曲は[{music}] {dif}:{level_str}です!!\n\n10分以内に楽曲を終了し、スコアを入力してください。\n例:9950231\n(対戦を途中終了する場合はどちらかが「終了」と入力してください)"
            await asyncio.sleep(1)
            await message.channel.send(startmsg)
            await asyncio.sleep(0.5)

            def check(m):
                try:
                    ms = m.content.split(' ')
                    for i in ms:
                        int(i)
                    return True
                except Exception:
                    if m.content == "終了" or m.content == "引き直し": #終了か引き直しと入力した場合のみok
                        return True
                    return False
                    
            await message.channel.send(f"{users[0]}さんのスコアを入力してください。\n楽曲を再選択する場合は「引き直し」と入力してください")
            BattleRisult1 = await client.wait_for('message', check=check, timeout=600)
            await asyncio.sleep(0.5)
            
            #引き直しが選択されたら選曲まで戻る
            if BattleRisult1.content == "引き直し":
                continue

            await message.channel.send(f"{users[1]}さんのスコアを入力してください。")
            BattleRisult2 = await client.wait_for('message', check=check, timeout=120)
            await asyncio.sleep(1)

            player1.append(BattleRisult1.content)
            player2.append(BattleRisult2.content)

            #どちらかが終了と入力したら終わる
            if BattleRisult1.content == "終了" or BattleRisult2.content == "終了":
                return await message.channel.send(f"対戦が途中で終了されました。お疲れ様でした。")
            
            #対戦曲数を数える
            count += 1
                        
            #最終曲になったらループを抜ける
            if count == N_music:
                await message.channel.send(f"対戦が終了しました。結果を集計します。")
                await asyncio.sleep(3)
                break

            await message.channel.send(f"{count}曲目お疲れ様でした！！ {count+1}曲目の選曲を行います。")
            await asyncio.sleep(3)
            
        return player1, player2, users


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
async def User_Status(message):
    BattleLog = pd.read_csv("BattleLog.csv")
    
    userwins = BattleLog[BattleLog["Winner"] == message.author.id and BattleLog["Drow"] == False]
    userloses = BattleLog[BattleLog["Loser"] == message.author.id and BattleLog["Drow"] == False]
    userdrow = BattleLog[(BattleLog["Winner"] == message.author.id or BattleLog["Loser"] == message.author.id) and BattleLog["Drow"] == True]
    
    userdata = pd.concat([userwins, userloses])
    
    for _, data in userdata.iterrows():
        #勝者と敗者のメンションIDを取得
        winner = data["Winner"]
        loser = data["Loser"]

        if data["Drow_Flg"] == True:
            pass
        elif int(winner[2:-1]) == message.author.id:
            wins += 1
        elif int(loser[2:-1]) == message.author.id:
            loses += 1
    await message.channel.send(f"戦績:win {wins}-{loses} lose")
    
def count(data):
    #重複行を纏める
    margedata = data.groupby().copy()
    
    for _, recode in data.iterrows():
        print(0)
            
        

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