import discord
from discord import ui
import random

#ボタンお試し
class SampleButton(ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)
    
    @ui.button(label="JOIN NOW!", style=discord.ButtonStyle.success)
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
        view = SampleSelect(timeout=None)
        await button.response.send_message(view=view, ephemeral=True)

    #@ui.button(label="NG", style=discord.ButtonStyle.gray)
    #async def ng(self, button: discord.ui.Button, interaction: discord.Interaction):
    #    await button.response.send_message(f"{button.user.mention} NG")
        
class SampleSelect(ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)

    @ui.select(
        cls=discord.ui.Select,
        placeholder="あなたのポテンシャル区分を選択してください",
        options=[
            discord.SelectOption(label="~~9.99"),
            discord.SelectOption(label="10.00~10.49"),
            discord.SelectOption(label="10.50~10.99"),
            discord.SelectOption(label="11.00~11.49"),
            discord.SelectOption(label="11.50~11.99"),
            discord.SelectOption(label="12.00~12.49"),
            discord.SelectOption(label="12.50~12.89"),
            discord.SelectOption(label="12.90~~"),
        ],
    )
    async def selectlist(self, interaction: discord.Interaction, select: discord.ui.Select):
        select.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"参加申請完了。あなたの区分は{select.values[0]}", ephemeral=True)