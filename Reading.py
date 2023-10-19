import requests
import json
import wave
import discord
from discord.channel import VoiceChannel
from discord.player import FFmpegPCMAudio

class VoiceBox():
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 50021
        self.botid = 1143179888984064130
        self.sepeker_id = 3 #初期値はずんだもん
    
    
    #音声変換を呼び出す設定
    async def CreateQuery(self, message):
        params = (('text', message),
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
    async def ReadingText(self, message):
        #テキストを音声作成のクエリにする
        query, params = await self.CreateQuery(message)
        
        #合成音声を作成
        await self.Get_ReadingAudio(query, params)
        
        #読み上げる
        audio = FFmpegPCMAudio(r"Voice\textread.wav")
        message.voice_client.play(audio)