from flask import Flask, request, jsonify, send_from_directory
from db import DB
from transcript import AudioTranscription
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 登入 API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    db = DB()
    try:
        db.connect()
        cursor = db.execute("SELECT password FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        if row and row[0] == password:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '帳號或密碼錯誤'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        db.close()

# 音訊檔案上傳與轉錄 API
@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '未收到檔案'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '未選擇檔案'})
    model_size = request.form.get('model', 'base')
    language = request.form.get('language', 'en')
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    try:
        transcriber = AudioTranscription(model_size=model_size, language=language)
        result = transcriber.transcribe_with_progress(file_path)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# 轉錄結果下載（可選）
@app.route('/api/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 靜態檔案服務首頁
@app.route('/')
def root():
    print('Serving index.html from', app.static_folder)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
