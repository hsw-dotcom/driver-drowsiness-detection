from gtts import gTTS #pip install gTTs
import playsound #pip install playsound
#language code : http://www.lingoes.net/en/translator/langcode.htm

def speak_ko():
    txt = "33 더하기 55 는 몇인가요?"
    tts_kr = gTTS(text=txt, lang='ko', slow=False)
    tts_kr.save("voice.mp3")
    playsound.playsound("voice.mp3")

if __name__ == "__main__":
    speak_ko()