import dotenv
from openai import OpenAI


class Chat_GPT():
    def __init__(self, chatbot_api, prompt_path=None):
        """初期設定"""
        #ユーザー登録変数の読み込み
        dotenv.load_dotenv()
        #CAHT_GPTのオブジェクトを作成
        self.gpt_client = OpenAI(api_key=chatbot_api)
        self.prompt_path = prompt_path
        #プロンプトを取得
        if prompt_path is None:
            #履歴保存用
            self.messagelist = []
        else:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
            #プロンプトを入力した履歴保存用Listを作成
            self.messagelist=[{"role": "system", "content": prompt}]


    async def chatbot_response(self, message):
        """Chat-GPTにメッセージを入力してレスポンスを返す"""
        #入力メッセージを追加
        try:
            text = message.content
        except AttributeError:
            #テキストが直接渡された時
            text = message
        self.messagelist.append({"role": "user", "content": text})
        #メッセージをChatGPTに入力
        response = self.gpt_client.chat.completions.create(model = "gpt-4-turbo", messages=self.messagelist)

        #返答を取得
        response_text = response.choices[0].message.content
        #会話記録を保持
        self.messagelist.append({"role": "assistant", "content": response_text})

        return response_text
    
    
    async def chatbot_delete_log(self):
        """保持している会話記録をクリアする"""
        #プロンプトを取得
        if self.prompt_path is None:
            #履歴Listを再作成
            self.messagelist = []
        else:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
            #プロンプトを入力して履歴Listを再作成
            self.messagelist=[{"role": "system", "content": prompt}]