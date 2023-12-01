import math
import random
import pandas as pd

#難易度ランダム選曲
def Random_Select_Level(level1="0", level2="12"):
    
    #＋難易度が指定された時は.7表記に変更する
    try:
        #引き数を数値型に変換
        level1 = float(level1)
    except ValueError:
        #引き数を数値型に変換
        if level1[-1] == "+":
            level1 = float(level1[:-1]) + 0.7
    
    try:        
        level2 = float(level2)
    except ValueError:
        if level2[-1] == "+":
            level2 = float(level2[:-1]) + 0.7
        
    #指定レベルが一つならその難易度のみから選曲
    if level2 == 12.0 and level1 != 0.0:
        level2 = float(level1)
    
    #楽曲情報をデータフレームに読み込む
    df_music = pd.read_csv("Datas/Arcaea_Music_Data.csv")
    
    #楽曲数を取得
    df_music_FTR = df_music[df_music["FTR_Level"] >= level1].copy()
    df_music_FTR = df_music_FTR[df_music_FTR["FTR_Level"] <= level2]

    df_music_BYD = df_music[df_music["BYD_Level"] >= level1].copy()
    df_music_BYD = df_music_BYD[df_music_BYD["BYD_Level"] <= level2]

    df_range_music = pd.concat([df_music_FTR, df_music_BYD])
    
    #乱数の範囲を取得
    music_num = len(df_range_music)

    #乱数を作成
    rand = random.randint(0,music_num-1)

    #乱数から選ばれた楽曲を抽出
    hit_music = df_range_music.iloc[rand]

    #結果を保存
    music = hit_music["Music_Title"]
    if pd.isnull(hit_music["BYD_Level"]) == True: #BYDのレベルデータがあるデータならBYDを結果として出力する
        level = hit_music["FTR_Level"]
        deffecult = "FTR" #難易度を表示
    else:
        level = hit_music["BYD_Level"]
        deffecult = "BYD" #難易度を表示

    #楽曲レベルを表示用に調整
    if level % 1 != 0.0:
        level_str = str(math.floor(level)) + "+"
    else:
        level_str = str(math.floor(level))
        
    return music, level_str, deffecult