#各種設定を行う
class setting():
    #ファイルパス
    WatingFile = ["Datas/MatchWaitList_1.csv", "Datas/MatchWaitList_2.csv"] #マッチ待機ファイル
    UserFile = "Datas/UserList.csv" #参加者登録ファイル
    ObserverFile = "Datas/ObserverID.csv" #大会運営コマンド起動可能者ファイル
    BotID = 1143179888984064130 #BOTのユーザーID
    MatchRoom = 1180148416442023966 #対戦チャンネル
    CommandRoom = 1180159444873658431 #コマンド系を受け付けるチャンネル
    BotRoom = 1180149262231797802 #裏でのbot動作用チャンネル
    GroupDivision = 12.40 #部門を分けるpt値
    RatingRange = 100 #対戦のマッチレート幅(+-)
    BattleFlg = False #対戦が開始しているかを判定する
    EventTime = 7200 #レート戦開催期間(秒)
    MatchTime = 10 #マッチメイキングの間隔(秒)
    RankingTime = 600 #現在のランキング表示間隔(秒)
    #レートの上下幅の設定
    __Ratio = [100 - 20*i for i in range(11)]                                #レート差のキーを作成
    __Addition_Ratio = [int(30 * round(1.5 - (i*0.1),1)) for i in range(11)] #レート差に応じた倍率の値を作成
    RateTrend_Dic = dict(zip(__Ratio, __Addition_Ratio))                     #レートの上下幅の辞書
