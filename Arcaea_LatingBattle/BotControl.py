import os
import csv
import json
import asyncio
import discord
import pandas as pd
import Config
import Matching
import RatingBattle
import TornamentCommand

#自分のBotのアクセストークンを取得
with open("BotToken\ToolBotKey.json") as file:
    token = json.load(file)

#自分のBotのアクセストークン
TOKEN = token["TokenKey"]

#接続に必要なオブジェクトを生成
client = discord.Client(intents=discord.Intents.all())

#起動時に動作する処理
@client.event
async def on_ready():
    #起動したらターミナルにログイン通知が表示される
    print("ログイン完了")
    #いくつかのコマンドを含むインスタンスを作成
    global cmd
    cmd = TornamentCommand.Command(Setting, client)
    
#設定の読み込み
Setting = Config.setting()
observars = pd.read_csv(Setting.ObserverFile) #運営側のIDを取得

#メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    #レート戦を開始するコマンド
    if message.channel.id == Setting.MatchRoom and message.author.id == Setting.MasterID:
        if message.content == "/BattleStart":
            #対戦、マッチメイキング処理のインスタンス作成
            global Match
            Match = Matching.BattleMatching(Setting, client, cmd)
            global Battle
            Battle = RatingBattle.BattleManager(Setting, client)

            #対戦を開始する
            Setting.BattleFlg = True #対戦中のフラグを立てる
            await Match.BattleStart()
            
        #最終結果の表示コマンド 
        if message.content == "/Result":
            await cmd.ShowResult()


    #bot自身のメッセージへの反応
    if message.author.id == Setting.BotID:
        #マッチが成立したことをbotに知らせるメッセージを受け取る
        if message.channel.id == Setting.BotRoom and message.content.startswith("~MatchAnnounce~"):
            #対戦を起動
            await Battle.RatingBattle(message) #対戦用関数を実行
        
        #手動でマッチを行ったときの場合
        if message.channel.id == Setting.BotRoom and message.content.startswith("/SelfMatch"):
            comannd = message.content.split(" ")
            message = await message.edit(content=f"/SelfMatch playerID {(comannd[1])[2:-1]} {(comannd[2])[2:-1]}")
            #対戦を起動
            await Battle.RatingBattle(message) #対戦用関数を実行
            
        #関数を抜ける
        return
    
    
    #運営のみが管理するコマンド
    if message.channel.id == Setting.MatchRoom and observars.isin([message.author.id]).any().any():
        #手動でマッチメイキングを行う
        if message.content.startswith("/SelfMatch"):
            BotRoom = client.get_channel(Setting.BotRoom)
            await BotRoom.send(message.content) #受け取ったメッセージをそのままbotに投げる
            
    
    #対戦以外のコマンドの受付
    if message.channel.id == Setting.CommandRoom:
        #ユーザーリストに登録
        if message.content.startswith("/join"):
            await cmd.Join_UserList(message)
            
    
    #対戦期間中、DMでのみ反応する
    if message.guild == None and Setting.BattleFlg == True:
        #レート戦用コマンド
        if message.content == "/match":
            await message.channel.send("マッチングを開始します") #DMに送信
            user_id = message.author.id #idを取得
            
            #対戦待ちにリストに書き込み
            error_flg, error_content = await Match.JoinList(user_id)
            if error_flg: #エラーがあった場合、エラー内容を送信して終了
                return await message.channel.send(error_content)
            
            #マッチするまで待機する
            async with message.channel.typing(): #マッチング待機中は入力中にする
                while True:
                    match_flg = await Match.MatchCheck(user_id) #マッチングが成立しているか確認
                    if match_flg:
                        return await message.channel.send("マッチングが成立しました。対戦を開始します。") #成立したので終了する
                    else:
                        await asyncio.sleep(3) #成立しなかったら3秒待って再度確認へ

        #現在のレートを表示
        if message.content == "/rate":
            await cmd.NowRating(message.channel, message.author.id)

#Botを起動
client.run(TOKEN)