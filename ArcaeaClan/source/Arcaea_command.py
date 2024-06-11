import os
import json
import math
import dotenv
import random
import asyncio
import discord
import pandas as pd
from datetime import datetime, timedelta
import ui


async def Random_Select_Level(level1=None, level2=None):
    """ランダム選曲機能"""
    #ユーザー環境変数を読み込み
    dotenv.load_dotenv()

    #レベル指定があるか
    if level1 == None and level2 == None:
        level1, level2 = "0", "12" #全曲指定にする
    elif level1 != None and level2 == None:
        level2 = level1            #単一の難易度のみにする

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


    #楽曲情報をデータフレームに読み込む
    df_music = pd.read_csv(os.environ["MUSIC"])

    #楽曲数を取得
    df_music_FTR = df_music[df_music["FTR_Level"] >= level1].copy()
    df_music_FTR = df_music_FTR[df_music_FTR["FTR_Level"] <= level2]

    df_music_ETR = df_music[df_music["ETR_Level"] >= level1].copy()
    df_music_ETR = df_music_ETR[df_music_ETR["ETR_Level"] <= level2]

    df_music_BYD = df_music[df_music["BYD_Level"] >= level1].copy()
    df_music_BYD = df_music_BYD[df_music_BYD["BYD_Level"] <= level2]


    df_range_music = pd.concat([df_music_FTR, df_music_ETR, df_music_BYD])

    #乱数の範囲を取得
    music_num = len(df_range_music)

    #乱数を作成
    rand = random.randint(0,music_num-1)

    #乱数から選ばれた楽曲を抽出
    hit_music = df_range_music.iloc[rand]

    #結果を保存
    title = hit_music["Music_Title"] #曲名

    #難易度帯を検索して取得
    if pd.isnull(hit_music["BYD_Level"]) == True and pd.isnull(hit_music["ETR_Level"]) == True:
        level = hit_music["FTR_Level"]
        deffecult = "FTR" #難易度を表示
    elif pd.isnull(hit_music["BYD_Level"]) == True:
        level = hit_music["ETR_Level"]
        deffecult = "ETR" #難易度を表示
    else:
        level = hit_music["BYD_Level"]
        deffecult = "BYD" #難易度を表示

    #楽曲レベルを表示用に調整
    if level % 1 != 0.0:
        level_str = str(math.floor(level)) + "+"
    else:
        level_str = str(math.floor(level))

    #画像データを取得
    image = hit_music["Image"]

    return title, level_str, deffecult, image


async def match_host(ctx, user, kind):
    """対戦のホストを立てる"""
    #メンバーリストを取得
    MemberList = pd.read_csv(os.environ["MEMBERLIST"])
    #登録済みか確認
    if MemberList["Discord_ID"].isin([user]).any().any():
        pass
    else:
        return await ctx.response.send_message("メンバー登録が行われていません。\n先に /sign_up でメンバー登録を行ってください", ephemeral=True)
    
    #対戦中、対戦待機中でないか確認
    check = await state_check(user)
    if check:
        return await ctx.response.send_message(f"あなたは対戦中、もしくは対戦ホスト中です。", ephemeral=True)
        
    #対戦形式を読み込み
    with open(os.environ["VS_DICT"], mode="r") as f:
        vs_dict = json.load(f)
    #対戦募集ボタンを表示
    view = ui.VSHostButton(user, kind, timeout=120) #2分で募集を削除
    await ctx.response.send_message(f"{ctx.user.mention}:Create {vs_dict[kind]} Room", view=view)

    #対戦フラグをDataFrameに登録
    await state_chenge(user, True)


async def state_check(user):
    """対戦ステータスを確認する"""
    MemberList = pd.read_csv(os.environ["MEMBERLIST"])
    user_state = MemberList[MemberList["Discord_ID"] == user].copy()
    if user_state["State"].item():
        return True #対戦中
    else:
        return False #未対戦
        

async def state_chenge(user:int, state:bool):
    """対戦ステータスの変更"""
    MemberList = pd.read_csv(os.environ["MEMBERLIST"])
    MemberList.loc[MemberList[MemberList["Discord_ID"] == user].index, "State"] = state
    MemberList.to_csv(os.environ["MEMBERLIST"], index=False)


async def Arcaea_ScoreBattle(ctx, host_id, guest_id, battle_type):
    """スコアバトルを行う関数"""
    #対戦を始める
    try:
        #ゲスト側の対戦ステータスを変更
        await state_chenge(guest_id, True)
        #ユーザーを取得
        host_user = ctx.client.get_user(host_id)
        guest_user = ctx.client.get_user(guest_id)

        #対戦方式によって分岐
        b_type = int(battle_type)
        #1vs1対決
        if b_type == 0 or b_type == 1:
            try:
                #対決を実行
                thread, score1, score2, music_ls = await Singles_RandomScoreBattle(ctx, host_user, guest_user, b_type)
            #終了を選ばれた時のみ対戦を終わらせてスレッドを閉じる
            except TypeError:
                return await ctx.followup.send(f"対戦が途中で終了されました。お疲れ様でした。")

        #対戦方式によってスコア計算を分岐
        if b_type == 0: #通常スコア対決
            #得点を計算
            winner, loser, player1_score, player2_score = await Score_Battle(score1, score2, host_user, guest_user)
        elif b_type == 1: #EXスコア対決
            #得点を計算
            winner, loser, player1_score, player2_score, Drow_Flg = await EX_Score_Battle(score1, score2, host_user, guest_user)

        #勝負形式を取得
        if b_type == 0:
            vs_format = "ScoreBattle"
        else:
            vs_format = "EXScoreBattle"

        #名前を変数に
        host_name = host_user.display_name
        guest_name = guest_user.display_name

        #勝敗をスレッドに表示
        if player1_score == player2_score:
            await thread.send(f"結果は両者 {player1_score:,} で引き分けです!!お疲れ様でした")
            Drow_Flg = True
            #表示用のリザルトを作成
            result = f"[{vs_format}]\n"\
                     f"・1曲目 {music_ls[0]}\n{host_name}：{int(score1[0]):,}\n{guest_name}：{int(score2[0]):,}\n"\
                     f"・2曲目 {music_ls[1]}\n{host_name}：{int(score1[1]):,}\n{guest_name}：{int(score2[1]):,}\n"\
                     f"・Total\n{host_name}：{player1_score:,}\n{guest_name}：{player2_score:,}\n\n"\
                     f"Drow：{winner.display_name, loser.display_name}!!"

        else:
            await thread.send(f"{host_name}: {player1_score:,}\n{guest_name}: {player2_score:,}\n\n勝者は{winner.mention}さんでした!!お疲れ様でした!!")
            Drow_Flg = False
            #表示用のリザルトを作成
            result = f"[{vs_format}]\n"\
                     f"・1曲目 {music_ls[0]}\n{host_name}：{int(score1[0]):,}\n{guest_name}：{int(score2[0]):,}\n"\
                     f"・2曲目 {music_ls[1]}\n{host_name}：{int(score1[1]):,}\n{guest_name}：{int(score2[1]):,}\n"\
                     f"・Total\n{host_name}：{player1_score:,}\n{guest_name}：{player2_score:,}\n\n"\
                     f"Winner：{winner.display_name}!!"

        #csvファイルに保存
        if b_type == 0: #通常スコア
            log_path = os.environ["SCORE_LOG"]
        else:           #EXスコア
            log_path = os.environ["EXSCORE_LOG"]
        df_log = pd.read_csv(log_path)
        now_data = [[winner.id, loser.id, Drow_Flg]]
        df_now = pd.DataFrame(now_data, columns=["Winner", "Loser", "Drow_Flg"])
        df_log = pd.concat([df_log, df_now])
        df_log.to_csv(log_path, index=False)

        #ダブルス対決
        #elif batlle_sys == 2:
        #    try:
        #        #対戦を実行
        #        thread, team1, team2, users, music_ls =  await Doubles_RandomScoreBattle(client, message)
        #    #終了を選ばれた時のみ対戦を終わらせてスレッドを閉じる
        #    except TypeError:
        #        return await message.reply(f"対戦が途中で終了されました。お疲れ様でした。")
        #
        #    #スコアを計算
        #    winner, loser, team1_score, team2_score = await Score_Battle(team1, team2, users[0], users[2])
        #
        #    #メンションをUserIDに変換
        #    winner_id = int(winner[2:-1])
        #    loser_id = int(loser[2:-1])
        #    team1_user_name1 = f"{client.get_user(int((users[0])[2:-1])).display_name},{client.get_user(int((users[1])[2:-1])).display_name}"
        #    team2_user_name2 = f"{client.get_user(int((users[2])[2:-1])).display_name},{client.get_user(int((users[3])[2:-1])).display_name}"
        #    #勝者チームの2人を取得
        #    if winner == users[0]:
        #        winner1 = users[0]
        #        winner2 = users[1]
        #    else:
        #        winner1 = users[2]
        #        winner2 = users[3]
        #
        #    #勝敗をスレッドに表示
        #    if team1_score == team2_score:
        #        await thread.send(f"結果は両チーム{team1_score} で引き分け!!お疲れ様!!!")
        #        #表示用のリザルトを作成
        #        result = f"[ScoreBattle(Team)]\n"\
        #                 f"・1曲目 {music_ls[0]}\n"\
        #                 f"{team1_user_name1}チーム：{int(team1[0]) + int(team1[1])}\n"\
        #                 f"{team2_user_name2}チーム：{int(team2[0]) + int(team2[1])}\n"\
        #                 f"・2曲目 {music_ls[1]}\n"\
        #                 f"{team1_user_name1}チーム：{int(team1[2]) + int(team1[3])}\n"\
        #                 f"{team2_user_name2}チーム：{int(team2[2]) + int(team2[3])}\n"\
        #                 f"・Total\n{team1_user_name1}：{team1_score}\n"\
        #                 f"{team2_user_name2}：{team2_score}\n"\
        #                  "\n"\
        #                 f"Drow：{team1_user_name1}チーム {team2_user_name2}チーム!"
        #    else:
        #        await thread.send(f"{users[0]}チーム: {team1_score}\n{users[2]}チーム: {team2_score}\n\n勝者は{winner1}, {winner2}チーム!!おめでとう!!お疲れ様!!")
        #        #表示用のリザルトを作成
        #        result = f"[ScoreBattle(Team)]]\n"\
        #                 f"・1曲目 {music_ls[0]}\n"\
        #                 f"{team1_user_name1}チーム：{int(team1[0]) + int(team1[1])}\n"\
        #                 f"{team2_user_name2}チーム：{int(team2[0]) + int(team2[1])}\n"\
        #                 f"・2曲目 {music_ls[1]}\n"\
        #                 f"{team1_user_name1}チーム：{int(team1[2]) + int(team1[3])}\n"\
        #                 f"{team2_user_name2}チーム：{int(team2[2]) + int(team2[3])}\n"\
        #                 f"・Total\n{team1_user_name1}：{team1_score}\n"\
        #                 f"{team2_user_name2}：{team2_score}\n"\
        #                  "\n"\
        #                 f"Winner：{client.get_user(int(winner1[2:-1])).display_name},{client.get_user(int(winner2[2:-1])).display_name}チーム!!"

        #対戦結果をチャンネルに表示
        await ctx.followup.send(result)

        #対戦ステータスを変更
        await state_chenge(host_user.id, False)
        await state_chenge(guest_user.id, False)

        #30秒後スレッドを閉じる
        await asyncio.sleep(1) #間を空ける
        await thread.send(f"このスレッドは30秒後、自働的に削除されます。")
        await asyncio.sleep(30) #スレッド削除まで待機
        await thread.delete() #スレッドを削除

    #トラブルがおこった際に表示
    except Exception as error:
        print(type(error))
        print(error.args)
        await ctx.followup.send("タイムアウト、もしくはコマンド不備により対戦が終了されました。")
        #対戦ステータスを変更
        await state_chenge(host_user.id, False)
        await state_chenge(guest_user.id, False)


#1vs1で戦う時のフォーマット
async def Singles_RandomScoreBattle(ctx, host_user, guest_user, EX_flg):
    #勝負形式を取得
    if EX_flg == 1:
        vs_format = "EXScoreBattle"
    else:
        vs_format = "ScoreBattle"

    #対戦スレッドを作成
    thread = await ctx.channel.create_thread(name="{} vs {}：{}".format(host_user.display_name, guest_user.display_name, vs_format),type=discord.ChannelType.public_thread)

    #スレッド内でのエラーをキャッチ
    try:
        #リンクプレイコードのチェック
        def checkLinkID(m):
            try:
                ms = m.content
                if len(ms) == 6:
                    str(ms[0:4])
                    int(ms[4:6])
                    return True
            except Exception:
                return False

        #メッセージとボタンを作成
        an = f"Channel：{thread.mention} \n {host_user.display_name} vs {guest_user.display_name}"
        ms = f"Channel：{host_user.mention} vs {guest_user.mention} \n (途中終了する時はお互いに「終了」を押してね)"
        b_stop = ui.VSStopbutton(host_user.id, guest_user.id, timeout=None)

        #メッセージを送信して難易度選択を待機
        await ctx.response.send_message(an, delete_after=30)
        await thread.send(ms, view=b_stop)
        await thread.send(f"{host_user.mention}:Link Playのルームを作成して、ルームコードを入力してね")
        
        #メッセージを受け取ったスレッドに対してのみ返す
        while True:
            msg = await ctx.client.wait_for('message', check=checkLinkID, timeout=600)
            #同一スレッドかつホストの入力であるか確認
            if thread.id == msg.channel.id and host_user.id == msg.author.id:
                break
            else:
                pass

        await asyncio.sleep(0.5) #インターバル

        #課題曲難易度選択のボタンを表示
        view = ui.VSMusicDifChoice(host_user.id, guest_user.id, EX_flg, timeout=600)
        await thread.send("難易度を選択してね!お互いがOKを押したら次に進むよ",view=view)

    #スレッド内でトラブルが起こったらスレッドを閉じる
    except Exception:
        await asyncio.sleep(1) #間を空ける
        await thread.send("タイムアウトより対戦が終了されたよ。チャンネルを削除するね")
        await asyncio.sleep(3) #スレッド削除まで待機
        await thread.delete()
        #対戦ステータスを変更
        await state_chenge(host_user.id, False)
        await state_chenge(guest_user.id, False)
        

async def s_sb_selectlevel(ctx, host_user_id, guest_user_id, dif_ls, EX_flg):
    """レベル選択ボタンを表示"""
    view = ui.VSMusicLevelChoice(host_user_id, guest_user_id, dif_ls, EX_flg, timeout=600)
    await ctx.followup.send("レベルを選択してね!お互いがOKを押したら次に進むよ",view=view)


async def s_sb_musicselect(ctx, host_user_id, guest_user_id, dif_ls, level_ls, EX_flg, Score_Count=None):
    """楽曲表示と決定処理"""
    music, level_str, dif, image = await Random_Select_Level(dif=dif_ls, level_list=level_ls)
    #対戦開始前のメッセージを作成
    musicmsg = f"対戦曲:[{music}] {dif}:{level_str}!!"
    music = f"{music} {dif} {level_str}"
    #選択のボタンを表示
    view = ui.VSMusicButton(host_user_id, guest_user_id, dif_ls, level_ls, music, EX_flg, Score_Count, timeout=600)
    #課題曲を表示
    await ctx.channel.send(musicmsg, file=discord.File(image), view=view)
    await ctx.channel.send("お互いが選択したらゲームスタート!!")
    

async def s_sb_battle(ctx, host_user_id, guest_user_id, dif_ls, level_ls, music, EX_flg, Score_Count=None):
    """スコア受け取りから終了まで"""
    try:
        #初回の場合はインスタンス作成
        if Score_Count != None:
            pass
        else:
            Score_Count = ScoreManage()

        #チャンネル属性を取得
        channel = ctx.channel
        #ユーザー属性を取得
        host_user =  ctx.client.get_user(host_user_id)
        guest_user =  ctx.client.get_user(guest_user_id)

        #一人目
        result1 = s_sb_score_check(ctx=ctx, channel=channel, score_user=host_user, wait_user=guest_user, EX_flg=EX_flg)
        if result1 is None:
            #タイムアウト処理が行われたので終了
            return

        result2 = s_sb_score_check(ctx=ctx, channel=channel, score_user=guest_user, wait_user=host_user, EX_flg=EX_flg)
        if result2 is None:
            #タイムアウト処理が行われたので終了
            return
                            
        await asyncio.sleep(1) #インターバル

        #スコアをlistに保存
        Score_Count.score1.append(result1.content)
        Score_Count.score2.append(result2.content)

        #対戦曲数を数える
        Score_Count.count += 1

        #選択曲をレコード用に取得
        Score_Count.music_ls.append(music)

        #最終曲になったらループを抜ける
        if Score_Count.count == 2:
            await channel.send(f"対戦終了～～！！ 対戦結果は～～？")
            await asyncio.sleep(3)

            #スコア計算、結果表示関数
            await s_sb_result(ctx, channel, host_user, guest_user, Score_Count.score1, Score_Count.score2, Score_Count.music_ls, EX_flg)
        else:
            await channel.send(f"{Score_Count.count}曲目おつかれさま！！ {Score_Count.count+1}曲目はなにがでるかな～")
            await asyncio.sleep(3)
            #楽曲選択に移行
            await s_sb_musicselect(ctx, host_user_id, guest_user_id, dif_ls, level_ls, EX_flg, Score_Count)

    #スレッド内でトラブルが起こったらスレッドを閉じる
    except Exception as e:
        print(e)
        await asyncio.sleep(1) #間を空ける
        await channel.send("タイムアウトより対戦が終了されたよ。チャンネルを削除するね")
        await asyncio.sleep(3) #スレッド削除まで待機
        await channel.delete()
        #対戦ステータスを変更
        await state_chenge(host_user.id, False)
        await state_chenge(guest_user.id, False)


class ScoreManage():
    """対戦のスコアを一時保存するためのクラス"""
    def __init__(self):
        self.score1 = []
        self.score2 = []
        self.music_ls = []
        self.count = 0
        
        
async def s_sb_score_check(ctx, channel, score_user, wait_user, EX_flg):
    #スコア受け取り監視関数を定義
    def check(m):
        """通常スコア用チェック関数"""
        try:
            ms = m.content.split(' ')
            if len(ms) == 1:
                for i in ms:
                    int(i)
                return True
        except Exception:
            return False

    def checkEX(m):
        """EXスコア用チェック関数"""
        try:
            ms = m.content.split(' ')
            if len(ms) == 4:
                for i in ms:
                    int(i)
                return True
        except Exception:
            return False
    
    if EX_flg == False:
        #通常スコア
        result = await ctx.client.wait_for('message', check=check, timeout=600)
    else:
        #EXスコア
        result = await ctx.client.wait_for('message', check=checkEX, timeout=600)
        
    #メッセージを受け取ったスレッドであるか、メンションされたユーザーからであるかを確認
    if channel.id == result.channel.id and score_user.id == result.author.id:
        #スコア確認ボタンを表示
        view = ui.VSScoreCheck(score_user.id)
        if EX_flg == False:
            #通常スコア
            await channel.send(f"入力スコア「{int(result.content):,}」でOKかな？", view=view)
        else:
            ex_result = result.content.split(" ")
            await channel.send(f"入力スコア「Pure:{int(ex_result[0]):,}, 内部Pure:{int(ex_result[1]):,}, Far:{int(ex_result[2]):,}, Lost{int(ex_result[3]):,}」でOKかな？", view=view)
        stasrt_time = datetime.now()
        timeout = stasrt_time + timedelta(minutes=10)
        while True:
            #時刻を取得
            nowtime = datetime.now()
            #次に進む
            if view.check_flg is not None:
                break
            #終了する
            elif nowtime >= timeout:
                try:
                    #チャンネルを削除
                    await ctx.channel.delete()
                    #対戦ステータスを変更
                    await state_chenge(score_user.id, False)
                    await state_chenge(wait_user.id, False)
                    return #終わる
                except discord.errors.NotFound:
                    return #終わる
            else:
                await asyncio.sleep(1)

        if view.check_flg:
            #二人目に進む
            return result
        else:
            #やり直しを行う
            s_sb_score_check(ctx, channel, score_user, wait_user)
    else:
        #他ユーザーからの反応は無視して再度入力を待つ
        s_sb_score_check(ctx, channel, score_user, wait_user)


async def s_sb_result(ctx, channel, host_user, guest_user, score1, score2, music_ls, b_type):
        #対戦方式によってスコア計算を分岐
        if b_type == 0: #通常スコア対決
            #得点を計算
            winner, loser, player1_score, player2_score = await Score_Battle(score1, score2, host_user, guest_user)
        elif b_type == 1: #EXスコア対決
            #得点を計算
            winner, loser, player1_score, player2_score, Drow_Flg = await EX_Score_Battle(score1, score2, host_user, guest_user)

        #名前を変数に
        host_name = host_user.display_name
        guest_name = guest_user.display_name

        #勝敗をスレッドに表示
        if b_type == False:
            #通常スコアバトル
            vs_format = "ScoreBattle"
            if player1_score == player2_score:
                await channel.send(f"結果は両者 {player1_score:,} で引き分け!! 白熱した戦いだったね!")
                Drow_Flg = True
                #表示用のリザルトを作成
                result = f"[{vs_format}]\n"\
                         f"・1曲目 {music_ls[0]}\n{host_name}：{int(score1[0]):,}\n{guest_name}：{int(score2[0]):,}\n"\
                         f"・2曲目 {music_ls[1]}\n{host_name}：{int(score1[1]):,}\n{guest_name}：{int(score2[1]):,}\n"\
                         f"・Total\n{host_name}：{player1_score:,}\n{guest_name}：{player2_score:,}\n\n"\
                         f"Drow：{winner.display_name} {loser.display_name}!!"

            else:
                await channel.send(f"{host_name}: {player1_score:,}\n{guest_name}: {player2_score:,}\n\n勝者は{winner.mention}さん!!おめでとう!!🎉🎉")
                Drow_Flg = False
                #表示用のリザルトを作成
                result = f"[{vs_format}]\n"\
                         f"・1曲目 {music_ls[0]}\n{host_name}：{int(score1[0]):,}\n{guest_name}：{int(score2[0]):,}\n"\
                         f"・2曲目 {music_ls[1]}\n{host_name}：{int(score1[1]):,}\n{guest_name}：{int(score2[1]):,}\n"\
                         f"・Total\n{host_name}：{player1_score:,}\n{guest_name}：{player2_score:,}\n\n"\
                         f"Winner：{winner.display_name}!!"
                
        elif b_type == 1: #EXスコア対決
            #EXスコアバトル
            vs_format = "EXScoreBattle"
            if sum(player1_score) == sum(player2_score):
                await channel.send(f"結果は両者 {sum(player1_score):,} で引き分け!! 白熱した戦いだったね!")
                Drow_Flg = True
                #表示用のリザルトを作成
                result = f"[{vs_format}]\n"\
                         f"・1曲目 {music_ls[0]}\n{host_name}：{int(player1_score[0]):,}\n{guest_name}：{int(player2_score[0]):,}\n"\
                         f"・2曲目 {music_ls[1]}\n{host_name}：{int(player1_score[1]):,}\n{guest_name}：{int(player2_score[1]):,}\n"\
                         f"・Total\n{host_name}：{sum(player1_score):,}\n{guest_name}：{sum(player2_score):,}\n\n"\
                         f"{winner.display_name}さんvs{loser.display_name}さんは引き分けでした!!!"

            else:
                await channel.send(f"{host_name}: {sum(player1_score):,}\n{guest_name}: {sum(player2_score):,}\n\n勝者は{winner.mention}さん!!おめでとう!!🎉🎉")
                Drow_Flg = False
                #表示用のリザルトを作成
                result = f"[{vs_format}]\n"\
                         f"・1曲目 {music_ls[0]}\n{host_name}：{int(player1_score[0]):,}\n{guest_name}：{int(player2_score[0]):,}\n"\
                         f"・2曲目 {music_ls[1]}\n{host_name}：{int(player1_score[1]):,}\n{guest_name}：{int(player2_score[1]):,}\n"\
                         f"・Total\n{host_name}：{sum(player1_score):,}\n{guest_name}：{sum(player2_score):,}\n\n"\
                         f"勝者は{winner.display_name}さんでした!!!"


        #csvファイルに保存
        if b_type == False: #通常スコア
            log_path = os.environ["SCORE_LOG"]
        else:           #EXスコア
            log_path = os.environ["EXSCORE_LOG"]
        df_log = pd.read_csv(log_path)
        now_data = [[winner.id, loser.id, Drow_Flg]]
        df_now = pd.DataFrame(now_data, columns=["Winner", "Loser", "Drow_Flg"])
        df_log = pd.concat([df_log, df_now])
        df_log.to_csv(log_path, index=False)

        #対戦結果をチャンネルに表示
        result_ch = await ctx.client.fetch_channel(int(os.environ["B_RESULT_CH"]))
        await result_ch.send(result)

        #対戦ステータスを変更
        await state_chenge(host_user.id, False)
        await state_chenge(guest_user.id, False)

        #30秒後スレッドを閉じる
        await asyncio.sleep(1) #間を空ける
        await channel.send(f"このチャンネルは1分後に自動で削除されるよ\nおつかれさま～～!またね!!")
        await asyncio.sleep(60) #スレッド削除まで待機
        await channel.delete() #スレッドを削除


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
    user1_score_ls = []
    user2_score_ls = []

    for score1, score2 in zip(user1, user2):
        #EXスコアを計算(無印Pure:3点,Pure:2点,Far:1点,Lost:0点)
        #1Pプレイヤーのスコアを計算
        pure1, P_pure1, far1, lost1 = score1.split(' ')
        F_pure1 = int(pure1) - int(P_pure1)
        user1_score += int(P_pure1)*3 + int(F_pure1)*2 + int(far1)*1
        total_P_pure1 += int(P_pure1)
        user1_score_ls.append(int(P_pure1)*3 + int(F_pure1)*2 + int(far1)*1)

        #2Pプレイヤーのスコアを計算
        pure2, P_pure2, far2, lost2 = score2.split(' ')
        F_pure2 = int(pure2) - int(P_pure2)
        user2_score += int(P_pure2)*3 + int(F_pure2)*2 + int(far2)*1
        total_P_pure2 += int(P_pure1)
        user2_score_ls.append(int(P_pure2)*3 + int(F_pure2)*2 + int(far2)*1)

    if user1_score > user2_score:   #user1の勝利
        Drow_Flg = False
        return name1, name2, user1_score_ls, user2_score_ls, Drow_Flg
    elif user1_score < user2_score: #user2の勝利
        Drow_Flg = False
        return name2, name1, user1_score_ls, user2_score_ls, Drow_Flg
    else:                           #EXスコアが引き分けのときは内部精度勝負
        if total_P_pure1 > total_P_pure2:   #user1の勝利
            Drow_Flg = False
            return name1, name2, user1_score_ls, user2_score_ls, Drow_Flg
        elif total_P_pure1 < total_P_pure2: #user2の勝利
            Drow_Flg = False
            return name2, name1, user1_score_ls, user2_score_ls, Drow_Flg
        else:                               #それでも結果がつかなかった場合引き分け
            Drow_Flg = True
            return name1, name2, user1_score_ls, user2_score_ls, Drow_Flg


#戦績を確認
async def User_Status(ctx, user, file_path):
    #データを読み込んで加工しやすいように前処理
    BattleLog = pd.read_csv(file_path)
    BattleLog["Winner"] = BattleLog["Winner"].astype("Int64")
    BattleLog["Loser"] = BattleLog["Loser"].astype("Int64")
    wins = BattleLog[BattleLog["Winner"] == user]
    loses = BattleLog[BattleLog["Loser"] == user]
    userdata = pd.concat([wins, loses])

    #引き分け行に前処理を行う
    idx = 0
    for recode in userdata.itertuples():
        if recode.Drow_Flg == True:
            if recode.Winner == user:
                pass
            else:
                userdata.loc[idx, "Loser"] == userdata.loc[idx, "Winner"]
                userdata.loc[idx, "Winner"] == user

    #重複行を纏める
    margedata = userdata.drop_duplicates()
    #結果を保存するデータフレームを作成
    result = pd.DataFrame(columns=["User"])

    #対戦した相手をUserとしてデータフレームに登録していく
    for idx, recode in margedata.iterrows():
        if recode["Winner"] == user: #勝ってたとき
            if (result["User"] == recode["Loser"]).any():
                pass
            else:
                new_user = pd.DataFrame({"User":[recode["Loser"]]})
                result = pd.concat([result, new_user])
        elif recode.Loser == user: #負けてたとき
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
        if recode["Winner"] == user and recode["Drow_Flg"] == False: #入力者が勝者の場合
            idx = result.index[result["User"] == recode["Loser"]]
            result.loc[idx, "Win"] += 1 
        elif recode["Loser"] == user and recode["Drow_Flg"] == False: #入力者が敗者の場合
            idx = result.index[result["User"] == recode["Winner"]]
            result.loc[idx,"Lose"] += 1
        elif recode["Drow_Flg"] == True:
            if recode["Winner"] == user:
                idx = result.index[result["User"] == recode["Loser"]]
                result.loc[idx,"Drow"] += 1
            elif recode["Loser"] == user:
                idx = result.index[result["User"] == recode["Winner"]]
                result.loc[idx,"Drow"] += 1

    #名前を表示名に変更する
    for idx, recode in result.iterrows():
        result.loc[idx, "User"] = (await ctx.client.fetch_user(recode["User"])).display_name

    #集計が終了したデータを勝利→引き分け→敗北にソートして返す
    return result.sort_values(by=["Win", "Drow", "Lose"])


#作りかけの機能
#async def task_create():
#    """今週の課題曲を指定"""
#    music, level_str, dif = Random_Select_Level("9")
#
#    msg = f"「{music}」{dif}:{level_str}" 
#    #メッセージを作成
#    embed = discord.Embed(title="今週の課題曲",description=msg)
#    embed.add_field(name="今週の課題曲", value=msg, inline=False)