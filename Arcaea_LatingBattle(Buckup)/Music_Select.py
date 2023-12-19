import math
import random
import pandas as pd

#楽曲選択
async def Select_Assignment_Song(pt_1, pt_2):
    #低い方のポテンシャル基準で難易度を選択
    if pt_1 > pt_2:
        pt = pt_2
    else:
        pt = pt_1

    #難易度指定
    if pt < 11.00:
        Category = 7
    elif pt < 11.50:
        Category = 6
    elif pt < 12.00:
        Category = 5
    elif pt < 12.40:
        Category = 4
    elif pt < 12.60:
        Category = 3
    elif pt < 12.90:
        Category = 2
    else:
        Category = 1
        
    #楽曲情報をデータフレームに読み込む
    df_music = pd.read_csv("Datas/Battle_Music_Data.csv")
    
    #楽曲数を取得
    df_range_music = df_music[df_music["CategoryNo"] == Category]
    
    #乱数の範囲を取得
    music_num = len(df_range_music)

    #乱数を作成
    rand = random.randint(0,music_num-1)

    #乱数から選ばれた楽曲を抽出
    hit_music = df_range_music.iloc[rand]

    #結果を保存
    music = hit_music["Music_Title"]
    if pd.isnull(hit_music["BYD_Level"]) == True and pd.isnull(hit_music["PRS_Level"]) == True: #BYDのレベルデータがあるデータならBYDを結果として出力する
        level = hit_music["FTR_Level"]
        deffecult = "FTR" #難易度を表示
    elif pd.isnull(hit_music["PRS_Level"]) == True:
        level = hit_music["BYD_Level"]
        deffecult = "BYD" #難易度を表示
    else:
        level = hit_music["PRS_Level"]
        deffecult = "PRS" #難易度を表示
        
    #ジャケット画像データを取得
    df_image = pd.read_csv("Datas\Battle_Music_Image.csv")
    image = df_image.query("Music_Title == @music").loc[:,"Image"].iloc[-1]

    #楽曲レベルを表示用に調整
    if level % 1 != 0.0:
        level_str = str(math.floor(level)) + "+"
    else:
        level_str = str(math.floor(level))
        
    return music, level_str, deffecult, image