import discord
from discord import ui
import Arcaea_command
import asyncio


class VSButton(ui.View):
    """対戦システムの選択ボタン"""
    def __init__(self, timeout=None):
        #初期設定
        super().__init__(timeout=timeout)
    
    @ui.button(label="スコアバトル(1vs1)", style=discord.ButtonStyle.success)
    async def score(self, button: discord.ui.Button, interaction: discord.Interaction):
        """1vs1(Score)"""
        await Arcaea_command.match_host(button, button.user.id, "0")

    @ui.button(label="EXスコアバトル(1vs1)", style=discord.ButtonStyle.blurple)
    async def exscore(self, button: discord.ui.Button, interaction: discord.Interaction):
        """1vs1(EXScore)"""
        await Arcaea_command.match_host(button, button.user.id, "1")
        
    async def msg_send(self, msg):
        #ボタンメッセージを渡す
        self.message = msg

    async def on_timeout(self):
        """タイムアウト処理"""
        #タイムアウトになったらボタンを削除
        await self.message.delete()


class VSHostButton(ui.View):
    """対戦募集ボタン"""
    def __init__(self, user, kind, timeout=None):
        self.host = user
        self.kind = kind
        self.timeout_flg = True
        super().__init__(timeout=timeout)

    @ui.button(label="参加する", style=discord.ButtonStyle.success)
    async def vsstart(self, button: discord.ui.Button, interaction: discord.Interaction):
        guest = button.user.id
        #参加者のステータス確認
        if await Arcaea_command.state_check(guest):
            return await button.response.send_message(f"あなたは対戦中、もしくは対戦ホスト中です。", ephemeral=True)
        else:
            self.timeout_flg = False
            #募集ボタンを削除
            await button.message.delete()
            #対戦処理を開始
            await Arcaea_command.Arcaea_ScoreBattle(button, self.host, guest, self.kind)

    @ui.button(label="取り消し(ホストのみ可)", style=discord.ButtonStyle.gray)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.host == button.user.id:
            self.timeout_flg = False
            #募集を取り消し
            await button.message.delete()
            #ホストのステータスを変更
            await Arcaea_command.state_chenge(button.user.id, False)
            await button.response.send_message("募集を取り消しました。", ephemeral=True)
        else:
            await button.response.send_message("あなたはこの募集のホストではありません。", ephemeral=True)
              
    async def msg_send(self, msg):
        #ボタンメッセージを渡す
        self.message = msg
            
    async def on_timeout(self):
        """タイムアウト処理"""
        if self.timeout_flg:
            #タイムアウトになったらボタンを削除
            await self.message.edit(content="タイムアウトにより、募集は取り消されました。", view=None)
            #ホストのステータスを変更
            await Arcaea_command.state_chenge(self.host, False)


class VSStopbutton(ui.View):
    """対戦を途中終了する"""
    def __init__(self, user1, user2, timeout=180):
        self.player = [user1, user2]
        self.click = []
        super().__init__(timeout=timeout)

    @ui.button(label="終了", style=discord.ButtonStyle.gray)
    async def stop(self, button: discord.ui.Button, interaction: discord.Interaction):
        #対戦者かチェック
        flg = await self.check(button.user.id)
        if flg:
            #同じプレイヤーが再び押していないか
            if button.user.id in self.click:
                await button.response.send_message("すでに押しています。", ephemeral=True)
            else:
                #ボタンをクリックした人を追加
                self.click.append(button.user.id)
                #二人ともがボタンを押したら終了処理を行う
                if len(self.click) == 2:
                    await button.response.send_message(f"{button.user.display_name}が終了を選択しました。\n対戦を終了します。")
                    await asyncio.sleep(3) #インターバル
                    await button.channel.delete() #スレッドを閉じる
                    #対戦ステータスを変更
                    for user in self.player:
                        await Arcaea_command.state_chenge(user, False)
                else:
                    await button.response.send_message(f"{button.user.display_name}が終了を選択しました。")
        else:
            await button.response.send_message("あなたは対戦者ではありません。", ephemeral=True)

    async def check(self, user):
        """対戦者以外ではないか確認"""
        if user in self.player:
            return True #対戦者
        else:
            return False #それ以外


class VSMusicDifChoice(ui.View):
    """課題曲難易度選択ボタン"""
    def __init__(self, channel, user1, user2, EX_flg, timeout=None):
        self.channel = channel
        self.player = [user1, user2]
        self.click = []
        self.EX_flg = EX_flg
        self.FTR = False #各難易度の選択フラグ
        self.ETR = False
        self.BYD = False
        self.timeout_flg = True
        super().__init__(timeout=timeout)

    @ui.button(label="FTR", style=discord.ButtonStyle.gray)
    async def ftr(self, button: discord.ui.Button, interaction: discord.Interaction):
        #対戦者かチェック
        if await self.check(button.user.id):

            if self.FTR == False:
                self.FTR = True
                self.children[0].style = discord.ButtonStyle.success
            else:
                self.FTR = False
                self.children[0].style = discord.ButtonStyle.gray

            #結果を表示
            await button.response.edit_message(view=self)
            await self.check_show_dif(button)
        else:
            await button.response.send_message("きみは対戦者じゃないよ", ephemeral=True)

    @ui.button(label="ETR", style=discord.ButtonStyle.gray)
    async def etr(self, button: discord.ui.Button, interaction: discord.Interaction):
        #対戦者かチェック
        if await self.check(button.user.id):

            if self.ETR == False:
                self.ETR = True
                self.children[1].style = discord.ButtonStyle.success
            else:
                self.ETR = False
                self.children[1].style = discord.ButtonStyle.gray
                
            #結果を表示
            await button.response.edit_message(view=self)
            await self.check_show_dif(button)
        else:
            await button.response.send_message("きみは対戦者じゃないよ", ephemeral=True)

    @ui.button(label="BYD", style=discord.ButtonStyle.gray)
    async def byd(self, button: discord.ui.Button, interaction: discord.Interaction):
        #対戦者かチェック
        if await self.check(button.user.id):
            if self.BYD == False:
                self.BYD = True
                self.children[2].style = discord.ButtonStyle.success
            else:
                self.BYD = False
                self.children[2].style = discord.ButtonStyle.gray

            #結果を表示
            await button.response.edit_message(view=self)
            await self.check_show_dif(button)
        else:
            await button.response.send_message("きみは対戦者じゃないよ", ephemeral=True)

    @ui.button(label="選択OK!!", style=discord.ButtonStyle.blurple)
    async def ok(self, button: discord.ui.Button, interaction: discord.Interaction):
        #対戦者かチェック
        if await self.check(button.user.id):
            #難易度が選ばれているか
            if self.FTR == False and self.ETR == False and self.BYD == False:
                await button.response.send_message("難易度が選ばれてないよ！！")
            else:
                #同じプレイヤーが再び押していないか
                if button.user.id in self.click:
                    await button.response.send_message("もう押してるよ！", ephemeral=True)
                else:
                    #ボタンをクリックした人を追加
                    self.click.append(button.user.id)
                    #二人ともがボタンを押したら処理を行う
                    if len(self.click) == 2:
                        #タイムアウト処理を無効化
                        self.timeout_flg = False
                        #ボタンを決定メッセージで上書き
                        await button.response.edit_message(content="難易度が決定されたよ！", view=None)
                        await button.followup.send(f"{button.user.display_name}がOKを選択したよ！ 難易度決定！")
                        #決定した難易度をListに
                        ls = []
                        if self.FTR:
                            ls.append("FTR")
                        if self.ETR:
                            ls.append("ETR")
                        if self.BYD:
                            ls.append("BYD")

                        #レベル選択へ
                        await Arcaea_command.s_sb_selectlevel(button, self.player[0], self.player[1], ls, self.EX_flg)
                    else:
                        await button.response.send_message(f"{button.user.display_name}がOKを選択したよ！")
                
        else:
            await button.response.send_message("きみは対戦者じゃないよ", ephemeral=True)

    async def check(self, user):
        """対戦者以外ではないか確認"""
        if user in self.player:
                return True #対戦者
        else:
            return False #それ以外
        
    async def check_show_dif(self, button):
        """今選択されている難易度を表示"""
        ls = []
        if self.FTR:
            ls.append("FTR")
        if self.ETR:
            ls.append("ETR")
        if self.BYD:
            ls.append("BYD")

        #返す文を作成
        msg = "選択されている難易度"
        for dif in ls:
            msg += f":{dif}"

        #送信
        await button.followup.send(msg)

    async def on_timeout(self):
        """タイムアウト処理"""
        try:
            if self.timeout_flg:
                #タイムアウトになったらチャンネルを削除
                await self.channel.delete()
                #対戦ステータスを変更
                await Arcaea_command.state_chenge(self.player[0], False)
                await Arcaea_command.state_chenge(self.player[1], False)
        except discord.HTTPException:
            pass
            

class VSMusicLevelChoice(ui.View):
    """課題曲レベル選択ボタン"""
    def __init__(self, channel, user1, user2, dif, EX_flg, timeout=None):
        self.channel = channel
        self.player = [user1, user2]
        self.click = []
        self.EX_flg = EX_flg
        self.timeout_flg = True
        #各レベルの選択フラグ
        self.level_dic = {"7":False,
                          "7+":False,
                          "8":False,
                          "8+":False,
                          "9":False,
                          "9+":False,
                          "10":False,
                          "10+":False,
                          "11":False,
                          "12":False}
        self.dif = dif #選択されてる難易度
        self.FTR_Level = ["7", "7+", "8", "8+", "9", "9+", "10", "10+", "11"]
        self.ETR_Level = ["8", "8+", "9", "9+", "10", "10+"]
        self.BYD_Level = ["9", "9+", "10", "10+", "11", "12"]
        super().__init__(timeout=timeout)

    @discord.ui.select(cls=discord.ui.Select, placeholder="課題曲のレベルを指定してね",options=[discord.SelectOption(label="ALL"), 
                                                                                              discord.SelectOption(label="7"),
                                                                                              discord.SelectOption(label="7+"),
                                                                                              discord.SelectOption(label="8"),
                                                                                              discord.SelectOption(label="8+"),
                                                                                              discord.SelectOption(label="9"),
                                                                                              discord.SelectOption(label="9+"),
                                                                                              discord.SelectOption(label="10"),
                                                                                              discord.SelectOption(label="10+"),
                                                                                              discord.SelectOption(label="11"),
                                                                                              discord.SelectOption(label="12")]
                       )
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
        level = select.values[0]
        #全レベル指定の場合
        if level == "ALL":
            #全レベルをTrueに
            #選択されたレベルが選択中の難易度にあるか
            if "FTR" in self.dif:
                for key in self.FTR_Level:
                    self.level_dic[key] = True
            if "ETR" in self.dif:
                for key in self.ETR_Level:
                    self.level_dic[key] = True
            if "BYD" in self.dif:
                for key in self.BYD_Level:
                    self.level_dic[key] = True
        else:
            #ALL以外
            #選択されたレベルが選択中の難易度にあるか
            if "FTR" in self.dif and level in self.FTR_Level:
                pass
            elif "ETR" in self.dif and level in self.ETR_Level:
                pass
            elif "BYD" in self.dif and level in self.BYD_Level:
                pass
            else:
                #ない場合
                return await interaction.response.send_message("選択した難易度にこのレベルはないよ")

            #レベルを選択を辞書に反映
            if self.level_dic[level] == False:
                self.level_dic[level] = True
            else:
                self.level_dic[level] = False

        #今選択されている難易度を取得
        msg = "選択されているレベル"
        for key, value in self.level_dic.items():
            if value:
                msg += f":{key}"

        #送信
        await interaction.response.send_message(msg)

    @ui.button(label="選択OK!!", style=discord.ButtonStyle.success)
    async def ok(self, button: discord.ui.Button, interaction: discord.Interaction):
        #対戦者かチェック
        if await self.check(button.user.id):
            #選択されたレベルをチェック
            ls = []
            for key, value in self.level_dic.items():
                if value:
                    ls.append(key)
            
            if len(ls) == 0:
                #レベルが選ばれてないとき
                await button.response.send_message("レベルが選択されてないよ！")
            else:
                #同じプレイヤーが再び押していないか
                if button.user.id in self.click:
                    await button.response.send_message("もう押してるよ！", ephemeral=True)
                else:
                    #ボタンをクリックした人を追加
                    self.click.append(button.user.id)
                    #二人ともがボタンを押したら処理を行う
                    if len(self.click) == 2:
                        self.timeout_flg = False #タイムアウト処理を無効化
                        #ボタンを決定メッセージで上書き
                        await button.response.edit_message(content="Levelが決定したよ！",view=None)
                        await button.followup.send(f"{button.user.display_name}がOKを選択したよ！ 課題曲を発表します！！")
                        #+を.7形式に変換
                        temp_ls = []
                        for lv in ls:
                            if lv[-1] == "+":
                                lv_f = float(lv[:-1]) + 0.7
                                temp_ls.append(lv_f)
                            else:
                                lv_f = float(lv)
                                temp_ls.append(lv_f)

                        #曲選択へ
                        await Arcaea_command.s_sb_musicselect(button, self.player[0], self.player[1], self.dif, temp_ls, self.EX_flg)
                    else:
                        await button.response.send_message(f"{button.user.display_name}がOKを選択したよ！")
        else:
            await button.response.send_message("きみは対戦者じゃないよ", ephemeral=True)

    async def check(self, user):
        """対戦者以外ではないか確認"""
        if user in self.player:
            return True #対戦者
        else:
            return False #それ以外

    async def on_timeout(self):
        """タイムアウト処理"""
        try:
            if self.timeout_flg:
                #タイムアウトになったらチャンネルを削除
                await self.channel.delete()
                #対戦ステータスを変更
                await Arcaea_command.state_chenge(self.player[0], False)
                await Arcaea_command.state_chenge(self.player[1], False)
        except discord.HTTPException:
            pass


class VSMusicButton(ui.View):
    """課題曲選択ボタン"""
    def __init__(self, channel, user1, user2, dif_ls, level_ls, music, EX_flg, Score_Count=None, timeout=None):
        self.channel = channel
        self.player = [user1, user2]
        self.ok_click = []
        self.reroll_click = []
        self.dif_ls = dif_ls
        self.level_ls = level_ls
        self.music = music
        self.EX_flg = EX_flg
        self.Score_Count = Score_Count
        self.timeout_flg = True
        super().__init__(timeout=timeout)

    @ui.button(label="OK!!", style=discord.ButtonStyle.success)
    async def ok(self, button: discord.ui.Button, interaction: discord.Interaction):
        """決定"""
        #対戦者かチェック
        flg = await self.check(button.user.id)
        if flg:
            #同じプレイヤーが再び押していないか
            if button.user.id in self.ok_click:
                await button.response.send_message("もう押してるよ！", ephemeral=True)
            else:
                #ボタンをクリックした人を追加
                self.ok_click.append(button.user.id)
                #二人ともがボタンを押したら対戦を行う
                if len(self.ok_click) == 2:
                    #タイムアウト処理を無効化
                    self.timeout_flg = False
                    #ボタンを決定メッセージで上書き
                    await button.response.edit_message(content="対戦が開始されます", view=None)
                    #対戦開始をアナウンス
                    await button.followup.send(f"{button.user.display_name}さんがOKを押したよ！\n対戦スタート！！")
                    #対戦へ
                    await Arcaea_command.s_sb_battle(button, self.player[0], self.player[1], self.dif_ls, self.level_ls, self.music, self.EX_flg, self.Score_Count)
                else:
                    await button.response.send_message(f"{button.user.display_name}さんがOKを押したよ！")
        else:
            await button.response.send_message("きみは対戦者じゃないよ", ephemeral=True)

    @ui.button(label="引き直し", style=discord.ButtonStyle.blurple)
    async def exscore(self, button: discord.ui.Button, interaction: discord.Interaction):
        """引き直し"""
        #対戦者かチェック
        flg = await self.check(button.user.id)
        if flg:
            #同じプレイヤーが再び押していないか
            if button.user.id in self.reroll_click:
                await button.response.send_message("もう押してるよ！", ephemeral=True)
            else:
                #ボタンをクリックした人を追加
                self.reroll_click.append(button.user.id)
                #二人ともがボタンを押したら引き直しを行う
                if len(self.reroll_click) == 2:
                    #タイムアウト処理を無効化
                    self.timeout_flg = False
                    #ボタンを決定メッセージで上書き
                    await button.response.edit_message(content="課題曲の再抽選を実施します", view=None)
                    await button.followup.send(f"{button.user.display_name}さんが引き直しを押したよ\nなにがでるかな～～")
                    #再度抽選を行う
                    await Arcaea_command.s_sb_musicselect(button, self.player[0], self.player[1], self.dif_ls, self.level_ls, self.EX_flg, self.Score_Count)
                else:
                    await button.response.send_message(f"{button.user.display_name}さんが引き直しを押したよ")
        else:
            await button.response.send_message("きみは対戦者じゃないよ", ephemeral=True)

    async def check(self, user):
        """対戦者以外ではないか確認"""
        if user in self.player:
            return True #対戦者
        else:
            return False #それ以外
        
    async def on_timeout(self):
        """タイムアウト処理"""
        try:
            if self.timeout_flg:
                #タイムアウトになったらチャンネルを削除
                await self.channel.delete()
                #対戦ステータスを変更
                await Arcaea_command.state_chenge(self.player[0], False)
                await Arcaea_command.state_chenge(self.player[1], False)
        except discord.HTTPException:
            pass
            
class VSScoreCheck(ui.View):
    """スコア確認ボタン"""
    def __init__(self, user, timeout=None):
        self.user_id = user
        self.check_flg = None
        super().__init__(timeout=timeout)

    @ui.button(label="OK!", style=discord.ButtonStyle.success)
    async def scoreok(self, button: discord.ui.Button, interaction: discord.Interaction):
        if button.user.id == self.user_id:
            self.check_flg = True
            await button.response.edit_message(content="入力を確定したよ!!", view=None)
        else:
            await button.response.send_message("スコア入力者じゃないよ", ephemeral=True)

    @ui.button(label="入力しなおす", style=discord.ButtonStyle.gray)
    async def reinput(self, button: discord.ui.Button, interaction: discord.Interaction):
        if button.user.id == self.user_id:
            self.check_flg = False
            await button.response.edit_message(content="スコアを入力し直してね", view=None)
        else:
            await button.response.send_message("スコア入力者じゃないよ", ephemeral=True)