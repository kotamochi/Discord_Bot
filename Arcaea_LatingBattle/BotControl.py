import os
import csv
import json
import asyncio
import discord
from discord import app_commands
import pandas as pd
import Config
import Matching
import RatingBattle
import TornamentCommand

#設定の読み込み
Setting = Config.setting()

#自分のBotのアクセストークンを取得
with open(Setting.BotTokenFile) as file:
    token = json.load(file)

#自分のBotのアクセストークン
TOKEN = token["TokenKey"]

#接続に必要なオブジェクトを生成
client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)

#起動時に動作する処理
@client.event
async def on_ready():
    #起動したらターミナルにログイン通知が表示される
    print("ログイン完了")
    #常設コマンドのインスタンス作成
    global cmd
    cmd = TornamentCommand.Command(Setting, client)
    await tree.sync()
    

#コマンドに対応した処理
@tree.command(name="eventstart", description="大会を始める(管理者のみ)")
async def event_start(ctx):
    '''大会を開始する(Masterのみ使用可)'''
    if ctx.channel_id == Setting.EventRoom and ctx.user.id == Setting.MasterID:
        #対戦、マッチメイキングのインスタンス
        global match
        match = Matching.BattleMatching(Setting, client, cmd)
        global battle
        battle = RatingBattle.BattleManager(Setting, client)

        #対戦を開始
        Setting.BattleFlg = True #対戦中のフラグを立てる
        await match.battle_start(ctx)
    else:
        await ctx.response.send_message("このコマンドは管理者しか使えないよ")


@tree.command(name="eventresult", description="大会の最終結果を発表(管理者のみ)")
async def event_result(ctx):
    '''大会の最終結果を表示する(Masterのみ使用可)'''
    if ctx.channel_id == Setting.EventRoom and ctx.user.id == Setting.MasterID:
        await ctx.response.send_message("結果発表~~~~~~~~~~~~~!!!!!!!!!")
        await asyncio.sleep(3)
        #最終結果表示
        await cmd.show_result()
    else:
        await ctx.response.send_message("このコマンドは管理者しか使えないよ")


@tree.command(name="join", description="ユーザー登録を行うよ")
async def join(ctx, pt:float):
    '''ユーザー登録を行う'''
    if ctx.channel_id == Setting.CommandRoom:
        await cmd.join_userlist(ctx, pt) #ユーザー登録関数
    else:
        await ctx.response.send_message("ここでは登録できないよ\nCommandチャンネルで登録してね")
        

@tree.command(name="match", description="対戦を始めるよ(期間中,DMのみ)")     
async def matching(ctx):
    '''マッチングを開始する'''
    if ctx.guild_id == None: #DMであるか
        if Setting.BattleFlg: #対戦期間中か
            await ctx.response.send_message("マッチングを開始します") #DMに送信
            user_id = ctx.user.id #idを取得

            #対戦待ちにリストに書き込み
            error_flg, error_content = await match.join_list(user_id)
            if error_flg: #エラーがあった場合、エラー内容を送信して終了
                return await ctx.channel.send(error_content)

            #マッチするまで待機する
            async with ctx.channel.typing(): #マッチング待機中は入力中にする
                while True:
                    match_flg = await match.match_check(user_id) #マッチングが成立しているか確認
                    if match_flg:
                        return await ctx.channel.send("マッチングが成立しました。対戦を開始します。") #成立したので終了する
                    else:
                        await asyncio.sleep(3) #成立しなかったら3秒待って再度確認へ
        else:
            await ctx.response.send_message("対戦期間外だよ")
    else:
        await ctx.response.send_message("ここでは使えないよ。ToolBotsのDMで使用してね")


@tree.command(name="rate", description="自分の現在レートが見れるよ(DMのみ)")
async def rate(ctx):
    '''現在レートを表示する'''
    if ctx.guild_id == None: #DMであるか
        await cmd.now_rating(ctx)
    else:
        await ctx.response.send_message("ここでは使えないよ。ToolBotsのDMで使用してね")


@tree.command(name='selfmatch', description="手動でマッチングを行うよ(運営のみ)")
async def self_match(ctx, player1:discord.User, player2:discord.User):
    '''非常時に手動マッチングを行う'''
    observers = await cmd.get_observars(ctx) #運営者一覧を取得
    if ctx.channel_id == Setting.MatchRoom and ctx.user.id in observers:
        #コマンドからBotへの指令文を作成して送信
        msg = f"~MatchAnnounce~ playerID {player1[2:-1]} {player2[2:-1]}"
        BotRoom = client.get_channel(Setting.BotRoom)
        await BotRoom.send(msg)
    else:
        await ctx.response.send_message("このコマンドは運営しか使えないよ")
        

@client.event
async def on_message(message):
    '''Botへの指令を受け取る'''
    #bot自身のメッセージへの反応
    if message.author.id == Setting.BotID:
        #マッチが成立したことをbotに知らせるメッセージを受け取る
        if message.channel.id == Setting.BotRoom and message.content.startswith("~MatchAnnounce~"):
            #対戦を起動
            await battle.rating_battle(message) #対戦用関数を実行    
    return


#Botを起動
client.run(TOKEN)