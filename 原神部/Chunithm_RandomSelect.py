import pandas as pd 
import random
import asyncio
import requests

#チームコースの曲を決める関数
def Music_Select(const1=0, const2=15.4):
    #定数を決めていない時は全曲から選ぶ
    const1 = float(const1)
    const2 = float(const2)
        
    #楽曲情報をデータフレームに読み込む
    df_music = pd.read_csv("chunirec.csv")

    #楽曲数を取得
    df_music = df_music[df_music["MAS_Const"] >= const1]
    df_music = df_music[df_music["MAS_Const"] <= const2]

    #乱数の範囲を取得
    music_num = len(df_music)

    #選曲された曲を追加するリストを作成
    music_list = []
    
    #選曲
    for i in range(3):
        a = random.randint(0,music_num-1)

        #乱数から選ばれた楽曲を抽出
        hit_music = df_music.iloc[a]

        #リストに保存
        music_list.append(hit_music["Music_Title"])

    return music_list


async def test(client, thread, session_dic):
    await thread.send("テスト")
    
    def a(m):
        if m.channel.id == session_dic[m.author.id]:
            return True
    
    await client.wait_for('message', check=a, timeout=600)
    await thread.send("テスト2")


async def worst_best(name, level):
    TOKEN = "76e210508cb76a99f588449b6c04c4efbcf471f40e6adc37625c58e7fdb74780e171a64b53f4044f00b758c3e9aebc826fd0e86d983ef864af53aba3111278b0"

    #とりあえず例として、どこかのWeb APIを叩くことにする
    url = f"https://api.chunirec.net/2.0/records/showall.json?user_name={name}&region=jp2&token={TOKEN}"

    #requests.getを使うと、レスポンス内容を取得できるのでとりあえず変数へ保存
    response = requests.get(url)

    #response.json()でJSONデータに変換して変数へ保存
    jsonData = response.json()

    #jsonからデータフレームに変換
    df = pd.json_normalize(jsonData)