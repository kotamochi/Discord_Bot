import pandas as pd
import random
import math


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
        
    #レベル指定がない時は全曲から選ぶ
    if level2 == 12.0 and level1 != 0.0:
        level2 = float(level1)
    
    #楽曲情報をデータフレームに読み込む
    df_music = pd.read_csv("Arcaea_Music_Data.csv")
    
    #楽曲数を取得
    df_music_FTR = df_music[df_music["FTR_Level"] >= level1].copy()
    df_music_FTR = df_music_FTR[df_music["FTR_Level"] <= level2]

    df_music_BYD = df_music[df_music["BYD_Level"] >= level1].copy()
    df_music_BYD = df_music_BYD[df_music["BYD_Level"] <= level2]

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

#ポテンシャル値の計算
def Potential_Score(music, score, difficult="FTR"):

    #楽曲情報をデータフレームに読み込む
    df_music = pd.read_csv("Arcaea_Music_Data.csv")

    #ptを算出したい曲のデータを取得
    pt_music = df_music[df_music["Music_Title"] == music]

    #登録されている略称(ニックネーム)でも可
    if pt_music["Music_Title"].empty == True:
        pt_music = df_music[df_music["Nickname"] == music]

    #曲の譜面定数情報を取得
    if difficult == "BYD" or difficult == "byd": #BYDの定数を取得
        pt_music_b = pt_music.dropna(subset=["BYD_Const"])
        const = float(pt_music_b["BYD_Const"].values)
        difficult = "BYD"                        #返信用に形式を統一

    else:                                        #FTRの定数を取得
        pt_music_f = pt_music.dropna(subset=["FTR_Const"])
        const = float(pt_music_f["FTR_Const"].values)

    #スコアの桁数を合わせる(994と入力したものを9,940,000に直す)
    while True:
        score_digit = len(str(score)) #現在の桁数を取得
        if score_digit == 7 or score_digit == 8:
            break
        score = score * 10

    #スコア区分を変数として作成
    PM = 10000000
    EX = 9800000
    AA = 9500000

    #楽曲のポテンシャル値を計算
    if score >= PM:
        potential = const + 2                       #譜面定数+2.0

    elif score >= EX:
        potential = const + 1 + (score - EX)/200000 #譜面定数+1.0+(スコア-9,800,000)/200,000

    else:
        potential = const + (score - AA)/300000     #譜面定数+(スコア-9,500,000)/300,000 (下限は0)

        #※ポテンシャル値は0以下にならない
        if potential <= 0:
            potential = 0

    return round(potential, 2), score, difficult #少数第３位を四捨五入して表示



#現在使用していない機能
#定数ランダム選曲
def Random_Select_Const(const1="0", const2="12.0"):
    
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