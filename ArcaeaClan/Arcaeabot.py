import os
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
        #1v1勝負
        if message.content.startswith('/a vs'):
            await Arcaea_command.Arcaea_ScoreBattle(client, message, 0) #対戦用関数を実行
        #EXスコア勝負
        elif message.content.startswith('/a ex'):
            await Arcaea_command.Arcaea_ScoreBattle(client, message, 1) #対戦用関数を実行      
        #ダブルス勝負
        elif message.content.startswith('/a 2vs2'):
            await Arcaea_command.Arcaea_ScoreBattle(client, message, 2) #対戦用関数を実行      

        #戦績を確認する
        if message.content == '/a log':
            #Score勝負の結果集計
            file_1vs1_log = "BattleLog.csv"
            battledata = await Arcaea_command.User_Status(client, message, file_1vs1_log)
            user = message.author #入力したユーザー名を取得

            #表示用に戦績を整形する
            result = ""
            for _, battle_recode in battledata.iterrows():
                result += f"**{battle_recode['User']} || W:{battle_recode['Win']}-{battle_recode['Lose']}:L (D:{battle_recode['Drow']})**\n"

            #埋め込みメッセージを作成
            embed = discord.Embed(title="ランダム1v1",description="ランダム1vs1の過去の戦績です")
            embed.set_author(name=f"{user.display_name}の戦績",icon_url=user.avatar.url)

            #戦績が一件もなかった時は該当なしにする
            if result == "": 
                embed.add_field(name="通常スコアバトル", value="該当なし", inline=False)
            else:
                embed.add_field(name="通常スコアバトル", value=result, inline=False)

            #EXScore勝負の結果集計
            file_EX1vs1_log = "BattleLog_EXScore.csv"
            battledata = await Arcaea_command.User_Status(client, message, file_EX1vs1_log)

            #表示用に戦績を整形する
            result = ""
            for _, battle_recode in battledata.iterrows():
                result += f"**{battle_recode['User']} || W:{battle_recode['Win']}-{battle_recode['Lose']}:L (D:{battle_recode['Drow']})**\n"

            #戦績が一件もなかった時は該当なしにする
            if result == "":
                embed.add_field(name="EXスコアバトル", value="該当なし", inline=False)
            else:
                #埋め込みメッセージを作成
                embed.add_field(name="EXスコアバトル", value=result, inline=False)

            #戦績を送信
            await message.reply(embed=embed)

        
    #戦績ファイルを出力する(開発者用)
    if message.content == '/battlelog' and message.author.id == Creater_ID:
        dm_channel = await message.author.create_dm()
        await dm_channel.send(file=discord.File('BattleLog.csv'))
        await dm_channel.send(file=discord.File('BattleLog_EXScore.csv'))


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