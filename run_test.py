# run_test.py

import requests
import json
from urllib.parse import quote_plus

# --- يمكنك تغيير هذا الرابط ---
# الرابط الذي يحتوي على أحرف خاصة ويتسبب بالمشاكل
srt_url_original = "https://cacdn.hakunaymatata.com/subtitle/db91eab723581eaa443391f61b58164c.srt?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jYWNkbi5oYWt1bmF5bWF0YXRhLmNvbS9zdWJ0aXRsZS8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzYwNTM5NjA2fX19XX0_&Signature=LQMOmx7JTZL6GKnIDxysio5Yz2kfwq3kearPRic0zvgaTdHSdTs6HosUkNUL0wkNwr3SAQ7wvnCFtkImYMrtZywlW7p66tXZM86iau2O0HWpVg8QjiFhaZc24~MxGQOc7JvK7nCzgcx3sfPkDlvQd3r0l7G0IQ2Yn2~~EsnJi8zQMrUbG2nI7VCyW-dsAzRuH~CkKu7A43ZZZ0J2AWb2bE-yS7nQIvTu345FDjFAdDV~AMD4EfADnGvxUU2Lsmnpqu4yLPVVTtQH2jgzb2SkDc7tYe1Sp~lH-nzXI7uRdJN0bbT7hztZhLq48SdMxn8a1STkghAnGmqeKj7Nlpc6Vw__&Key-Pair-Id=KMHN1LQ1HEUPL" # (أكمل الرابط)
# رابط بسيط للتجربة السريعة
srt_url_simple = "https://cacdn.hakunaymatata.com/subtitle/db91eab723581eaa443391f61b58164c.srt?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jYWNkbi5oYWt1bmF5bWF0YXRhLmNvbS9zdWJ0aXRsZS8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzYwNTM5NjA2fX19XX0_&Signature=LQMOmx7JTZL6GKnIDxysio5Yz2kfwq3kearPRic0zvgaTdHSdTs6HosUkNUL0wkNwr3SAQ7wvnCFtkImYMrtZywlW7p66tXZM86iau2O0HWpVg8QjiFhaZc24~MxGQOc7JvK7nCzgcx3sfPkDlvQd3r0l7G0IQ2Yn2~~EsnJi8zQMrUbG2nI7VCyW-dsAzRuH~CkKu7A43ZZZ0J2AWb2bE-yS7nQIvTu345FDjFAdDV~AMD4EfADnGvxUU2Lsmnpqu4yLPVVTtQH2jgzb2SkDc7tYe1Sp~lH-nzXI7uRdJN0bbT7hztZhLq48SdMxn8a1STkghAnGmqeKj7Nlpc6Vw__&Key-Pair-Id=KMHN1LQ1HEUPL"
# -----------------------------

# اختر الرابط الذي تريد تجربته
target_srt_url = srt_url_simple 

# الحل لمشكلة الرموز الخاصة: نقوم بترميز الرابط قبل إرساله
encoded_srt_url = quote_plus(target_srt_url)

# بناء رابط الـ API الكامل
api_endpoint = f"http://127.0.0.1:5000/generate-audio?url={encoded_srt_url}"

print(f"🚀 إرسال طلب إلى:\n{api_endpoint}\n")

try:
    response = requests.get(api_endpoint, timeout=None) # Timeout=None يعني الانتظار للأبد
    
    print(f"🔢 كود الحالة: {response.status_code}")

    if response.status_code == 200:
        print("✅ نجح الطلب! النتائج:")
        # طباعة النتائج بشكل جميل
        pretty_json = json.dumps(response.json(), indent=2, ensure_ascii=False)
        print(pretty_json)
    else:
        print("❌ فشل الطلب! رسالة الخطأ من الخادم:")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"❌ لا يمكن الاتصال بالخادم. هل قمت بتشغيل api_server.py؟")
    print(f"Error: {e}")