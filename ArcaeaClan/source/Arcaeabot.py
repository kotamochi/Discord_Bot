import os
import dotenv
import datetime
import pandas as pd
import discord
from discord.ext import tasks
from discord import app_commands
import ui
import Arcaea_command


#.envファイルの読み込み
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
    global Creater_DM, Creater_ID, Server_ID, MemberRole_ID, SubRole_ID, RandomSelect_CH, RandomBattle_CH, Create_RoomID
    Creater_ID = int(os.environ["CREATER_ID"])
    Server_ID = int(os.environ["SERVER_ID"])
    MemberRole_ID = int(os.environ["MEMBERROLE_ID"])
    SubRole_ID = int(os.environ["SUBROLE_ID"])
    RandomSelect_CH = int(os.environ["MUSIC_CH"])
    RandomBattle_CH = int(os.environ["BATTLE_CH"])
    Create_RoomID = int(os.environ["CREATER_ROOM_ID"])
    #管理者のDMオブジェクトを作成
    Creater = await client.fetch_user(Creater_ID)
    Creater_DM = await Creater.create_dm()

    #コマンドの更新
    await tree.sync()
    #viwe = await tree.fetch_commands() #登録されてるコマンドを表示するやつ(確認用)
    #print(viwe)

    #ログイン通知
    await Creater_DM.send("起動したよ")
    #起動チェック処理実行
    await chack_online.start()

#60秒ごとに実行
@tasks.loop(seconds=60) 
async def chack_online():
    """毎日定刻に起動チェックを行う"""
    #時刻確認
    now = datetime.datetime.now()
    oncheaktime =now.strftime('%H:%M')
    musictasktime = now.strftime('%A %H:%M')

    #定刻に管理者DMに起動チェックを送信とメンバーリスト更新
    if oncheaktime == '09:00':
        #メンバーリストの更新
        guild_info = client.get_guild(Server_ID) #サーバー情報を取得
        members_info = guild_info.get_role(MemberRole_ID).members
        sub_info = guild_info.get_role(SubRole_ID).members
        sub_ids = [i.id for i in sub_info]
        
        #一人ずつデータを作成
        member_list = []
        for member in members_info:
            if member.id in sub_ids:
                #サブ垢は飛ばす
                pass
            else:
                #データ作成
                user_data = [member.display_name, member.id, False]
                #データをリストに追加
                member_list.append(user_data)
                
        #MemberListをDataFrameにして保存
        df_members = pd.DataFrame([member_list], columns={"User_Name", "Discord_ID", "State"}) #新規ユーザーデータを作成
        df_members = df_members.astype({"Discord_ID":"int64"}) #データの型変換
        df_members.to_csv(os.environ["MEMBERLIST"], index=False) #保存
        
        #起動通知
        await Creater_DM.send("起動中...メンバーリスト更新完了。")


@client.event
async def on_member_join(member):
    """サーバー参加時にロール付与"""
    #Roleオブジェクトを取得
    role = member.guild.get_role(MemberRole_ID)
    #入ってきたMemberに役職を付与
    await member.add_roles(role)
    await client.guilds.get_role(MemberRole_ID)

#コマンド
@tree.command(name="rand", description="ランダム選曲(例:例:dif=FTR,level=9+,level2=11 ➡ FTR 9+~11))\n(ランダム選曲CHのみ)")
async def music_random(ctx, dificullity:str=None, level:str=None, level2:str=None):
    """ランダム選曲を行うコマンド"""
    try:
        #ランダム選曲CHのみで有効
        if ctx.channel_id == RandomSelect_CH or ctx.channel_id == Create_RoomID:
            #選曲を実行
            music, level_str, dif, image = await Arcaea_command.Random_Select_Level(level, level2, dificullity)

            #ランダムで決まった曲を返信
            return await ctx.response.send_message(f"{ctx.user.mention}さんに課題曲:{music} {dif}:{level_str}です!!", file=discord.File(image))

        else:
            #利用場所エラー
            return await noaction_messeage(ctx)

    #エラー処理
    except Exception:
        return await ctx.response.send_message("コマンドが正しく動作しませんでした。もう一度試してみて!", ephemeral=True)


@tree.command(name="sign_up", description="対戦を使うための登録(初回のみ)\n(対戦CHのみ)")
async def sign_up(ctx):
    """対戦"""
    try:
        #対戦CHのみで有効
        if ctx.channel_id == RandomBattle_CH or ctx.channel_id == Create_RoomID:
            #メンバーリストを取得
            MemberList = pd.read_csv(os.environ["MEMBERLIST"])
            #登録済みか確認
            if MemberList["Discord_ID"].isin([ctx.user.id]).any().any():
                #登録済みなら通知して処理を終わる
                return await ctx.response.send_message("既に登録されています。", ephemeral=True)

            #登録処理
            signup_user = pd.DataFrame([[ctx.user.display_name, ctx.user.id, False]], columns=MemberList.columns) #新規ユーザーデータを作成
            MemberList = pd.concat([MemberList, signup_user]) #既存データと結合
            MemberList = MemberList.astype({"Discord_ID":"int64"}) #データの型変換
            MemberList.to_csv(os.environ["MEMBERLIST"], index=False) #保存

            #登録完了を知らせる
            return await ctx.response.send_message("登録完了です!")
        else:
            #利用場所エラー
            return await noaction_messeage(ctx)
        
    #エラー処理
    except Exception:
        return await ctx.response.send_message("コマンド処理中にエラーが発生したよ。もう一度試してみて!", ephemeral=True)


@tree.command(name="vs", description="対戦システムを起動。\n(対戦CHのみ)")
async def vs_select(ctx):
    try:
        #対戦CHでのみ有効
        if ctx.channel_id == RandomBattle_CH or ctx.channel_id == Create_RoomID:
            #選択画面の表示
            view = ui.VSButton(timeout=300) #5分でuiを削除
            return await ctx.response.send_message(view=view)
        
        else:
            #利用場所エラー
            return await noaction_messeage(ctx)
    
    #エラー処理
    except Exception:
        return await ctx.response.send_message("コマンド処理中にエラーが発生したよ。もう一度試してみて!", ephemeral=True)


@tree.command(name="log", description="対戦記録を表示。\n(対戦CHのみ)")
async def log_view(ctx):
    try:
        #対戦CHでのみ有効
        if ctx.channel_id == RandomBattle_CH or ctx.channel_id == Create_RoomID:
            user = ctx.user #コマンドを入力したユーザー名を取得
            
            ##Score勝負の結果集計
            file_1vs1_log = os.environ["SCORE_LOG"]
            #戦績を取得
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
            #戦績を取得
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
        return await ctx.response.send_message("コマンド処理中にエラーが発生したよ。もう一度試してみて!", ephemeral=True)


@tree.command(name="master_log", description="対戦記録ファイルを出力。(管理者のみ)", )
async def master_log_view(ctx):
    """管理者用コマンド 戦績ファイルの取得"""
    try:
        #管理者のDMでのみ有効
        if ctx.channel_id == Creater_DM.id:
            await ctx.response.send_message(file=discord.File(os.environ["SCORE_LOG"]))
            await  ctx.followup.send(file=discord.File(os.environ["EXSCORE_LOG"]))

        else:
            #利用場所エラー
            return await noaction_messeage(ctx)

    #エラー処理
    except Exception:
        return await ctx.response.send_message("データを正しく出力できませんでした。", ephemeral=True)
    

async def noaction_messeage(ctx):
    """使用できない場所でコマンドを使用したときに送信"""
    await ctx.response.send_message("ここではこのコマンドは使用できません", ephemeral=True)


#Botを起動
client.run(TOKEN)