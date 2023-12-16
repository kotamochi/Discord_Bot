import os

#プログラム言語を始める
print("Hello World")

#処理
a = 1
if a == a:
    a = 1
    
#プログラミング言語を終わる
print("Python、Python、おかえりください")

#言語が帰ったか確認
if os.path.isfile("C:/Users/kotam/AppData/Local/Programs/Python/Python311/python.exe"):
    print(False) #帰ってないとき
    
else:
    print(True) #帰ったとき