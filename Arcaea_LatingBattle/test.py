import Config
import pandas as pd
a = Config.setting()

df_user = pd.read_csv(a.ObserverFile)
#df_mydata = df_user[df_user["Discord_ID"] == 502838276294705162]
if df_user.isin([502838276294705162]).any().any():
    print(500)
#if df_mydata["State"].item():
#    print("4234")
#else:
#    print("fefe")