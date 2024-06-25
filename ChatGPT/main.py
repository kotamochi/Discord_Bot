import os
import dotenv
import discord
import ChatBot


#ユーザー登録変数の読み込み
dotenv.load_dotenv()
#アクセストークンを取得
TOKEN = os.environ["BOT_TOKEN"]
GPT_TOKEN = os.environ["CHAT_GPT_TOKEN"]
#接続に必要なオブジェクトを生成
client = discord.Client(intents=discord.Intents.all())
chatgpt = ChatBot.Chat_GPT(GPT_TOKEN)

@client.event
async def on_ready():
    """bot起動時処理"""
    print("起動しました。")
    

@client.event
async def on_message(message):
    """メッセージを受け取る"""
    try:
        #Botの発言は飛ばす
        if message.author.bot:
            return
        elif message.content == "履歴を削除":
            chatgpt.chatbot_delete_log()
            return await message.channel.send("会話履歴をリセットしました。")
        else:
            #GPTにメッセージを送信して結果を表示
            respons = await chatgpt.chatbot_response(message)
            return await message.channel.send(respons)

    #エラー処理
    except Exception:
        return await message.channel.send("予期せぬエラーが発生しました。もう一度お試しください。", delete_after=10)


try:
    client.run(TOKEN)
except Exception as e:
    print(e)
    print("botがエラーにより終了しました。")