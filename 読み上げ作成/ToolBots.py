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
    global read
    global voice_client
    global channel_id
    #メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    
    #音声チャンネルに接続して読み上げ開始
    if message.content == '/reading':
        read = Reading.VoiceBox()
        vc = message.author.voice.channel
        voice_client = await vc.connect()
        source = FFmpegPCMAudio(r"Voice\connectstart.wav")
        message.guild.voice_client.play(source)
        channel_id = message.channel.id
        
    if message.content == '/stop':
        vc = message.author.voice.channel
        await voice_client.disconnect()
        del read #接続インスタンスを破棄
    
    #読み上げインスタンスが起動しているか確認
    if message.channel.id == channel_id: 
        if message.content[0] == "/": #コマンドは読み上げない
            pass
        else:
            #テキストを読み上げる
            await read.ReadingText(message, voice_client)


#Botの起動とDiscordサーバーへの接続
client.run(token=token["TokenKey"])