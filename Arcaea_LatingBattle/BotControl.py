import os
import json
import asyncio
import discord

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
    
#ID系統の設定
matchroom = 1153650397634891807
A_rate = 1000
B_rate = 1000


#メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    #DMでのみ反応させる
    if message.guild:
        return
    #本番用
    if message.content == "match":
        await message.channel.send("マッチングを開始します")
        await 
        async with message.channel.typing():
            while True:
                await asyncio.sleep(3)
                
                
    #流れ説明用
    if message.guild:
        return
    global A_rate
    global B_rate
    if message.content == "/r match":
        await message.channel.send("マッチングを開始します")
        await asyncio.sleep(1)
        await message.channel.send("マッチング中...")
        async with message.channel.typing():
            await asyncio.sleep(5)
        id = client.get_channel(matchroom)
        await id.send("[A]sv[B]の対戦を開始します")
        await id.send("[A]の勝利です　お疲れさまでした")
        A_rate += 30
        B_rate -= 20
        
    if message.content == "/r rate":
        await message.channel.send(f"現在のレートは{A_rate}です")
        id = client.get_channel(matchroom)
        await id.send(f"現在の順位\nAさん {A_rate}\nBさん {B_rate}")
        
        
        
        
        
    
#Botを起動
client.run(TOKEN)