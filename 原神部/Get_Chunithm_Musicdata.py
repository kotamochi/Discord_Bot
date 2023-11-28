import requests
import json
import pandas as pd
TOKEN = "76e210508cb76a99f588449b6c04c4efbcf471f40e6adc37625c58e7fdb74780e171a64b53f4044f00b758c3e9aebc826fd0e86d983ef864af53aba3111278b0"

#とりあえず例として、どこかのWeb APIを叩くことにする
url = f"https://api.chunirec.net/2.0/music/showall.json?region=jp2&token={TOKEN}"

print(url)
#requests.getを使うと、レスポンス内容を取得できるのでとりあえず変数へ保存
response = requests.get(url)

#response.json()でJSONデータに変換して変数へ保存
jsonData = response.json()

#jsonからデータフレームに変換
df = pd.json_normalize(jsonData)

#必要ないデータを削除
df.drop(columns=['meta.id', 'meta.release', 'data.BAS.level', 'data.BAS.const', 'data.BAS.maxcombo', 'data.BAS.is_const_unknown',
                 'data.ADV.level', 'data.ADV.const', 'data.ADV.maxcombo', 'data.ADV.is_const_unknown',
                 'data.EXP.level', 'data.EXP.const', 'data.EXP.maxcombo', 'data.EXP.is_const_unknown',
                 'data.MAS.maxcombo', 'data.MAS.is_const_unknown', 'data.ULT.maxcombo', 'data.ULT.is_const_unknown',
                 'data.WE.level', 'data.WE.const', 'data.WE.maxcombo', 'data.WE.is_const_unknown'], inplace=True)

#カラム名を設定
columns = ["Music_Title", "Genre", "Artist", "BPM", "MAS_Level", "MAS_Const", "ULT_Level", "ULT_Const"]
#カラム名を変更
df.columns = columns

#WE譜面を削除
df.dropna(subset=["MAS_Level"], inplace=True)

#csvに保存する
df.to_csv("chunirec.csv", index=False)
