# ✅ استخدم Python 3.11 بدل 3.13
FROM python:3.11-slim

# تثبيت ffmpeg و git
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

# تعيين مجلد العمل
WORKDIR /app

# نسخ الملفات
COPY . .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# تعيين الأمر الافتراضي لتشغيل السيرفر
CMD ["gunicorn", "api_server:app", "--timeout", "120", "--workers", "2"]
