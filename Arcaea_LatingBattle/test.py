import Config

a = Config.setting()

def b():
    a.BattleFlg = True

def c():
    print(a.BattleFlg)

c()
b()
c()