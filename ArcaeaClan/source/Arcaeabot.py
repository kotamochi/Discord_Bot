import os
import dotenv
import datetime
import pandas as pd
import discord
from discord.ext import tasks
from discord import app_commands
import ui
import Arcaea_command


#ユーザー登録変数の読み込み
dotenv.load_dotenv()
#アクセストークンを取得
TOKEN = os.environ["DEBUG_BOT_TOKEN"]
#接続に必要なオブジェクトを生成
client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    """初回起動設定"""
    #各種IDを取得
    global Creater_DM, Creater_ID, MemberRole_ID, RandomSelect_CH, RandomBattle_CH, Create_RoomID
    Creater_ID = int(os.environ["CREATER_ID"])
    MemberRole_ID = int(os.environ["MEMBERROLE_ID"])
    RandomSelect_CH = int(os.environ["MUSIC_CH"])
    RandomBattle_CH = int(os.environ["BATTLE_CH"])
    Create_RoomID = int(os.environ["CREATER_ROOM_ID"])
    #管理者のDMオブジェクトを作成
    Creater = await client.fetch_user(Creater_ID)
    Creater_DM = await Creater.create_dm()

    #コマンドの更新
    await tree.sync()
    #viwe = await tree.fetch_commands() #登録されてるコマンドを表示するやつ
    #print(viwe)

    #ログイン通知
    await Creater_DM.send("起動したよ")
    #起動確認処理実行
    await chack_online.start()


@tasks.loop(seconds=60) #60秒ごとに実行
async def chack_online():
    """毎日定刻に起動チェックを行う"""
    #時刻確認

    now = datetime.datetime.now()
    oncheaktime =now.strftime('%H:%M')
    musictasktime = now.strftime('%A %H:%M')

    if oncheaktime == '09:00':
        #管理者DMに起動チェックと対戦Logを送信
        await Creater_DM.send("起動してるよ")
        await Creater_DM.send(file=discord.File('BattleLog.csv'))
        await Creater_DM.send(file=discord.File('BattleLog_EXScore.csv'))


@client.event
async def on_member_join(member):
    """サーバー参加時にロール付与"""
    #Roleオブジェクトを取得
    role = member.guild.get_role(MemberRole_ID)
    #入ってきたMemberに役職を付与
    await member.add_roles(role)


#コマンド
@tree.command(name="rand", description="ランダム選曲(例:level=9+,level2=11 ➡ 9+~11)\n(ランダム選曲CHのみ)")
async def music_random(ctx, level:str=None, level2:str=None):
    try:
        #ランダム選曲チャンネルのみ有効
        if ctx.channel_id == RandomSelect_CH or ctx.channel_id == Create_RoomID:
            if level == None and level2 == None:
                music, level_str, dif, image = await Arcaea_command.Random_Select_Level()
            elif level != None and level2 == None:
                music, level_str, dif, image  = await Arcaea_command.Random_Select_Level(level)
            else:
                music, level_str, dif, image  = await Arcaea_command.Random_Select_Level(level, level2)

            #ランダムで決まった曲を返信
            return await ctx.response.send_message(f"課題曲:{music} {dif}:{level_str}です!!", file=discord.File(image))

        else:
            #利用場所エラー
            return await noaction_messeage(ctx)

    #エラー処理
    except Exception:
        return await ctx.response.send_message("コマンドが間違ってるかも。もう一度試してみて!", ephemeral=True)


@tree.command(name="sign_up", description="対戦を使うための登録(初回のみ)\n(対戦CHのみ)")
async def sign_up(ctx):
    #対戦チャンネルのみ有効
    if ctx.channel_id == RandomBattle_CH or ctx.channel_id == Create_RoomID:
        #メンバーリストを取得
        MemberList = pd.read_csv(os.environ["MEMBER"])
        #登録済みか確認
        if MemberList["Discord_ID"].isin([ctx.user.id]).any().any():
            return await ctx.response.send_message("既に登録されています。", ephemeral=True)

        #登録する
        signup_user = pd.DataFrame([[ctx.user.display_name, ctx.user.id, False]], columns=MemberList.columns) #新規ユーザーデータを作成
        MemberList = pd.concat([MemberList, signup_user])
        MemberList = MemberList.astype({"Discord_ID":"int64"})
        MemberList.to_csv(os.environ["MEMBER"], index=False)
            
        return await ctx.response.send_message("登録完了です!")
    else:
        #利用場所エラー
        return await noaction_messeage(ctx)


@tree.command(name="vs", description="対戦システムを起動。\n(対戦CHのみ)")
async def vs_select(ctx):
    try:
        #対戦チャンネルのみ有効
        if ctx.channel_id == RandomBattle_CH or ctx.channel_id == Create_RoomID:
            #選択画面の表示
            view = ui.VSButton(timeout=300)
            return await ctx.response.send_message(view=view)
        
        else:
            #利用場所エラー
            return await noaction_messeage(ctx)
    
    #エラー処理
    except Exception:
        return await ctx.response.send_message("コマンドが間違ってるかも。もう一度試してみて!", ephemeral=True)


@tree.command(name="log", description="対戦記録を表示。\n(対戦CHのみ)")
async def log_view(ctx):
    try:
        #対戦チャンネルのみ有効
        if ctx.channel_id == RandomBattle_CH or ctx.channel_id == Create_RoomID:
            ##Score勝負の結果集計
            file_1vs1_log = os.environ["SCORE_LOG"]
            user = ctx.user #入力したユーザー名を取得
            battledata = await Arcaea_command.User_Status(ctx, user.id, file_1vs1_log)

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
            file_EX1vs1_log = os.environ["EXSCORE_LOG"]
            battledata = await Arcaea_command.User_Status(ctx, user.id, file_EX1vs1_log)

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
            await ctx.response.send_message(embed=embed)

        else:
            #利用場所エラー
            return await noaction_messeage(ctx)
    
    #エラー処理
    except Exception:
        return await ctx.response.send_message("コマンドが間違ってるかも。もう一度試してみて!", ephemeral=True)


@tree.command(name="master_log", description="対戦記録ファイルを出力。(作者のみ)", )
async def master_log_view(ctx):
    try:
        #戦績ファイルを出力する(開発者用)
        if ctx.channel_id == Creater_DM.id:
            await ctx.response.send_message(file=discord.File(os.environ["SCORE_LOG"]))
            await  ctx.followup.send(file=discord.File(os.environ["EXSCORE_LOG"]))

        else:
            #利用場所エラー
            return await noaction_messeage(ctx)

    #エラー処理
    except Exception:
        return await ctx.response.send_message("データを正しく出力できませんでした。", ephemeral=True)


#デバック用コマンド
#@tree.command(name="c_state", description="ステ変更(デバック)", )
#async def state(ctx):
#    await Arcaea_command.state_chenge(ctx.user.id, False)
#    return await ctx.response.send_message("変更しました。")
    

    ##ポテンシャル計算機(身内用)
    #if message.channel.id == 1071411461508841593:
    #    #ポテンシャルを計算する
    #    if message.content.startswith('/a pt'):
    #        comannd = message.content.split(' ')
    #        music_ls = []
    #        try:
    #            score = int(comannd[-1])
    #            byd_flg = "FTR"
    #            for i in range(len(comannd)-3):
    #                music_ls.append(comannd[i+2])
    #
    #        except ValueError:
    #            score = int(comannd[-2])
    #            byd_flg = comannd[-1]
    #
    #            for i in range(len(comannd)-4):
    #                music_ls.append(comannd[i+2])
    #
    #        #listから曲名を作成
    #        music = " ".join(music_ls)
    #
    #        #ポテ計算を実行
    #        potential, score_r, difficult = Arcaea_command.Potential_Score(music, score, byd_flg)
    #
    #        #返信文を作成
    #        reply = f"Music:{music} ({difficult})\nScore:{score_r}\nPt:{potential}"
    #
    #        #メンションをつけて返信
    #        await message.reply(reply)


async def noaction_messeage(ctx):
    """使用できない場所でコマンドを使用したときに送信"""
    await ctx.response.send_message("ここではこのコマンドは使用できません", ephemeral=True)


#Botを起動
client.run(TOKEN)
#try:
#    client.run(TOKEN) #bot起動処理
#except discord.errors.HTTPException:
#    os.system('kill 1')
#    os.system("python restarter.py")