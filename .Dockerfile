# استخدم نسخة Python 3.11
FROM python:3.11-slim

# اجعل مجلد العمل هو /app
WORKDIR /app

# انسخ كل الملفات إلى الحاوية
COPY . .

# ثبّت التبعيات
RUN pip install --no-cache-dir -r requirements.txt

# شغّل السيرفر
CMD ["python", "api_server.py"]
