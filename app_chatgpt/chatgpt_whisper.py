# 添加对上一级目录import的支持
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Python_User_Logger import *

import openai

from pydub import AudioSegment

def main():
    openai.api_key = "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"   # openai账号：采用微软账号(jack.seaver@outlook.com)，plus 20美元/月、token费用另算。

    # 截取1分钟的音频
    # song = AudioSegment.from_mp3("my.m4a")
    # PyDub handles time in milliseconds
    # one_minute = 1 * 60 * 1000
    # first_1_minute = song[:one_minute]
    # first_1_minute.export("my_1_minute.m4a", format="m4a")

    # audio_file= open("my_1_minute.m4a", "rb")
    audio_file1= open("my.m4a", "rb")
    audio_file2= open("my.m4a", "rb")

    # audio --> 该国语言
    transcript1 = openai.Audio.transcribe("whisper-1", audio_file1)


    # audio --> 英语
    transcript2 = openai.Audio.translate("whisper-1", audio_file2)

    # 回复的内容格式
    # {
    #   "text": "Imagine the wildest idea that you've ever had, and you're curious about how it might scale to something that's a 100, a 1,000 times bigger.
    # ....
    # }

    print("transcript1 is : {}".format(transcript1))
    print("transcript2 is : {}".format(transcript2))

if __name__ == "__main__" :
    main()