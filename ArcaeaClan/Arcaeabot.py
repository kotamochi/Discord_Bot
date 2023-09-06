import json
import discord
import Arcaea_command

#自分のBotのアクセストークンを取得
with open("ArcaeabotKey.json") as file:
    token = json.load(file)

#自分のBotのアクセストークン
TOKEN = token["TokenKey"]

#接続に必要なオブジェクトを生成
client = discord.Client(intents=discord.Intents.all())

#起動時に動作する処理
@client.event
async def on_ready():
    #起動したらターミナルにログイン通知が表示される
    print('ログインしました')

#メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    #課題曲を作成する
    if message.content.startswith('/a rand'):
        #渡されたコマンドを分割
        comannd = message.content.split(' ')
        
        #譜面定数上下限を設定してる時
        if len(comannd) == 4:
            level_low = comannd[2]
            level_high = comannd[3]
            music, level_str = Arcaea_command.Random_Select_Level(level_low, level_high)
        
        #譜面定数の下限を設定している時
        elif len(comannd) == 3:
            level = comannd[2]
            music, level_str = Arcaea_command.Random_Select_Level(level)
        
        #譜面定数を設定していない時
        else:
            music, level_str = Arcaea_command.Random_Select_Level()
        
        #ランダムで決まった曲を返信
        await message.channel.send(f"課題曲:{music} FTR:{level_str}です!!")

client.run(TOKEN)