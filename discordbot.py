#インストールした discord.py を読み込む
import discord

#自分のBotのアクセストークンに置き換えてください
TOKEN = 'MTE0MzE3OTg4ODk4NDA2NDEzMA.G9Ukc5.JqEsDBOuEQgevpfVqqn1hACnwzeH_-wMP3mXtg'

#接続に必要なオブジェクトを生成
client = discord.Client(intents=discord.Intents.all())

#起動時に動作する処理
@client.event
async def on_ready():
    #起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# 返信する非同期関数を定義 
async def reply(message):
    reply = f'{message.author.mention} にゃー！' # 返信メッセージの作成
    await message.channel.send(reply) # 返信メッセージを送信

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
        await message.channel.send("マリオです", file=discord.File(r"C:\Users\kotam\OneDrive\画像\mario.png"))
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
    #話しかけられたかの判定
    if client.user in message.mentions:
        await reply(message)
        
    #対戦を行うコマンド
    if message.content.startswith('/vs'):
        comannd, user1, user2 = message.content.split(' ')
        await message.channel.send(f"{user1}と{user2}の対戦を開始します")
        
@client.event
async def on_reaction_add(reaction, user):
    #拍手のリアクションに対して、ぱちぱちを返す
    if str(reaction.emoji) == '👏':
        await reaction.message.channel.send('ぱちぱち')

@client.event
async def on_reaction_remove(reaction, user):
    #拍手のリアクションに対して、ぱちぱちを返す
    if str(reaction.emoji) == '👏':
        await reaction.message.channel.send('しゅん...')
#Botの起動とDiscordサーバーへの接続
client.run(TOKEN)