import os
import json
import discord
import Arcaea_command

#自分のBotのアクセストークンを取得
with open("..\Discord_APIToken.json") as file:
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

#ID系統の設定
MemberRole_ID = 1149393993159942214
RandomSelect_CH = 1148058499520135198
RandomBattle_CH = 1154008770737864714
Creater_ID = 502838276294705162 #私のユーザーID
Creater_RoomID = 1153650397634891807 #開発用チャンネルID

#サーバー入室時にロールを付与する
@client.event
async def on_member_join(member):
    # 用意したIDから Role オブジェクトを取得
    role = member.guild.get_role(MemberRole_ID)

    # 入ってきた Member に役職を付与
    await member.add_roles(role)

#メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    #ランダム選曲チャンネル以外では反応しない
    if message.channel.id == RandomSelect_CH:
        #課題曲を作成する
        if message.content.startswith('/a rand'):
            try:
                #渡されたコマンドを分割
                comannd = message.content.split(' ')

                #譜面定数上下限を設定してる時
                if len(comannd) == 4:
                    level_low = comannd[2]
                    level_high = comannd[3]
                    music, level_str, dif  = Arcaea_command.Random_Select_Level(level_low, level_high)

                #譜面定数の下限を設定している時
                elif len(comannd) == 3:
                    level = comannd[2]
                    music, level_str, dif  = Arcaea_command.Random_Select_Level(level)

                #譜面定数を設定していない時
                elif message.content == "/a rand":
                    music, level_str, dif = Arcaea_command.Random_Select_Level()

                #ランダムで決まった曲を返信
                await message.channel.send(f"課題曲:{music} {dif}:{level_str}です!!")
            except Exception:
                await message.channel.send("コマンドが間違ってるかも。もう一度試してみて!")

    #ランダム1v1チャンネル以外では反応しない
    if message.channel.id == RandomBattle_CH or message.channel.id == Creater_RoomID:
        #1v1勝負をする
        if message.content.startswith('/a vs'):
            try:
                await Arcaea_command.Arcaea_RandomScoreBattle(client, message) #対戦用関数を実行      
            except Exception:
                await message.channel.send("タイムアウト、もしくはコマンド不備により対戦が終了されました。") #トラブルがおこった際に表示

        #ダブルス勝負をする
        if message.content.startswith('/a 2vs2'):
            try:
                await Arcaea_command.Arcaea_DoublesScoreBattle(client, message) #対戦用関数を実行      
            except Exception:
                await message.channel.send("タイムアウト、もしくはコマンド不備により対戦が終了されました。") #トラブルがおこった際に表示

        #EXスコア勝負
        if message.content.startswith('/a ex'):
            try:
                await Arcaea_command.Arcaea_RandomScoreBattle(client, message) #対戦用関数を実行      
            except Exception:
                await message.channel.send("タイムアウト、もしくはコマンド不備により対戦が終了されました。") #トラブルがおこった際に表示

        #戦績を確認する
        if message.content == '/a log':
            await Arcaea_command.User_Status(message)
        
    #戦績ファイルを出力する(開発者用)
    if message.content == '/battlelog' and message.author.id == Creater_ID:
        dm_channel = await message.author.create_dm()
        await dm_channel.send(file=discord.File('BattleLog.csv'))

    #ポテンシャル計算機(身内用)
    if message.channel.id == 1071411461508841593:
        #ポテンシャルを計算する
        if message.content.startswith('/a pt'):
            comannd = message.content.split(' ')
            music_ls = []
            try:
                score = int(comannd[-1])
                byd_flg = "FTR"
                for i in range(len(comannd)-3):
                    music_ls.append(comannd[i+2])

            except ValueError:
                score = int(comannd[-2])
                byd_flg = comannd[-1]

                for i in range(len(comannd)-4):
                    music_ls.append(comannd[i+2])

            #listから曲名を作成
            music = " ".join(music_ls)

            #ポテ計算を実行
            potential, score_r, difficult = Arcaea_command.Potential_Score(music, score, byd_flg)

            #返信文を作成
            reply = f"Music:{music} ({difficult})\nScore:{score_r}\nPt:{potential}"

            #メンションをつけて返信
            await message.reply(reply)

try:
    client.run(TOKEN)
except discord.errors.HTTPException:
    os.system('kill 1')
    os.system("python restarter.py")