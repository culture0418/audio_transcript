import whisper

class AudioTranscription:
    def __init__(self, model_size: str = "base", language: str = "en"):
        self.model_size = model_size
        self.language = language
        self.model = whisper.load_model(model_size)

    def transcribe_with_progress(self, audio_path: str) -> str:
        """
        讀取音訊檔案（支援 .wav, .mp3, .m4a 等格式）並使用 Whisper 進行轉錄，顯示進度條。
        參數：
        - audio_path: 音訊檔案路徑，例如 "audio.wav" 或 "audio.mp3"
        回傳：
        - 完整的轉錄文字
        """
        result = self.model.transcribe(audio_path, language=self.language, verbose=True)
        return result["text"].strip()

# test code
# if __name__ == "__main__":
#     audio_file = "test.wav"  # 請替換成你的音訊檔案名稱（支援 .wav, .mp3 等）
#     transcriber = AudioTranscription(model_size="base", language="en")
#     transcript = transcriber.transcribe_with_progress(audio_file)
#     print("轉錄結果：")
#     print(transcript)
