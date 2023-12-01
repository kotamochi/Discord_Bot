#各種設定を行う
class setting():
    WatingFile = ["Datas/MatchWaitList_1.csv", "Datas/MatchWaitList_2.csv"]
    UserFile = "Datas/UserList.csv"
    ObserverFile = "Datas/ObserverID.csv"
    BotID = 1143179888984064130 #BOTのユーザーID
    MatchRoom = 1153650397634891807 #テスト用
    BotRoom = 1179647382699376720 #裏でのbot動作用チャンネル #テスト用
    EventTime = 2 #レート戦開催期間(時間)
    GroupDivision = 12.40 #部門を分けるpt値
    RatingRange = 100
    BattleFlg = False #対戦が開始しているかを判定する
    #レートの上下幅の設定
    __Ratio = [100 - 20*i for i in range(11)]                                #レート差のキーを作成
    __Addition_Ratio = [int(30 * round(1.5 - (i*0.1),1)) for i in range(11)] #レート差に応じた倍率の値を作成
    RateTrend_Dic = dict(zip(__Ratio, __Addition_Ratio))                     #レートの上下幅の辞書