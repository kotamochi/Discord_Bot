import pandas as pd 
import random
import asyncio

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