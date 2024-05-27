import discord
from discord import ui
import Arcaea_command
import asyncio


class VSButton(ui.View):
    """対戦システムの選択ボタン"""
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)
    
    @ui.button(label="スコアバトル(1vs1)", style=discord.ButtonStyle.success)
    async def score(self, button: discord.ui.Button, interaction: discord.Interaction):
        """1vs1"""
        await Arcaea_command.match_host(button, button.user.id, "0")

    @ui.button(label="EXスコアバトル(1vs1)", style=discord.ButtonStyle.blurple)
    async def exscore(self, button: discord.ui.Button, interaction: discord.Interaction):
        """1vs1(EXScore)"""
        await Arcaea_command.match_host(button, button.user.id, "1")

    #@ui.button(label="ScoreBattle 2vs2", style=discord.ButtonStyle.blurple)
    #async def score2(self, button: discord.ui.Button, interaction: discord.Interaction):
    #    """2vs2"""
    #    await Arcaea_command.match_host(button, button.user.id, "2")


class VSHostButton(ui.View):
    """対戦募集ボタン"""
    def __init__(self, user, kind, timeout=180):
        self.host = user
        self.kind = kind
        super().__init__(timeout=timeout)

    @ui.button(label="参加する", style=discord.ButtonStyle.success)
    async def vsstart(self, button: discord.ui.Button, interaction: discord.Interaction):
        guest = button.user.id
        await Arcaea_command.Arcaea_ScoreBattle(button, self.host, guest, self.kind)

    @ui.button(label="取り消し(ホストのみ可)", style=discord.ButtonStyle.gray)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.host == button.user.id:
            #募集を取り消し
            await button.message.delete()
            #対戦フラグを消す
            await Arcaea_command.state_chenge(button.user.id, False)
            await button.response.send_message("募集を取り消しました。", ephemeral=True)
        else:
            await button.response.send_message("あなたはこの募集のホストではありません。", ephemeral=True)


class VSStopbutton(ui.View):
    """対戦を途中終了する"""
    def __init__(self, user1, user2, timeout=180):
        self.player = [user1, user2]
        self.click = []
        self.vsstop = False
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
                    #ボタンを無効化
                    self.disabled = True
                    await button.response.edit_message(view=self)
                    await button.followup.send(f"{button.user.display_name}が終了を選択しました。\n対戦を終了します。")
                    self.vsstop = True #終了フラグを立てる
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


class VSMusicButton(ui.View):
    """課題曲選択ボタン"""
    def __init__(self, user1, user2, timeout=180):
        self.player = [user1, user2]
        self.ok_click = []
        self.reroll_click = []
        self.start = False #対戦を初めていいか
        self.reroll = False
        super().__init__(timeout=timeout)

    @ui.button(label="OK!!", style=discord.ButtonStyle.success)
    async def ok(self, button: discord.ui.Button, interaction: discord.Interaction):
        """決定"""
        #対戦者かチェック
        flg = await self.check(button.user.id)
        if flg:
            #同じプレイヤーが再び押していないか
            if button.user.id in self.ok_click:
                await button.response.send_message("すでに押しています。", ephemeral=True)
            else:
                #ボタンをクリックした人を追加
                self.ok_click.append(button.user.id)
                #二人ともがボタンを押したら対戦を行う
                if len(self.ok_click) == 2:
                    #ボタンを無効化
                    self.children[0].disabled, self.children[1].disabled = True, True
                    await button.response.edit_message(view=self)
                    #対戦開始をアナウンス
                    await button.followup.send(f"{button.user.display_name}が決定を選択しました。\n対戦を開始してください。")
                    self.start = True #対戦フラグを立てる
                else:
                    await button.response.send_message(f"{button.user.display_name}が決定を選択しました。")
        else:
            await button.response.send_message("あなたは対戦者ではありません。", ephemeral=True)

    @ui.button(label="引き直し", style=discord.ButtonStyle.blurple)
    async def exscore(self, button: discord.ui.Button, interaction: discord.Interaction):
        """引き直し"""
        #対戦者かチェック
        flg = await self.check(button.user.id)
        if flg:
            #同じプレイヤーが再び押していないか
            if button.user.id in self.reroll_click:
                await button.response.send_message("すでに押しています。", ephemeral=True)
            else:
                #ボタンをクリックした人を追加
                self.reroll_click.append(button.user.id)
                #二人ともがボタンを押したら引き直しを行う
                if len(self.reroll_click) == 2:
                    #ボタンを無効化
                    self.children[0].disabled, self.children[1].disabled = True, True
                    await button.response.edit_message(view=self)
                    await button.followup.send(f"{button.user.display_name}が引き直しを選択しました。\n課題曲を再抽選します。")
                    self.reroll = True #引き直しフラグを立てる
                else:
                    await button.response.send_message(f"{button.user.display_name}が引き直しを選択しました。")
        else:
            await button.response.send_message("あなたは対戦者ではありません。", ephemeral=True)


    async def check(self, user):
        """対戦者以外ではないか確認"""
        if user in self.player:
            return True #対戦者
        else:
            return False #それ以外