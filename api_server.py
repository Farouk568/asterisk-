# api_server.py

import os
import time
import json
import pysrt
import concurrent.futures
import uuid
import requests
from pydub import AudioSegment
from gradio_client import Client
from flask import Flask, request, jsonify, send_from_directory, url_for

# ✨✨✨== التعديل الأول: إصلاح مشكلة الطباعة باللغة العربية في طرفية ويندوز ==✨✨✨
import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# =========================================================================

# ================= إعداد التطبيق والخادم =================
app = Flask(__name__)
OUTPUT_DIR = "output_audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================= إعداد عميل توليد الصوت =================
tts_client = None
try:
    tts_client = Client("NihalGazi/Text-To-Speech-Unlimited")
    print("✅ تم الاتصال بخدمة Text-To-Speech بنجاح.")
except Exception as e:
    print(f"❌ فشل الاتصال بخدمة Text-To-Speech: {e}")

male_voices = ["dan", "onyx", "verse", "ash", "amuch"]
female_voices = ["nova", "fable", "coral", "shimmer", "ballad"]

# ================= دوال مساعدة =================

def to_milliseconds(srt_time):
    return (srt_time.hours * 3600 + srt_time.minutes * 60 + srt_time.seconds) * 1000 + srt_time.milliseconds

def tts_line(text, voice_name, out_path, emotion="neutral", retries=5):
    if not tts_client:
        raise ConnectionError("عميل TTS غير متاح.")
    for attempt in range(1, retries + 1):
        try:
            print(f"🎙️ [{voice_name}] توليد صوت... (محاولة {attempt}/{retries})")
            audio_path, _ = tts_client.predict(prompt=text, voice=voice_name, emotion=emotion, api_name="/text_to_speech_app")
            
            # ✨✨✨== التعديل الثاني: التحقق من أن الـ API أعاد ملفًا صالحًا ==✨✨✨
            if not audio_path:
                raise Exception("فشل الـ API في إنشاء ملف صوتي، أعاد قيمة None.")
            # ====================================================================

            os.rename(audio_path, out_path)
            print(f"✅ [{voice_name}] تم إنشاء الصوت: {os.path.basename(out_path)}")
            return compress_mp3(out_path, bitrate="64k")
        except Exception as e:
            print(f"⚠️ خطأ في المحاولة {attempt} للصوت [{voice_name}]: {e}")
            if "503" in str(e): time.sleep(10 * attempt)
            else: time.sleep(3)
    print(f"❌ فشل توليد الصوت بعد {retries} محاولات: {text[:30]}...")
    return None

def compress_mp3(file_path, bitrate="128k"):
    try:
        audio = AudioSegment.from_file(file_path)
        audio.export(file_path, format="mp3", bitrate=bitrate)
        print(f"💾 تم ضغط الملف إلى {bitrate}: {os.path.basename(file_path)}")
        return file_path
    except Exception as e:
        print(f"⚠️ فشل ضغط الملف {file_path}: {e}")
        return file_path

def process_line(i, sub, voice_name, job_dir):
    try:
        out_file = os.path.join(job_dir, f"line_{i+1}.mp3")
        if result_path := tts_line(sub.text, voice_name, out_file):
            start_ms = to_milliseconds(sub.start)
            end_ms = to_milliseconds(sub.end)
            print(f"✅ [{voice_name}] {sub.text.replace(chr(10), ' ')} ({sub.start} → {sub.end})")
            return {"file_path": result_path, "start_ms": start_ms, "end_ms": end_ms, "text": sub.text}
    except Exception as e:
        print(f"❌ خطأ في السطر {i+1}: {e}")
    return None

# ================= نقاط النهاية (API Endpoints) =================

@app.route('/generate-audio', methods=['GET'])
def generate_audio_endpoint():
    srt_url = request.args.get('url')
    if not srt_url:
        return jsonify({"error": "الرجاء توفير 'url' كمعامل في الرابط. مثال: ?url=https://..."}), 400

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(OUTPUT_DIR, job_id)
    os.makedirs(job_dir)
    print(f"\n🎬 بدء مهمة جديدة: {job_id}")

    try:
        print(f"📥 تحميل الترجمة من: {srt_url}")
        response = requests.get(srt_url, timeout=20)
        response.raise_for_status()
        subs = pysrt.from_string(response.text)
    except Exception as e:
        return jsonify({"error": f"فشل تحميل أو قراءة ملف الترجمة: {e}"}), 500

    voice_cycle = [male_voices[i % len(male_voices)] if i % 2 == 0 else female_voices[i % len(female_voices)] for i in range(len(subs))]
    
    print(f"🚀 بدء العمل بالتوازي (حتى 8 عمال)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_line, i, sub, voice_cycle[i], job_dir): i for i, sub in enumerate(subs)}
        future_results = [None] * len(subs)
        for future in concurrent.futures.as_completed(futures):
            future_results[futures[future]] = future.result()

    final_response = []
    for result in filter(None, future_results):
        filename = os.path.basename(result["file_path"])
        audio_url = url_for('serve_audio', job_id=job_id, filename=filename, _external=True)
        final_response.append({"audio_url": audio_url, "start_ms": result["start_ms"], "end_ms": result["end_ms"], "text": result["text"]})

    print(f"\n✅ اكتملت المهمة {job_id}. تم توليد {len(final_response)} مقطعًا صوتيًا.")
    return jsonify(final_response)

@app.route('/audio/<job_id>/<filename>')
def serve_audio(job_id, filename):
    return send_from_directory(os.path.join(OUTPUT_DIR, job_id), filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
