import Config
import pandas as pd
import Matching
import TornamentCommand
a = Config.setting()


message= "a a 502838276294705162 1141419953942175754"
comannd = message.split(' ')
player_id = [int(comannd[2]), int(comannd[3])]
player_mention = [f"<@{comannd[2]}>", f"<@{comannd[3]}>"]
df_user = pd.read_csv(a.UserFile) #ユーザーファイル読み込み
player_rate = df_user[(df_user["Discord_ID"] == player_id[0]) | (df_user["Discord_ID"] == player_id[1])]
win_id = 502838276294705162
#rate1 = int(player_rate.query("Discord_ID == @win_id").loc[:,"Rating"].values)
#rate1 = round(rate1 / 20) * 20

ls = {100:45,
      80:42,
      60:39,
      40:36,
      20:33,
      0:1.30,
      -20:27,
      -40:24,
      -60:21,
      -80:18,
      -100:15
}
music = "Lumia"
df_user = pd.read_csv(a.UserFile) #ユーザーデータ取得
for _, player_data in df_user.iterrows():
      id = player_data["Discord_ID"]
      print(id)
      
print(int(0/60))