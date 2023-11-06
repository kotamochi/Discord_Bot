import requests
import json
import wave
import asyncio
from discord.player import FFmpegPCMAudio

class VoiceBox():
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 50021
        self.botid = 1143179888984064130
        self.sepeker_id = 3 #初期値はずんだもん
    
    
    #音声変換を呼び出す設定
    async def CreateQuery(self, message):
        if message.author.id == 665896865627111425:
            params = (('text', message.content),
                      ('speaker', 26))
        else:
            params = (('text', message.content),
                      ('speaker', self.sepeker_id))
        query = requests.post(f'http://{self.host}:{self.port}/audio_query',
                              params=params)

        return query, params
    
    
    #音声合成を実施
    async def Get_ReadingAudio(self, query, params):
        synthesis = requests.post(f'http://{self.host}:{self.port}/synthesis',
                                  headers = {"Content-Type": "application/json"},
                                  params = params,
                                  data = json.dumps(query.json())
                                  )
    
        #wavファイルに音声データを保存
        voice = wave.open(r"Voice\textread.wav", 'w')
        voice.setnchannels(1)
        voice.setsampwidth(2)
        voice.setframerate(24000)
        voice.writeframes(synthesis.content)
        voice.close()
    
    
    #読み上げbotの実行部分
    async def ReadingText(self, message, voice_client):
        #テキストを音声作成のクエリにする
        query, params = await self.CreateQuery(message)
        
        #合成音声を作成
        await self.Get_ReadingAudio(query, params)
        
        #前の文章が読み終わっていることを確認して読み上げる
        while True:
            if not voice_client.is_playing():
                audio = FFmpegPCMAudio(r"Voice\textread.wav")
                message.guild.voice_client.play(audio) #読み上げ
                #確認処理を抜ける
                break
                #0.3秒待って再度確認
            else:
                await asyncio.sleep(0.3)