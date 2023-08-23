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


df.to_csv("chunirec.csv")
