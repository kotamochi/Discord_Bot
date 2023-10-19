import discord
import json
import Reading
from discord.channel import VoiceChannel
from discord.player import FFmpegPCMAudio

#自分のBotのアクセストークンを取得
with open("Discord_APIToken.json") as file:
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
    
#メッセージに対して反応する
@client.event
async def on_message(message):
    #メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    #「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/reading':
        read = Reading.VoiceBox()
        vc = message.author.voice.channel
        await vc.connect()
        source = FFmpegPCMAudio(r"Voice\connectstart.wav")
        message.guild.voice_client.play(source)
        
    if message.content == '/stop':
        vc = message.author.voice.channel
        await vc.disconnect()
    
    #読み上げインスタンスが起動している時
    if read:
        #テキストを読み上げる
        await read.ReadingText(message.content)
    else:
        pass

#Botの起動とDiscordサーバーへの接続
client.run(token=token["TokenKey"])