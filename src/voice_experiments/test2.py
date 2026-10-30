from google.cloud import texttospeech

def create_result3_audio():
    # 구글 클라이언트를 생성합니다.
    client = texttospeech.TextToSpeechClient()

    # TTS로 변환할 텍스트를 설정합니다.
    text = "숫자로 말해주세요."

    # TTS 요청을 만듭니다.
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR", name="ko-KR-Wavenet-D", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # TTS API를 호출하여 음성을 생성합니다.
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # 생성된 음성을 파일로 저장합니다.
    with open("result3.wav", "wb") as out:
        out.write(response.audio_content)

# 음성 파일 생성 함수를 호출합니다.
create_result3_audio()
