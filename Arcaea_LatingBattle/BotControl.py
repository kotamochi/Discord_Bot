import os
import csv
import json
import asyncio
import discord
import pandas as pd
import Config
import Arcaea_command
import Matching

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
    
#設定の読み込み
Setting = Config.setting()
observars = pd.read_csv(Setting.ObserverFile) #運営側のIDを取得

#メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    #レート戦を開始するコマンド
    if message.channel.id == Setting.MatchRoom and observars.isin([message.author.id]):
        if message.content == "/BattleStart":
            #グローバル変数とインスタンス作成
            global Battle
            Battle = Matching.BattleMatching(Setting)

            #対戦を開始する
            await Battle.BattleStart(message.channel)
            Setting.BattleFlg = True #対戦中のフラグを立てる

    #DMでのみ反応させる
    if message.guild == False and Setting.BattleFlg:
        #レート戦用コマンド
        if message.content == "/match":
            await message.channel.send("マッチングを開始します") #DMに送信
            user_id = message.author.id #idを取得
            
            #対戦待ちにリストに書き込み
            await Battle.JoinList(user_id)
            async with message.channel.typing():
                while True:
                    await asyncio.sleep(3)

                
                
    #流れ説明用
    if message.guild:
        return
    global A_rate
    global B_rate
    play1 = "<@502838276294705162>"
    play2 = "<@1141419953942175754>"
    if message.content == "/r match":
        await message.channel.send("マッチングを開始します")
        await asyncio.sleep(1)
        await message.channel.send("マッチング中...")
        async with message.channel.typing():
            await asyncio.sleep(5)
        id = client.get_channel(matchroom)
        #await id.send(f"{play1}vs{play2}の対戦を開始します")
        #ms = f"/a vs {play1} {play2}"
        #await Arcaea_command.Arcaea_ScoreBattle(client, ms, 0) #対戦用関数を実行
        A_rate += 30
        B_rate -= 20
        
    if message.content == "/r rate":
        await message.channel.send(f"現在のレートは{A_rate}です")
        id = client.get_channel(matchroom)
        await id.send(f"現在の順位\nAさん {A_rate}\nBさん {B_rate}")
        
        
        
        
        
    
#Botを起動
client.run(TOKEN)