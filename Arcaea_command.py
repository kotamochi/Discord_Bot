import pandas as pd
import random
import math

def random_select(const1=0, const2=12.0):
    #定数を決めていない時は全曲から選ぶ
    const1 = float(const1)
    const2 = float(const2)
    
    #楽曲情報をデータフレームに読み込む
    df_music = pd.read_csv("Arcaea_Music_Data.csv")
    
    #楽曲数を取得
    df_music = df_music[df_music["FTR_Const"] >= const1]
    df_music = df_music[df_music["FTR_Const"] <= const2]
    
    #乱数の範囲を取得
    music_num = len(df_music)

    rand = random.randint(0,music_num-1)

    #乱数から選ばれた楽曲を抽出
    hit_music = df_music.iloc[rand]

    #結果を保存
    music = hit_music["Music_Title"]
    level = hit_music["FTR_Level"]
    
    if level % 1 != 0.0:
        level_str = str(math.floor(level)) + "+"
    else:
        level_str = str(math.floor(level))
        
    return music, level_str