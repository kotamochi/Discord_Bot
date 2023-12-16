import discord
import json
import Chunithm_RandomSelect
import pandas as pd

#自分のBotのアクセストークンを取得
with open(r"原神部/Discord_APIToken.json") as file:
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

#メッセージ受信時に返信を返す処理
#async def reply(message):
#    reply = f'{message.author.mention} にゃー！' # 返信メッセージの作成
#    await message.channel.send(reply) # 返信メッセージを送信

#メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    #メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    #「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')
    if message.content == '/inu':
        await message.channel.send('わおーん')    
    if message.content == '/arcaea':
        await message.channel.send("https://arcaea.lowiro.com/ja")
    if message.content == '/mario':
        a = pd.read_csv(r"原神部/image.csv")
        b = a.loc[0,"画像データ"]
        c = str(a['画像データ'].values)
        await message.channel.send("マリオです", file=discord.File(b))
    if message.content == '/原神部':
        await message.channel.send("原神部集大成", file=discord.File(r"C:\Users\kotam\OneDrive\画像\genshinbu.jpg"))
    if message.content == '/kirby':
        await message.channel.send("カービィ", file=discord.File(r"C:\Users\kotam\OneDrive\画像\kirby.jpg"))
    if message.content == '/りーま':
        await message.channel.send("りーまくん", file=discord.File(r"C:\Users\kotam\OneDrive\画像\ri-ma.jpg"))
    if message.content == '/実写りくす':
        await message.channel.send("ゲーセンに現れたりくす", file=discord.File(r"C:\Users\kotam\OneDrive\画像\rikusu_real.jpg"))
    if message.content == '/りくすピース':
        await message.channel.send("ス〇イピースりくす", file=discord.File(r"C:\Users\kotam\OneDrive\画像\oishi-yami-.jpg"))
    if message.content == 'こゃーん':
        await message.channel.send("こねこねこ")
    ##話しかけられたかの判定
    #if client.user in message.mentions:
    #    await reply(message)
        
    #対戦を行うコマンド
    if message.content.startswith('/vs'):
        comannd, user1, user2 = message.content.split(' ')
        await message.channel.send(f"{user1}と{user2}の対戦を開始します")
        
    #チームコースを作成する
    if message.content.startswith('/チームコース'):
        #渡されたコマンドを分割
        comannd = message.content.split(' ')
        
        #譜面定数上下限を設定してる時
        if len(comannd) == 3:
            const1 = comannd[1]
            const2 = comannd[2]
            result = Chunithm_RandomSelect.Music_Select(const1, const2)
        
        #譜面定数の下限を設定している時
        elif len(comannd) == 2:
            const1 = comannd[1]
            result = Chunithm_RandomSelect.Music_Select(const1)
        
        #譜面定数を設定していない時
        else:
            result = Chunithm_RandomSelect.Music_Select()
        
        #結果を表示
        await message.channel.send(f"今回の課題曲は\n{result[0]}\n{result[1]}\n{result[2]}\nの三曲です!!")
        
    if message.content.startswith('/対戦'):
        #スレッドを作成
        thread = await message.channel.create_thread(name="Test")
        #await Arcaea_command.Arcaea_RandomScoreBattle(client, message)
        
        #セッションを管理
        with open("session.json", "r") as file:
            session_dic = json.load(file)
            session_num = len(session_dic)
        #スレッドidを取得して、現在実行中のスレッドを管理する
        session = thread.id
        session_dic[int(user1[2:-1])] = session
        session_dic[int(user2[2:-1])] = session
        await Chunithm_RandomSelect.test(client, message, thread)


#Botの起動とDiscordサーバーへの接続
client.run(token=token["TokenKey"])