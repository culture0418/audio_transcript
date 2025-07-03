from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
from db import DB
from transcript import AudioTranscription
import os
from werkzeug.utils import secure_filename
import threading
import uuid
import io
from docx import Document

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 全域進度字典
progress_dict = {}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success': False, 'error': '請提供帳號和密碼'})
    try:
        if username != "kslab":
            return jsonify({'success': False, 'error': '帳號錯誤'})
        elif password != "kslab":
            return jsonify({'success': False, 'error': '密碼錯誤'})
        else:
            return jsonify({'success': True})
    finally:
        pass


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
    task_id = str(uuid.uuid4())
    progress_dict[task_id] = 0
    def run_transcribe():
        try:
            transcriber = AudioTranscription(model_size=model_size, language=language)
            def progress_cb(percent):
                progress_dict[task_id] = percent
            result = transcriber.transcribe_with_progress(file_path, progress_callback=progress_cb)
            progress_dict[task_id] = 100
            progress_dict[task_id+'_result'] = result
        except Exception as e:
            progress_dict[task_id] = -1
            progress_dict[task_id+'_error'] = str(e)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    threading.Thread(target=run_transcribe).start()
    return jsonify({'success': True, 'task_id': task_id})

# 查詢進度 API
@app.route('/api/progress/<task_id>')
def progress(task_id):
    percent = progress_dict.get(task_id, 0)
    if percent == 100:
        result = progress_dict.get(task_id+'_result', '')
        return jsonify({'progress': 100, 'done': True, 'result': result})
    elif percent == -1:
        error = progress_dict.get(task_id+'_error', '未知錯誤')
        return jsonify({'progress': 0, 'done': True, 'error': error})
    else:
        return jsonify({'progress': percent, 'done': False})

# 轉錄結果下載（可選）
@app.route('/api/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 靜態檔案服務首頁
@app.route('/')
def root():
    print('Serving index.html from templates')
    return render_template('index.html')

@app.route('/api/generate_docx', methods=['POST'])
def generate_docx():
    data = request.json
    text = data.get('text', '')
    if not text.strip():
        return jsonify({'success': False, 'error': '沒有內容'}), 400
    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document', as_attachment=True, download_name='transcription.docx')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
