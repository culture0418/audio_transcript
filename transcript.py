import whisper
import time
import os

class AudioTranscription:
    def __init__(self, model_size: str = "base", language: str = "en"):
        self.model_size = model_size
        self.language = language
        self.model = whisper.load_model(model_size)

    def transcribe_with_progress(self, audio_path: str, progress_callback=None) -> str:
        # 模擬進度條到 70%
        total_steps = 10
        for i in range(total_steps):
            time.sleep(3)  # 可依實際情況調整
            if progress_callback:
                progress_callback(int((i+1)/total_steps*70))
        # 實際轉錄
        result = self.model.transcribe(audio_path, language=self.language, verbose=True)
        if progress_callback:
            progress_callback(100)
        return result["text"].strip()

# test code
# if __name__ == "__main__":
#     audio_file = "test.wav"  # 請替換成你的音訊檔案名稱（支援 .wav, .mp3 等）
#     transcriber = AudioTranscription(model_size="base", language="en")
#     transcript = transcriber.transcribe_with_progress(audio_file)
#     print("轉錄結果：")
#     print(transcript)
